<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/verbs.c

## Purpose
This file is a central RDMA/InfiniBand core verbs implementation. It wraps provider driver operations with common validation, reference counting, resource tracking, security hooks, GID/GRH ownership rules, RoCE address resolution, QP state-machine checks, CQ/MR/multicast/XRC/WQ helpers, drain helpers, RDMA netdev allocation, and hardware stats allocation.

## Important APIs, Types, And Functions
- Message helpers: `ib_event_msg()`, `ib_wc_status_msg()`, `ib_rate_to_mult()`, `mult_to_ib_rate()`, `ib_rate_to_mbps()`, and `ib_port_attr_to_speed_info()` translate enums and port attributes into stable strings or numeric rates.
- Transport helpers: `rdma_node_get_transport()`, `rdma_port_get_link_layer()`, `ib_get_eth_speed()`, `ib_get_rdma_header_version()`, and `ib_get_gids_from_rdma_hdr()` classify RDMA devices, ports, and packet headers.
- Protection-domain lifecycle: `__ib_alloc_pd()` allocates a driver PD, optionally creates an internal DMA MR, and registers restrack state; `ib_dealloc_pd_user()` releases the internal MR, calls provider deallocation, removes restrack, and frees memory.
- Address-handle lifecycle: `rdma_copy_ah_attr()`, `rdma_replace_ah_attr()`, `rdma_move_ah_attr()`, `rdma_destroy_ah_attr()`, `rdma_create_ah()`, `rdma_create_user_ah()`, `ib_create_ah_from_wc()`, `rdma_modify_ah()`, `rdma_query_ah()`, and `rdma_destroy_ah_user()` manage AH objects and SGID attribute references.
- RoCE address path: `rdma_fill_sgid_attr()`, `rdma_unfill_sgid_attr()`, `rdma_update_sgid_attr()`, `ib_resolve_unicast_gid_dmac()`, and `ib_resolve_eth_dmac()` ensure GRH SGID attributes and destination MACs are available before provider calls.
- SRQ/QP/CQ/MR lifecycle: `ib_create_srq_user()`, `ib_destroy_srq_user()`, `create_qp()`, `ib_create_qp_user()`, `ib_create_qp_kernel()`, `ib_destroy_qp_user()`, `__ib_create_cq()`, `ib_destroy_cq_user()`, `ib_reg_user_mr()`, `ib_alloc_mr()`, `ib_alloc_mr_integrity()`, and `ib_dereg_mr_user()` allocate core objects, call `ib_device->ops`, and maintain use counts and restrack entries.
- QP state rules: `qp_state_table` and `ib_modify_qp_is_ok()` encode required and optional attribute masks for transitions between RESET, INIT, RTR, RTS, SQD, SQE, and ERR.
- QP mutation and sharing: `_ib_modify_qp()`, `ib_modify_qp_with_udata()`, `ib_modify_qp()`, `ib_query_qp()`, `ib_open_qp()`, `ib_close_qp()`, and `__ib_destroy_shared_qp()` handle real/shared QPs, XRC target lookup, security hooks, counter binding, and SGID/LAG updates.
- Other exported helpers: multicast attach/detach, XRC domain allocation, WQ lifecycle, VF management wrappers, MR SG mapping, queue drain, RDMA netdev allocation/initialization, and `rdma_alloc_hw_stats_struct()` / `rdma_free_hw_stats_struct()`.

## Control Flow
Most public functions follow a common pattern: validate core invariants and provider capability, allocate or initialize the core object, call the provider operation in `device->ops`, then add resource tracking and increment dependent object use counts only after success. Destroy paths reject busy objects, call the provider destroy/dealloc operation, drop dependent references, delete restrack entries, release SGID or umem resources, and free memory.

AH creation first validates the port and GRH requirements, fills or verifies the SGID attribute, optionally resolves RoCE destination MACs or LAG transmit slave netdevices, calls the provider create method, then unwinds the temporary SGID fill so the caller's input attribute is not silently mutated. AH/QP modify uses the same SGID-fill pattern and transfers persistent SGID references to object fields only after provider/security modification succeeds.

QP creation builds the core QP object, initializes completion/event routing and MR lists, calls the provider create method, installs security state, and registers restrack. XRC target QPs add a second shared-open object stored in an xarray under `xrcd->tgt_qps`. QP modification is funneled through `_ib_modify_qp()`, which resolves AH data, rejects unsupported alternate paths for RoCE, masks oversized PSNs, auto-binds counters during reset-to-init port assignment, runs `ib_security_modify_qp()`, and then updates cached port and SGID references.

CREATION and teardown of CQ, SRQ, WQ, MR, XRCD, multicast membership, and VF wrappers are thin but important adapters around provider callbacks. Drain helpers move a QP to error and post sentinel WRs or poll SRQ completions so callers can wait until outstanding work is observed by the CQ path.

## State And Persistence
Persistent kernel state includes allocated RDMA core objects, provider-private driver objects embedded via `rdma_zalloc_drv_obj*()`, restrack records, use counters on PD/CQ/SRQ/XRCD/WQ/RWQ objects, SGID attribute references, QP security state, RDMA counter bindings, MR address/length/page size metadata, and optional CQ umem. State is in-memory only and tied to kernel object lifetime; provider hardware state is created and destroyed through `ib_device->ops`.

AH and QP attributes hold SGID references that must be explicitly released. QP shared-open state is persisted in `real_qp->open_list` and, for XRC targets, `xrcd->tgt_qps`. MR mapping helpers update `mr->iova`, `mr->length`, and `mr->page_size` while converting scatterlists to provider page vectors.

## Dependencies And Integration Points
The file depends on Linux networking headers, IPv4/IPv6 helpers, ethtool, security hooks, `rdma/ib_verbs.h`, `rdma/ib_cache.h`, `rdma/ib_addr.h`, `rdma/ib_umem.h`, `rdma/rw.h`, `rdma/lag.h`, core private RDMA helpers, and RDMA tracepoints. Its primary integration contract is `struct ib_device_ops`, with provider drivers supplying alloc/create/modify/query/destroy callbacks. It also integrates with netdevice lifetime through `ib_device_get_netdev()` / `dev_put()`, rtnl locking for ethtool speed, LAG slave selection, RDMA counters, uverbs `ib_udata`, and Linux resource tracking.

## Risks And Edge Cases
Reference ownership is the largest risk: failed paths must undo SGID fills, LAG netdevice references, provider-created resources, restrack entries, use counts, umem, and security state in the exact reverse order. QP alternate-path handling explicitly notes incomplete migration-state tracking. Some provider contracts are assumed, such as kernel CQ creation not setting `cq->umem` and drivers preserving CQ pointers during QP creation. `__ib_create_cq()` leaks the just-allocated CQ if `cq_attr->cqe` is zero because it returns directly after allocation. `ib_get_eth_speed()` calls `dev_put(netdev)` before a warning that may print `netdev->name`, so that diagnostic path depends on a pointer after ref release. Generic drain helpers rely on the caller ensuring CQ/SQ/RQ capacity and no concurrent posting.

## Test Signals
Useful signals are RDMA core build coverage, provider driver module builds, uverbs and kernel-verbs create/modify/destroy tests, RoCE AH/QP tests with IPv4, IPv6, multicast, VLAN, and LAG, QP transition negative tests against `ib_modify_qp_is_ok()`, MR scatterlist mapping boundary tests, XRC shared-QP open/close tests, CQ/SRQ drain behavior, KASAN/KCSAN/leak checking for error paths, and tracepoint or restrack validation showing objects are added and removed exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/Makefile

## Purpose
This Kbuild file selects hardware-provider subdirectories under `drivers/infiniband/hw` according to enabled kernel configuration symbols.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_INFINIBAND_MTHCA) += mthca/` and similar lines map each RDMA provider config option to its subdirectory.
- `obj-$(CONFIG_INFINIBAND_BNG_RE) += bng_re/` integrates the Broadcom next-generation RoCE driver into the hardware-provider build.

## Control Flow
Kbuild evaluates each `obj-*` expression during kernel or module build. If a config symbol is `y`, the subdirectory is built into the kernel; if it is `m`, the subdirectory contributes module objects; if unset, the directory is skipped.

## State And Persistence
The file does not persist runtime state. Its persistent effect is build graph shape: enabled drivers produce built-in objects or modules and disabled drivers are omitted.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system and the nested Makefiles in each provider directory, including `bng_re/Makefile`. It depends on the config symbols exported by provider Kconfig files and top-level RDMA build inclusion.

## Risks And Edge Cases
A wrong symbol or subdirectory name silently prevents a provider from building when configured. The `bng_re` entry must stay synchronized with `hw/bng_re/Kconfig` and the actual directory name. Ordering normally has limited semantic meaning, but duplicate or stale entries can create confusing build output.

## Test Signals
Build with `CONFIG_INFINIBAND_BNG_RE=y` and `=m` to confirm the `bng_re` directory is entered. A full RDMA hardware-provider build should show no missing-directory or unknown-symbol Kbuild errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/Kconfig

## Purpose
Defines the `INFINIBAND_BNG_RE` kernel configuration option for Broadcom next-generation RoCE HCA support.

## Important APIs, Types, And Functions
- `config INFINIBAND_BNG_RE` introduces a tristate option, allowing built-in, module, or disabled builds.
- Prompt: `Broadcom Next generation RoCE HCA support`.
- Dependencies: `64BIT`, `INET`, `DCB`, and `BNGE`.
- Help text documents 50/100/200/400/800 Gb RoCE HCA support and the module name `bng_re`.

## Control Flow
When Kconfig is evaluated, this option is visible only when all dependencies are satisfied. Selecting `y` or `m` drives the parent hardware Makefile to descend into `hw/bng_re/` and the local Makefile to build the driver object.

## State And Persistence
The file persists configuration metadata only. Runtime state is created by the resulting driver module when loaded or built in.

## Dependencies And Integration Points
The option depends on network stack support (`INET`), data center bridging (`DCB`), the Broadcom Ethernet driver symbol `BNGE`, and 64-bit architecture support. It integrates with `drivers/infiniband/hw/Makefile` through `CONFIG_INFINIBAND_BNG_RE`.

## Risks And Edge Cases
The dependency on `BNGE` is critical because `bng_re` calls `bnge_*` auxiliary and firmware messaging APIs and includes BNGE headers. If the dependency symbol name drifts, the RoCE driver may disappear from configuration menus or build without its Ethernet-side provider. The help text and module name must remain aligned with the local Makefile's module target.

## Test Signals
Run Kconfig olddefconfig/menuconfig paths with dependencies enabled and disabled to confirm visibility. Build `CONFIG_INFINIBAND_BNG_RE=m` and verify a `bng_re` module is produced only when `BNGE` and networking dependencies are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/Makefile

## Purpose
Builds the Broadcom `bng_re` RoCE provider module and points the compiler at the sibling Broadcom Ethernet driver headers.

## Important APIs, Types, And Functions
- `ccflags-y := -I $(srctree)/drivers/net/ethernet/broadcom/bnge` adds the BNGE include directory needed for `bnge.h`, `bnge_auxr.h`, `bnge_hwrm.h`, and related interfaces.
- `obj-$(CONFIG_INFINIBAND_BNG_RE) += bng_re.o` declares the module or built-in aggregate object.
- `bng_re-y := bng_dev.o bng_fw.o bng_res.o bng_sp.o bng_debugfs.o` lists the component objects linked into `bng_re.o`.

## Control Flow
Kbuild enters this directory when the parent Makefile sees `CONFIG_INFINIBAND_BNG_RE`. It compiles the listed source files, links them into the composite `bng_re.o`, and emits either a module or built-in object depending on config.

## State And Persistence
No runtime state exists in this file. Its persisted state is the driver object composition and include path used at build time.

## Dependencies And Integration Points
The file integrates `bng_dev.c`, `bng_fw.c`, `bng_res.c`, `bng_sp.c`, and `bng_debugfs.c`. It depends on the BNGE Ethernet driver source tree for shared headers and firmware/HWRM contracts.

## Risks And Edge Cases
Omitting `bng_sp.o` or other objects would create unresolved symbols such as `bng_re_get_dev_attr()`. The broad include path couples the RDMA provider to the Ethernet driver's in-tree layout; moving BNGE headers requires updating this Makefile.

## Test Signals
`make M=drivers/infiniband/hw/bng_re` or full kernel/module builds should compile all five component objects and link `bng_re.o` without missing includes or unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.c

## Purpose
Provides minimal debugfs registration for the Broadcom `bng_re` RoCE driver, creating a driver root and one directory per PCI device.

## Important APIs, Types, And Functions
- `static struct dentry *bng_re_debugfs_root` stores the root debugfs dentry for the module.
- `bng_re_register_debugfs()` creates `/sys/kernel/debug/bng_re`.
- `bng_re_unregister_debugfs()` removes the root dentry.
- `bng_re_debugfs_add_pdev()` creates a child directory named from `dev_name(&pdev->dev)` using `rdev->aux_dev->pdev`.
- `bng_re_debugfs_rem_pdev()` recursively removes the device-specific directory and clears `rdev->dbg_root`.

## Control Flow
Module init calls `bng_re_register_debugfs()` before auxiliary driver registration. Device initialization calls `bng_re_debugfs_add_pdev()` after the firmware channel and stats setup have progressed. Device uninitialization calls `bng_re_debugfs_rem_pdev()`, and module exit removes the global root after unregistering the auxiliary driver.

## State And Persistence
State is in-memory debugfs dentries only. `bng_re_debugfs_root` persists for module lifetime, and `rdev->dbg_root` persists for a probed device lifetime. No files or counters are created under the directories in this implementation.

## Dependencies And Integration Points
Depends on Linux debugfs, PCI device naming, the `bng_re_dev` structure from `bng_re.h`, and module/device lifecycle in `bng_dev.c`. It includes BNGE and firmware/resource headers indirectly because it operates on the full `bng_re_dev`.

## Risks And Edge Cases
`debugfs_create_dir()` failures are not checked, which is common for optional debugfs but means `dbg_root` may be an error pointer or NULL depending on debugfs state. `bng_re_unregister_debugfs()` uses `debugfs_remove()` rather than recursive removal; because device removal should already remove children before module exit, this depends on clean unregister ordering.

## Test Signals
With debugfs mounted and the module loaded, `/sys/kernel/debug/bng_re` should exist. After a compatible device probes, a PCI-device-named child directory should appear and then disappear after device removal or module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.h

## Purpose
Declares the debugfs lifecycle hooks used by the `bng_re` driver.

## Important APIs, Types, And Functions
- `bng_re_debugfs_add_pdev(struct bng_re_dev *rdev)` and `bng_re_debugfs_rem_pdev(struct bng_re_dev *rdev)` manage per-device debugfs directories.
- `bng_re_register_debugfs()` and `bng_re_unregister_debugfs()` manage module-level debugfs root creation and removal.

## Control Flow
The header has no executable control flow. It allows `bng_dev.c` to call debugfs setup and teardown functions implemented in `bng_debugfs.c`.

## State And Persistence
The header stores no state. It exposes functions that mutate `bng_re_debugfs_root` and `rdev->dbg_root` in the implementation.

## Dependencies And Integration Points
The prototypes reference `struct bng_re_dev`, which is supplied by the driver's main header. It integrates the debugfs implementation with module and device lifecycle code.

## Risks And Edge Cases
There is no forward declaration for `struct bng_re_dev` in this header, so includers must include a header that defines or declares it before using these prototypes. Current source inclusion order in `bng_dev.c` and `bng_debugfs.c` satisfies this.

## Test Signals
Compilation of `bng_dev.c` and `bng_debugfs.c` confirms the prototypes match the implementation. Sparse or header self-containment checks may flag the missing forward declaration if the header is included standalone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_dev.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_dev.c

## Purpose
Implements the top-level `bng_re` RoCE auxiliary driver: module registration, auxiliary-bus probe/remove, device allocation, Ethernet-side registration, chip context setup, HWRM ring and stats allocation, RCFW channel bring-up, debugfs attachment, and orderly teardown.

## Important APIs, Types, And Functions
- Module metadata declares author, `BNG_RE_DESC`, and dual BSD/GPL licensing.
- `bng_re_dev_add()` allocates `struct bng_re_dev` with `ib_alloc_device()`, binds netdev, auxiliary device, BNGE auxiliary device, and PCI function id.
- `bng_re_register_netdev()` / `bnge_unregister_dev()` connect and disconnect the RDMA provider from the BNGE Ethernet auxiliary device.
- `bng_re_setup_chip_ctx()` and `bng_re_destroy_chip_ctx()` allocate/free chip context and device attributes, and wire `rdev->bng_res` and `rdev->rcfw` references.
- `bng_re_init_hwrm_hdr()` and `bng_re_fill_fw_msg()` are small HWRM message helpers used by ring and stats operations.
- `bng_re_net_ring_alloc()` / `bng_re_net_ring_free()` issue HWRM ring allocation/free commands through `bnge_send_msg()`.
- `bng_re_stats_ctx_alloc()` / `bng_re_stats_ctx_free()` issue HWRM stats context allocation/free commands using the DMA memory allocated by `bng_re_alloc_stats_ctx_mem()`.
- `bng_re_query_hwrm_version()` caches HWRM interface version and command timeout in `bng_re_chip_ctx`.
- `bng_re_dev_init()` is the main bring-up sequence; `bng_re_dev_uninit()` is the teardown sequence.
- `bng_re_probe()`, `bng_re_remove()`, `bng_re_mod_init()`, and `bng_re_mod_exit()` integrate with the auxiliary bus and module loader.

## Control Flow
Module init creates the debugfs root and registers an auxiliary driver named `rdma` that matches `bng_en.rdma`. Probe allocates `bng_re_en_dev_info`, stores BNGE auxiliary state in driver data, allocates an RDMA device, and calls `bng_re_dev_init()`.

`bng_re_dev_init()` registers with the Ethernet device, verifies at least two MSI-X vectors, allocates chip context and device attributes, queries HWRM version, allocates the RCFW command/event queues, copies MSI-X records into `rdev->nqr`, allocates a CREQ network ring through HWRM, maps/enables the firmware channel, queries device attributes via `bng_re_get_dev_attr()`, creates debugfs, allocates coherent stats memory, allocates a firmware stats context, initializes firmware via RCFW, and marks `BNG_RE_FLAG_RCFW_CHANNEL_EN`.

Every failure label unwinds only the resources already acquired: stats context, coherent stats memory, RCFW channel mappings and IRQ, CREQ ring, `nqr`, firmware channel queues, chip context, and netdev registration. Remove calls `bng_re_dev_uninit()`, which removes debugfs, deinitializes firmware if enabled, frees firmware and stats resources, frees `nqr`, destroys chip context, unregisters from BNGE, and deallocates the RDMA device.

## State And Persistence
Persistent driver state lives in `struct bng_re_dev`: embedded `ib_device`, flags, netdev and auxiliary device pointers, BNGE auxiliary pointer, chip context, function id, resource root, RCFW channel, MSI-X/NQ record, device attributes, debugfs root, and stats context. HWRM-allocated state includes CREQ ring id and stats context id; DMA state includes stats memory and firmware command/event queues. Flags track netdev registration and firmware channel enablement to make teardown conditional.

## Dependencies And Integration Points
Depends on Linux module, PCI, auxiliary bus, RDMA core allocation, BNGE auxiliary APIs (`bnge_register_dev()`, `bnge_unregister_dev()`, `bnge_send_msg()`), BNGE HWRM structures, `bng_fw` channel functions, `bng_res` allocation helpers, `bng_sp` device-attribute query, and debugfs helpers. It bridges the Ethernet BNGE driver and RDMA core provider instance.

## Risks And Edge Cases
Bring-up ordering is sensitive: RCFW enablement requires a CREQ ring id and MSI-X vector, and firmware initialization requires device attributes and stats context. `bng_re_dev_init()` adds debugfs before stats allocation; failures after that jump to `disable_rcfw` and do not remove the per-device debugfs directory, so a stats or firmware-init failure can leave a debugfs child until broader cleanup occurs. `bng_re_net_ring_free()` logs `req.ring_id`, which is little-endian. Resource cleanup depends on `BNG_RE_FLAG_RCFW_CHANNEL_EN`; partial channel setup before the flag is set must be fully unwound by failure labels.

## Test Signals
Module load/unload should create and remove the debugfs root and register/unregister the auxiliary driver. Probe with insufficient MSI-X vectors should fail cleanly after netdev registration is unwound. Successful probe should show HWRM version query, CREQ ring allocation, IRQ request, firmware initialization, stats context allocation, and no leaks on remove. Fault injection at each `bng_re_dev_init()` step should verify reverse-order cleanup, especially debugfs, stats, ring, and RCFW channel resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.c

## Purpose
Implements the `bng_re` RoCE firmware communication channel. It allocates command and completion queues, maps doorbell/mailbox BAR regions, starts/stops the CREQ IRQ and tasklet, sends command queue messages, waits for completions, processes firmware events, and initializes/deinitializes firmware.

## Important APIs, Types, And Functions
- `bng_re_alloc_fw_channel()` allocates CREQ and CMDQ hardware queues plus the command-response shadow table `crsqe_tbl`.
- `bng_re_free_rcfw_channel()` frees the shadow table and both hardware queues.
- `bng_re_rcfw_send_message()` is the main synchronous command path used by higher-level slow-path code.
- `__send_message_basic_sanity()` rejects commands during firmware stall, duplicate initialization, or unsupported commands before firmware initialization.
- `__send_message()` assigns a cookie, records a `bng_re_crsqe`, copies the request into 16-byte CMDQ slots, advances producer state, and rings the CMDQ mailbox doorbell.
- `__wait_for_resp()` sleeps on `cmdq.waitq`, manually services CREQ on timeout intervals, and returns when the shadow entry is no longer in use.
- `bng_re_service_creq()` drains CREQ entries in a tasklet up to `BNG_FW_CREQ_ENTRY_POLL_BUDGET`, dispatching QP events and function events, advancing consumer/epoch state, ringing the NQ doorbell, and waking waiters.
- `bng_re_process_qp_event()` handles command completions by cookie and copies firmware response data into the caller's response buffer.
- `bng_re_map_cmdq_mbox()` and `bng_re_map_creq_db()` map PCI BAR regions for command producer/trigger and CREQ consumer doorbells.
- `bng_re_rcfw_start_irq()` / `bng_re_rcfw_stop_irq()` request/free CREQ IRQs and manage tasklet lifetime.
- `bng_re_enable_fw_channel()` maps MMIO, starts IRQs, writes initial CMDQ context to firmware, and prepares the first command doorbell.
- `bng_re_init_rcfw()` sends `INITIALIZE_FW`; `bng_re_deinit_rcfw()` sends `DEINITIALIZE_FW`.

## Control Flow
Allocation starts with a CREQ queue sized by `BNG_FW_CREQE_MAX_CNT`, then a CMDQ queue sized by `BNG_FW_CMDQE_MAX_CNT`, then a zeroed `crsqe_tbl` indexed by command cookie. Channel enablement initializes sequence and waitqueue state, maps the CMDQ mailbox and CREQ doorbell, starts the IRQ/tasklet, arms the CREQ/NQ doorbell, and writes `cmdq_init` to the mapped mailbox.

To send a command, `bng_re_rcfw_send_message()` extracts the opcode, runs sanity checks, calls `__send_message()`, derives the cookie from the request, waits for response, and reports firmware status as `-EIO`. `__send_message()` holds the CMDQ lock while checking free slots, filling the cookie, recording waiter state, setting side-buffer response address/size if present, copying request bytes across command queue entries, incrementing sequence/producer state, and issuing MMIO writes with a write barrier.

The interrupt handler schedules the CREQ tasklet. The tasklet loops while entries are valid for the current epoch, uses a DMA read barrier before reading the entry body, dispatches event type, advances the consumer and epoch via `bng_re_hwq_incr_cons()`, rings the NQ doorbell if entries were processed, and wakes command waiters. Teardown masks interrupts, synchronizes and frees IRQ, kills/disables the tasklet, unmaps BARs, deinitializes firmware, frees stats resources in the caller, and frees queues.

## State And Persistence
Persistent channel state is in `struct bng_re_rcfw`: PCI device, resource root, CMDQ context, CREQ context, shadow response table, cookie table lock, depth, timeout, and interrupt-enabled count. CMDQ state includes hardware queue indices, mailbox MMIO pointers, flags such as `FIRMWARE_INITIALIZED_FLAG`, `FIRMWARE_STALL_DETECTED`, and `FIRMWARE_FIRST_FLAG`, a waitqueue, and sequence number. CREQ state includes hardware queue, doorbell info, event stats, tasklet, ring id, MSI-X vector, IRQ name, and IRQ availability.

## Dependencies And Integration Points
Depends on `bng_roce_hsi.h` command and event layouts, `bng_res` hardware queue and doorbell helpers, `bng_sp` for device attributes consumed during initialization, PCI BAR mapping APIs, Linux IRQ/tasklet/waitqueue primitives, DMA barriers, and BNGE-provided ring ids/MSI-X information passed from `bng_dev.c`.

## Risks And Edge Cases
`__wait_for_resp()` loops forever unless completion arrives because it does not return a timeout after repeated `wait_event_timeout()` expirations; callers may hang on firmware loss. `bng_re_rcfw_send_message()` only sets `FIRMWARE_STALL_DETECTED` when `rc == -ENODEV`, but `__wait_for_resp()` as written does not produce that status. The sanity path maps `-ENXIO` through `bng_re_map_rc()`, but current checks mostly return `-ETIMEDOUT`, `-EINVAL`, or `-EOPNOTSUPP`. In `bng_re_map_creq_db()`, the zero-resource check tests `reg.bar_id` instead of `reg.bar_base`, so it can log incorrectly and miss a zero BAR base. IRQ start and stop must balance tasklet setup/enable/disable/kill exactly to avoid use-after-free or disabled tasklets.

## Test Signals
Build and boot tests should verify successful CMDQ/CREQ allocation, BAR mapping, IRQ request, first doorbell write, `INITIALIZE_FW`, and `DEINITIALIZE_FW`. Firmware command tests should exercise multi-slot commands, side-buffer responses, full CMDQ returning `-EAGAIN`, firmware status errors, and CREQ event dispatch. Fault injection should cover BAR map failure, IRQ request failure, command timeout/stall, and remove while interrupts are active. Lockdep/KCSAN and DMA debug are useful for CMDQ/CREQ locking and barrier correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.h

## Purpose
Defines firmware communication constants, queue/message data structures, inline command helpers, and public RCFW channel APIs for the `bng_re` driver.

## Important APIs, Types, And Functions
- Constants define BAR regions, offsets, command queue trigger value, CREQ/CMDQ depths and entry sizes, doorbell sizes, command cookie mask, and blocking-command bit.
- `struct bng_fw_cmdqe` models a 16-byte command queue entry; `struct bng_re_crsbe` models a 1024-byte response side buffer.
- `bng_fw_cmdqe_npages()` and `bng_fw_cmdqe_page_size()` compute memory required for CMDQ depth.
- `struct bng_re_cmdq_mbox`, `bng_re_cmdq_ctx`, `bng_re_creq_db`, `bng_re_creq_ctx`, `bng_re_crsqe`, `bng_re_rcfw_sbuf`, `bng_re_rcfw`, and `bng_re_cmdqmsg` define mailbox, queue, completion, shadow-entry, side-buffer, channel, and message state.
- `bng_re_rcfw_cmd_prep()` initializes opcode and command size in a `cmdq_base`.
- `bng_re_fill_cmdqmsg()` fills a command message wrapper.
- `bng_re_get_cmd_slots()` and `bng_re_set_cmd_slots()` handle normal and TLV-encoded command sizing.
- Public prototypes expose allocation, enable/disable, IRQ start/stop, message send, firmware init, and firmware deinit.

## Control Flow
The header's inline helpers are used before command submission. Callers prepare a command with byte size, calculate required slots, then `bng_re_set_cmd_slots()` converts the command size field to firmware slot units for non-TLV commands or byte length for TLV commands. The public functions are implemented in `bng_fw.c` and are called by `bng_dev.c` and slow-path modules.

## State And Persistence
The declared structures persist channel state for the life of the RDMA device. The shadow response table tracks outstanding command cookies, response buffers, request size, free slots at submission, opcode, and waiter liveness. Flags on the command context persist firmware initialization, stall detection, and first-doorbell behavior.

## Dependencies And Integration Points
Includes `bng_tlv.h` for TLV detection and uses command/event structures and bit definitions from `bng_roce_hsi.h` through implementation includes. It relies on `bng_res.h` types such as `bng_re_hwq`, `bng_re_reg_desc`, and `bng_re_db_info`, plus Linux waitqueues, tasklets, spinlocks, PCI DMA addresses, and atomic counters.

## Risks And Edge Cases
`BNG_FW_CREQ_ENTRY_POLL_BUDGET` is defined twice with the same value, which is harmless but noisy. The command slot helpers mutate `req->cmd_size`; callers must not use the original byte size after `bng_re_set_cmd_slots()` unless they retained it separately. TLV commands interpret `total_size` as units in `get` and convert to bytes in `set`, so TLV header correctness is critical. Cookie space is fixed to `BNG_FW_CMDQE_MAX_CNT - 1`, tying outstanding command tracking to CMDQ depth.

## Test Signals
Compile coverage should catch structure/prototype drift. Unit-style tests or debug assertions around command sizing should cover TLV and non-TLV requests at boundary sizes. Runtime firmware command tests validate cookie assignment, side-buffer response addressing, first-doorbell behavior, and CREQ epoch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_re.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_re.h

## Purpose
Defines top-level driver identity constants and core runtime structures for the Broadcom `bng_re` RoCE provider.

## Important APIs, Types, And Functions
- `BNG_RE_ADEV_NAME` is `bng_en`, used with `.rdma` for auxiliary-device matching.
- `BNG_RE_DESC` describes the module as `Broadcom 800G RoCE Driver`.
- `rdev_to_dev()` converts an `rdev` pointer to the embedded `ib_device`'s Linux device pointer.
- MSI-X constants define minimum and maximum RoCE vectors and CREQ NQ index.
- `struct bng_re_nq_db`, `bng_re_nq`, and `bng_re_nq_record` model notification queues, doorbells, MSI-X records, load accounting, tasklets, and CQ notification workqueues.
- `struct bng_re_en_dev_info` stores the RDMA device and BNGE auxiliary device associated with an auxiliary-bus instance.
- `struct bng_re_ring_attr` describes ring allocation inputs passed to HWRM ring allocation.
- `struct bng_re_dev` is the main per-device object embedding `ib_device` and all driver subsystems.

## Control Flow
The header has no executable flow, but it shapes the flow in `bng_dev.c`: auxiliary probe allocates `bng_re_en_dev_info`, `bng_re_dev_add()` allocates `bng_re_dev`, and initialization fills resource, firmware, stats, debugfs, and MSI-X fields.

## State And Persistence
`struct bng_re_dev` is the key persistent state container for a probed device. It stores flags for netdev registration and RCFW enablement, netdev/auxiliary pointers, chip context, resource manager, firmware channel, notification-queue record, device attributes, debugfs dentry, and stats context. `struct bng_re_nq_record` stores MSI-X entries copied from BNGE and per-vector NQ state.

## Dependencies And Integration Points
Includes `bng_res.h` and references RDMA core, BNGE auxiliary structures, PCI, netdevice, debugfs, workqueue, tasklet, mutex, and cpumask types. It is included by device, firmware, resource, and debugfs implementation files.

## Risks And Edge Cases
Several NQ fields are defined before full NQ implementation appears in this subset, so initialization and teardown must eventually cover tasklets, IRQs, workqueues, and load locking. `BNGE_INVALID_STATS_CTX_ID` is `-1` but stored in unsigned stats fields elsewhere, making sentinel interpretation dependent on casts. Structure ownership crosses RDMA and Ethernet drivers, so auxiliary device lifetime assumptions are important.

## Test Signals
Compilation across `bng_dev.c`, `bng_fw.c`, `bng_res.c`, and `bng_debugfs.c` validates structural consistency. Runtime probe/remove tests should confirm `bng_re_dev` fields are initialized before use and reset/freed in teardown, especially flags, `nqr`, debugfs, stats, and RCFW state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_re.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.c

## Purpose
Implements low-level resource allocation for `bng_re`: coherent DMA stats memory and paged hardware queues with 0-, 1-, or 2-level page-block-list indirection.

## Important APIs, Types, And Functions
- `bng_re_alloc_stats_ctx_mem()` allocates coherent DMA memory sized by `bng_re_chip_ctx.hw_stats_size`, initializes `fw_id` to invalid, and stores DMA address/size.
- `bng_re_free_stats_ctx_mem()` frees coherent stats memory if present, clears the structure, and restores invalid firmware id.
- `bng_alloc_pbl()` allocates arrays of virtual pointers and DMA addresses, then allocates each coherent page/block for a PBL level unless `sginfo->nopte` is set.
- `bng_free_pbl()` frees all coherent pages tracked by a PBL and the vmalloc arrays.
- `bng_re_alloc_init_hwq()` computes queue page needs, allocates the required PBL levels, fills DMA PTE/PDE entries with `PTU_PTE_VALID`, marks last and next-to-last queue pages, initializes hardware queue indices, element size, page-entry counts, direct-access pointers, and lock.
- `bng_re_free_hwq()` releases all allocated PBL levels and resets queue metadata.

## Control Flow
Stats allocation is a simple coherent DMA allocation path. Hardware queue allocation rounds requested depth and stride up to powers of two, computes pages from depth * stride / page size, and chooses a PBL layout. A single page without `nopte` uses level 0 directly. Up to 512 pages uses one indirection level: level 0 contains PTEs pointing to level 1 pages. More than 512 pages uses two indirection levels: level 0 contains PDEs pointing to level 1 PBL pages, and level 1 contains PTEs pointing to level 2 data pages.

On every PBL allocation failure, control jumps to `fail`, which calls `bng_re_free_hwq()` to release any partial allocations. On success, queue indices are zeroed, hardware queue metadata is assigned, and `pbl_ptr`/`pbl_dma_ptr` are set to the level containing directly addressable queue entries.

## State And Persistence
Persistent state is held in `struct bng_re_hwq`: PCI device, lock, PBL arrays for each level, current level, direct PBL pointers, max elements, requested depth, element size, producer/consumer indices, and queue entries per page. PBL structures persist coherent page pointers, DMA mappings, page count, and page size until `bng_re_free_hwq()`.

## Dependencies And Integration Points
Depends on Linux PCI DMA coherent allocation, vmalloc, power-of-two rounding, RDMA umem headers, BNGE HSI constants, and `bng_roce_hsi.h` PTE flags. Firmware allocation in `bng_fw.c` relies on these functions for CMDQ and CREQ storage. Stats memory is used by `bng_dev.c` and firmware initialization.

## Risks And Edge Cases
The allocator rounds depth and stride for memory sizing but later sets `hwq->max_elements = hwq->depth`, where `hwq->depth` is the original requested depth, while macros such as `HWQ_CMP()` assume power-of-two `max_elements`. This is safe only if callers already request power-of-two depths; otherwise ring math can break. `bng_re_free_hwq()` returns early if `level >= BNG_PBL_LVL_MAX`, which can skip partial allocations if level was not lowered before a later allocation failure. `nopte` paths skip data-page allocation and alter direct-access level selection, so callers must supply externally backed pages consistently.

## Test Signals
Allocation tests should cover 0-page rejection, one-page level 0, small multi-page level 1, large level 2, `nopte` cases, and injected failures at every PBL allocation stage. DMA debug should show all coherent allocations freed. Runtime CREQ/CMDQ operation validates `pbl_ptr`, `pbl_dma_ptr`, producer/consumer math, and last-page PTE flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.h

## Purpose
Defines resource-management constants, data structures, doorbell helpers, hardware queue helpers, chip context, stats context, and resource allocation APIs for `bng_re`.

## Important APIs, Types, And Functions
- Queue/PBL constants define pointer indexing, free-slot calculation, maximum PBL pages per level, doorbell validity/epoch/toggle bits, and maximum TQM allocation requests.
- `struct bng_re_reg_desc` describes an MMIO register mapping.
- `struct bng_re_db_info` stores doorbell pointers, associated hardware queue, XID, flags, and toggle.
- Epoch enums define consumer and producer epoch bits for queue wrap tracking.
- `struct bng_re_chip_ctx` caches chip number, hardware stats size, HWRM interface version, and command timeout.
- `struct bng_re_pbl`, `bng_re_sg_info`, `bng_re_hwq_attr`, and `bng_re_hwq` model paged DMA queue backing and runtime queue indices.
- `struct bng_re_stats` stores DMA stats memory, size, and firmware id.
- `struct bng_re_res` ties PCI device, chip context, and device attributes together.
- `bng_re_get_qe()` returns a queue-entry pointer for an index.
- `BNG_RE_INIT_DBHDR()`, `bng_re_ring_db()`, and `bng_re_ring_nq_db()` build and write 64-bit doorbell records.
- `bng_re_hwq_incr_cons()` advances consumer index and toggles epoch on wrap.
- `_is_max_srq_ext_supported()` tests a firmware capability flag.
- Public prototypes expose hardware queue and stats memory allocation/free.

## Control Flow
Inline helpers are used in the firmware event path and queue allocation path. Consumers call `bng_re_get_qe()` to locate entries, process entries, call `bng_re_hwq_incr_cons()` to advance ring state, then ring an NQ/CQ doorbell with `bng_re_ring_nq_db()` or `bng_re_ring_db()`. Allocation functions declared here are implemented in `bng_res.c`.

## State And Persistence
The structures declared here persist all low-level DMA and MMIO state for queues, doorbells, stats, and chip capabilities. Doorbell info keeps epoch flags that persist across queue wraps. Hardware queues persist producer/consumer indices and PBL address arrays until freed.

## Dependencies And Integration Points
Includes `bng_roce_hsi.h` for hardware bit definitions such as doorbell types and capability flags. The header is consumed by `bng_dev.c`, `bng_fw.c`, `bng_res.c`, and `bng_re.h`. It depends on Linux MMIO `writeq()`, DMA address types, spinlocks, PCI devices, and page-size constants.

## Risks And Edge Cases
`HWQ_FREE_SLOTS()` uses bit masking and therefore assumes `max_elements` is a power of two. `bng_re_get_qe()` does pointer arithmetic on `void *`, relying on compiler extension semantics common in kernel builds. Doorbell writes require correct epoch and toggle handling; stale flags can cause firmware to ignore entries or treat old entries as new. `BNG_RE_INIT_DBHDR()` packs several hardware fields into a 64-bit value, so field masks and shifts must match HSI definitions exactly.

## Test Signals
Compile tests validate HSI constants and structure visibility. Runtime queue tests should verify correct queue-entry addressing, consumer wrap epoch toggling, doorbell writes on CREQ drain, and free-slot behavior at empty, full, and wraparound states. Hardware or emulated firmware tests are needed to validate packed doorbell headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_res.h -->
