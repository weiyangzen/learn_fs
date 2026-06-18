<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cq.c

## Purpose
Implements the mlx5 InfiniBand completion queue provider. It translates hardware CQEs into `struct ib_wc`, handles CQ creation for kernel and uverbs users, manages CQ arming, polling, resizing, software-generated completions, cleanup during QP/SRQ teardown, and mlx5-specific CQ uAPI attributes.

## Important APIs, Types, And Functions
- CQ callbacks: `mlx5_ib_cq_comp()` routes completion EQ events to the RDMA core CQ completion handler, and `mlx5_ib_cq_event()` reports CQ error events as `IB_EVENT_CQ_ERR`.
- CQE access helpers: `get_cqe()`, `get_sw_cqe()`, `next_cqe_sw()`, and `sw_ownership_bit()` implement mlx5 ownership-bit based CQ ring traversal.
- Completion decoding: `handle_good_req()`, `handle_responder()`, `mlx5_handle_error_cqe()`, `get_sig_err_item()`, and `handle_atomics()` map requestor, responder, error, signature, and atomic CQEs into RDMA work completions and driver state.
- Polling APIs: `mlx5_ib_poll_cq()` is the provider `poll_cq` method; `poll_soft_wc()` and `mlx5_ib_poll_sw_comp()` drain software completions and synthesize flushed completions during internal device error.
- Notification API: `mlx5_ib_arm_cq()` programs the CQ arm doorbell and reports missed software completions when requested.
- Creation/destruction: `mlx5_ib_create_user_cq()`, `mlx5_ib_create_cq()`, `mlx5_ib_pre_destroy_cq()`, `mlx5_ib_post_destroy_cq()`, and `mlx5_ib_destroy_cq()` allocate doorbells, UMEM or fragment buffers, create the core mlx5 CQ, and tear it down.
- Resize and moderation: `mlx5_ib_modify_cq()`, `mlx5_ib_resize_cq()`, `resize_user()`, `resize_kernel()`, and `copy_resize_cqes()` implement moderation commands and firmware CQ resize.
- Cleanup and software completion: `__mlx5_ib_cq_clean()`, `mlx5_ib_cq_clean()`, and `mlx5_ib_generate_wc()` remove stale CQEs and enqueue driver-generated WCs.
- uAPI: `mlx5_ib_create_cq_defs` adds optional `MLX5_IB_ATTR_CREATE_CQ_UAR_INDEX` to CQ creation.

## Control Flow
Polling takes `cq->lock`, drains pending software completions first, then loops over hardware CQEs until either the caller's budget is reached or `next_cqe_sw()` reports no software-owned entry. `mlx5_poll_one()` advances `mcq.cons_index`, executes a read barrier after the ownership check, handles resize CQEs specially, finds the QP by QPN in `dev->qp_table.tree`, and fills the caller's `ib_wc`. Successful requestor completions update SQ tail state; responder completions consume RQ or SRQ entries; error completions map mlx5 syndromes to IB WC status and update UMR recovery state for UMR QPs.

CQ creation validates the requested entry count against firmware `log_max_cq_sz`, rounds to a power-of-two ring plus one spare entry, initializes locks/lists, builds a `create_cq_in` command, gets an EQ number for the requested completion vector, and calls `mlx5_core_create_cq()`. User CQs pin a userspace CQ buffer, map the userspace doorbell page with `mlx5_ib_db_map_user()`, choose a UAR index from either the new attribute, legacy command field, or context default, and may enable CQE compression or real-time timestamps. Kernel CQs allocate a kernel doorbell record and a fragment buffer, initialize all CQEs to invalid, and use the device UAR.

CQ resize serializes with `resize_mutex`, allocates either a new user UMEM or kernel fragment buffer, builds `modify_cq_in` with new PAS/page-size/log-size fields, and calls `mlx5_core_modify_cq()` with resize opmod. User resize swaps `ibcq.umem` after firmware success; kernel resize copies CQEs up to the resize CQE under the CQ spinlock and frees the old buffer after the swap.

## State And Persistence
All state is in-memory and hardware-backed. Persistent per-CQ fields include `mcq.cqn`, `mcq.cons_index`, doorbell DMA addresses, CQE size, `ibcq.cqe`, private CQ flags, user UMEM or kernel frag buffer, resize buffers, software WC list, notification state, and QP linkage lists for send/receive CQs. CQE ownership, consumer index doorbells, and firmware CQ context persist in hardware until destroyed. Software-generated WCs are list entries owned by the CQ and freed after polling.

## Dependencies And Integration Points
The file depends on RDMA core CQ, WC, uverbs, UMEM, and cache helpers; mlx5 core CQ commands; mlx5 fragment-buffer and doorbell helpers; QP/SRQ private structures; device capabilities; and the uverbs named-ioctl framework. It integrates with `doorbell.c` for user DB mapping, with QP and SRQ teardown through `mlx5_ib_cq_clean()`, with integrity/signature MR state through `dev->sig_mrs`, with completion EQs through mlx5 core callbacks, and with provider device ops registered elsewhere in the mlx5 driver.

## Risks And Edge Cases
CQ polling is concurrency-sensitive: CQ lock coverage must match QP table removal, SRQ WQE reclamation, software WC insertion, and resize buffer swaps. Error unwinds in user CQ creation must not release `ibcq.umem` directly because ib_core owns it after assignment, while DB and command buffers remain local driver resources. CQE compression, 128-byte padding, UAR-index selection, and page-offset quantization are all capability-dependent and should reject unsupported combinations. Resize must preserve CQE ownership bits exactly or completions can be lost or duplicated. The source as read contains syntax-level risk signals, including a duplicated local `ret` declaration in `mlx5_ib_destroy_cq()` and an extra brace-looking sequence in `handle_responder()`; build coverage should catch whether these are real defects in this source snapshot.

## Test Signals
Useful signals include provider build tests with `CONFIG_INFINIBAND_MLX5`, CQ create/destroy tests for user and kernel CQs, CQE-size and compression matrix tests, UAR-index uAPI compatibility tests, CQ polling with send/recv/RDMA/atomic/UMR/error CQEs, RoCE and IB responder metadata checks, SRQ/XRC receive completion tests, internal-error flushing tests, CQ resize under load, CQ moderation changes, KASAN/KCSAN runs around resize and cleanup, and leak tests for doorbell, UMEM, software WC, and frag-buffer unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.c

## Purpose
Implements mlx5 Data Direct auxiliary PCI-device discovery and affiliation with mlx5 IB devices. It binds an RDMA device to a matching Data Direct PCI function by comparing VUID strings read from PCI VPD, allowing the IB device to use a separate data-direct device when present.

## Important APIs, Types, And Functions
- Global registries: `mlx5_data_direct_dev_list` tracks probed Data Direct PCI functions and `mlx5_data_direct_reg_list` tracks IB-device registrations waiting for a matching VUID.
- `struct mlx5_data_direct_registration` stores an `mlx5_ib_dev` pointer and fixed-size VUID copy for deferred matching.
- `mlx5_data_direct_vpd_get_vuid()` reads PCI VPD and extracts the read-only `VU` keyword into `dev->vuid`.
- `mlx5_data_direct_set_dma_caps()` configures 64-bit DMA, falls back to 32-bit DMA, and sets a 2 GiB max segment size.
- Public IB hooks: `mlx5_data_direct_ib_reg()` and `mlx5_data_direct_ib_unreg()` add/remove an IB device registration and call `mlx5_ib_data_direct_bind()` or `mlx5_ib_data_direct_unbind()` on matches.
- PCI lifecycle: `mlx5_data_direct_probe()`, `mlx5_data_direct_remove()`, and `mlx5_data_direct_shutdown()` enable/disable the PCI device and update the global matching lists.
- Module-facing hooks: `mlx5_data_direct_driver_register()` and `mlx5_data_direct_driver_unregister()` register/unregister the local `pci_driver`.

## Control Flow
When an mlx5 IB device with a VUID appears, it calls `mlx5_data_direct_ib_reg()`. The function allocates a registration, locks `mlx5_data_direct_mutex`, scans already-probed Data Direct devices for the same VUID, binds immediately if found, and then appends the registration for future device probes. When a Data Direct PCI device probes, the driver allocates `mlx5_data_direct_dev`, enables bus mastering and DMA capabilities, attempts to enable PCIe atomics, reads the VUID from VPD, and calls `mlx5_data_direct_dev_reg()`. That function binds all existing IB registrations with the same VUID and then makes the Data Direct device available for later IB registrations.

Removal reverses the order: `mlx5_data_direct_dev_unreg()` removes the PCI device from the global list first to block new affiliations, unbinds matching registered IB devices, then `mlx5_data_direct_remove()` disables PCI and frees the VUID/device allocation. `mlx5_data_direct_ib_unreg()` removes the IB registration and warns if the IB device was not registered.

## State And Persistence
The state is process-kernel memory only: two global lists protected by `mlx5_data_direct_mutex`, one VUID allocation per probed Data Direct device, and one registration allocation per registered IB device. Hardware state is limited to PCI enablement, bus mastering, DMA masks, max segment size, and attempted atomic-op enablement. No on-disk state is written.

## Dependencies And Integration Points
The file depends on PCI core, PCI VPD helpers, DMA API, mlx5 IB private definitions, and `data_direct.h`. It integrates with mlx5 IB device lifecycle through `mlx5_data_direct_ib_reg()` / `mlx5_data_direct_ib_unreg()` and with PCI module lifecycle through `pci_register_driver()`. The actual bind/unbind behavior is delegated to `mlx5_ib_data_direct_bind()` and `mlx5_ib_data_direct_unbind()` in the broader mlx5 IB driver.

## Risks And Edge Cases
All list operations require the global mutex; missed locking would race PCI probe/remove against IB registration/unregistration. `mlx5_data_direct_ib_reg()` uses `strcpy()` into a fixed buffer sized for the hardware VUID field plus NUL, so caller-provided VUID length must match that contract. If VPD lacks keyword `VU`, the PCI function is rejected. PCI atomic enablement failures are logged only at debug level and do not fail probe. Remove order assumes unbind callbacks tolerate being called while the PCI device is still enabled but already removed from the visible list.

## Test Signals
Test with a matching ConnectX-8 Data Direct PCI ID and VUID-bearing mlx5 IB device to verify immediate and deferred bind paths. Negative tests should cover missing VPD `VU`, VUID mismatch, IB unregister without registration, probe/remove races, 64-bit DMA fallback, PCI atomic-op unavailable platforms, module unload after active registrations, and KASAN/leak checks for registration and VUID allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.h

## Purpose
Declares the mlx5 Data Direct PCI-device representation and the registration hooks used by the mlx5 IB driver and module lifecycle.

## Important APIs, Types, And Functions
- `struct mlx5_data_direct_dev` stores the Linux `device`, owning `pci_dev`, VUID string, and global-list linkage for a Data Direct function.
- `mlx5_data_direct_ib_reg()` / `mlx5_data_direct_ib_unreg()` register or unregister an IB device by VUID.
- `mlx5_data_direct_driver_register()` / `mlx5_data_direct_driver_unregister()` expose PCI driver lifecycle entry points.

## Control Flow
The header has no executable control flow. It supplies declarations for `data_direct.c` and any mlx5 IB device lifecycle code that needs to register an IB device for Data Direct binding.

## State And Persistence
No state is stored in the header. The declared structure is persisted in memory by `data_direct.c` for each probed PCI Data Direct device.

## Dependencies And Integration Points
The header forward-declares `struct mlx5_ib_dev` and relies on includers to have definitions for `struct device`, `struct pci_dev`, and `struct list_head` through surrounding mlx5 or Linux headers. It is the integration contract between the Data Direct PCI shim and the rest of mlx5 IB.

## Risks And Edge Cases
The header is intentionally minimal and not standalone: direct inclusion without the common mlx5/Linux headers would miss type declarations for `device`, `pci_dev`, and `list_head`. The `vuid` pointer lifetime is implementation-owned and must be freed by the PCI remove path.

## Test Signals
Header self-containment checks may flag missing type includes if included standalone. Normal build coverage should confirm prototypes match `data_direct.c` and call sites in the mlx5 IB lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.c

## Purpose
Implements mlx5 DEVX uverbs support: user contexts, raw firmware command objects, DEVX UMEM registration, async command/event file descriptors, object event subscription and dispatch, and hardware cleanup for user files. DEVX gives privileged-capability users controlled access to mlx5 firmware commands while tracking ownership, object lifetime, and event delivery through RDMA uverbs.

## Important APIs, Types, And Functions
- Context lifecycle: `mlx5_ib_devx_create()` creates a firmware UCTX with optional raw/controlled capabilities; `mlx5_ib_devx_destroy()` destroys it; `mlx5_ib_devx_init()` creates the device-level whitelist UID and registers the event notifier; `mlx5_ib_devx_cleanup()` unregisters and frees event-table state.
- Object representation: `struct devx_obj` in `devx.h` stores encoded object ID, destroy mailbox, flags, optional mkey/DCT/CQ/flow-counter state, and event subscriptions.
- Command classification: `devx_is_obj_create_cmd()`, `devx_is_obj_modify_cmd()`, `devx_is_obj_query_cmd()`, `devx_is_general_cmd()`, `devx_is_whitelist_cmd()`, `devx_get_obj_id()`, `devx_get_created_obj_id()`, and `devx_obj_build_destroy_cmd()` decide what commands are allowed and how to track/destroy created objects.
- uverbs command handlers: `MLX5_IB_METHOD_DEVX_OTHER`, `DEVX_OBJ_CREATE`, `DEVX_OBJ_MODIFY`, `DEVX_OBJ_QUERY`, `DEVX_OBJ_ASYNC_QUERY`, `DEVX_UMEM_REG`, `DEVX_QUERY_EQN`, `DEVX_QUERY_UAR`, and `DEVX_SUBSCRIBE_EVENT` implement the exported DEVX ABI.
- Validation and safety: `devx_get_uid()` selects either the user DEVX UID or device whitelist UID; `devx_is_valid_obj_id()` proves a modify/query command targets the supplied uverbs object; `devx_set_umem_valid()` marks command fields that reference DEVX UMEM-backed buffers.
- MKEY handling: `devx_handle_mkey_create()` detects indirect mkeys, forces non-indirect mkeys to use UMEM-valid flow, and clears TPH fields; `devx_handle_mkey_indirect()` registers indirect ODP mkeys for page fault handling.
- Async command FD: `struct devx_async_cmd_event_file`, `devx_init_event_queue()`, `devx_query_callback()`, `devx_async_cmd_event_read()`, `devx_async_cmd_event_poll()`, and `devx_async_cmd_event_destroy_uobj()` queue async query completions to a read-only fd.
- Event subscription FD: `struct devx_async_event_file`, `devx_event_notifier()`, `deliver_event()`, `dispatch_event_fd()`, `devx_async_event_read()`, `devx_async_event_poll()`, and `devx_async_event_destroy_uobj()` manage firmware event delivery by object/event or unaffiliated event.
- UMEM registration: `devx_umem_get()`, `devx_umem_find_best_pgsize()`, `devx_umem_reg_cmd_alloc()`, `MLX5_IB_METHOD_DEVX_UMEM_REG`, and `devx_umem_cleanup()` pin memory, build CREATE_UMEM MTT lists, and destroy UMEM objects.
- File cleanup: `mlx5_ib_ufile_hw_cleanup()` asynchronously destroys DEVX QPs before uverbs object cleanup can continue.
- ABI registration: `mlx5_ib_devx_defs` chains DEVX object, UMEM, async command FD, and async event FD object trees into uverbs.

## Control Flow
DEVX object creation starts from a raw firmware create mailbox supplied through uverbs. The handler rejects VHCA tunnel commands, resolves the UID, validates that the opcode is a supported create command, allocates a `devx_obj`, patches UID and UMEM-valid bits, and dispatches through special core helpers for DCT and non-APU CQ or through `mlx5_cmd_do()` for generic objects. On success it copies firmware output back to userspace, builds the matching destroy mailbox, encodes object type/opcode into `obj->obj_id`, and performs extra registration for indirect ODP mkeys. If a later copy or registration step fails, the handler destroys the just-created hardware object before freeing the wrapper.

Modify and query handlers follow a narrower path: resolve UID, verify opcode class, verify the supplied uverbs object really owns the object ID referenced by the command mailbox, patch UID, optionally mark UMEM-valid fields, execute the command, and copy firmware output even for remote I/O status where the firmware produced an output buffer. General `DEVX_OTHER` permits only general or whitelisted HCA commands, using either a user DEVX UID or the device whitelist UID.

Event subscription allocates xarray nodes under `dev->devx_event_table.event_xa`, keyed by event number plus object type and optionally by object ID. After all allocation succeeds, subscriptions are linked into the fd list, xarray event list, and object list under `event_xa_lock` with RCU list operations. Firmware EQ notifications enter `devx_event_notifier()`, filter noisy kernel-only events, map the event to object type and object ID when affiliated, and dispatch to subscribed fds or eventfds under RCU.

Async query allocates output storage bounded by `MAX_ASYNC_BYTES_IN_USE`, queues `mlx5_cmd_exec_cb()` on the fd's async context, and the callback appends completion data to the fd event queue. Read paths block unless nonblocking, validate user buffer size, copy one event to userspace, and free queued data. Destroy paths mark fds destroyed, wake waiters, cleanup async contexts, and free queued events/subscriptions.

## State And Persistence
DEVX state is in-memory uverbs object state plus firmware objects. Persistent runtime fields include per-context DEVX UIDs, the device whitelist UID, `devx_event_table` xarray, object wrappers with destroy mailboxes, indirect ODP mkey registration in `odp_mkeys`, async fd event queues, event subscription lists, UMEM pinning state, and bytes-in-use counters. Firmware objects persist until their stored destroy mailbox is executed, core DCT/CQ destroy helper succeeds, or an async file cleanup marks a QP as hardware-freed.

## Dependencies And Integration Points
The file depends on RDMA uverbs ioctl/object/fd infrastructure, mlx5 firmware command layouts, mlx5 core CQ/DCT/async command helpers, flow steering headers, ODP mkey support, xarray and RCU, eventfd, poll/read file operations, UMEM/DMABUF pinning, and user-capability checks. It integrates with `devx.h`, QP cleanup, flow steering destinations and counters, DEVX flow action users in `fs.c`, mlx5 EQ notifier registration, and RDMA user capability flags such as `RDMA_UCAP_MLX5_CTRL_LOCAL` and `RDMA_UCAP_MLX5_CTRL_OTHER_VHCA`.

## Risks And Edge Cases
Security depends on exhaustive opcode classification and `devx_is_valid_obj_id()` matching each modify/query mailbox to the supplied uverbs object. Missing an opcode in create/modify/query/destroy classification can either reject a valid command or allow an untracked object. Destroy mailbox construction must preserve namespace, vport, eswitch, table, and object fields exactly; otherwise cleanup can leak or destroy the wrong firmware resource. Event subscription teardown relies on RCU plus uobject refs and must coordinate fd destruction, object destruction, and device cleanup. Async byte accounting must be decremented on every completion/error path. DEVX exposes UAR IDs intentionally; the code documents that a user can harm its own objects but should not gain broader access. UMEM page-size selection must match firmware alignment rules, especially for offsets and DMABUF-backed memory. The implementation also has policy-sensitive capability branches for raw capabilities, internal device resources, VHCA tunnel commands, and switchdev other-vhca control.

## Test Signals
Strong coverage includes uverbs DEVX create/modify/query/destroy tests for every supported opcode class, negative tests for mismatched object handles and unsupported opcodes, DEVX UMEM registration with normal UMEM and DMABUF, page-size/offset boundary tests, indirect ODP mkey lifetime tests under page faults, async query read/poll/nonblocking/overflow tests, event subscription tests for affiliated/unaffiliated/CQ completion events and eventfd redirection, ufile cleanup with many DEVX QPs, capability gating tests for raw/user/control caps, switchdev transport namespace tests, and KASAN/KCSAN/lockdep runs during concurrent subscription, fd close, object destroy, and device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.h

## Purpose
Defines the DEVX object wrapper shared by mlx5 DEVX implementation and other mlx5 IB subsystems, and provides DEVX lifecycle prototypes or stubs depending on `CONFIG_INFINIBAND_USER_ACCESS`.

## Important APIs, Types, And Functions
- `MLX5_MAX_DESTROY_INBOX_SIZE_DW` sizes the embedded destroy mailbox to the largest currently needed destroy command (`delete_fte_in`).
- `struct devx_obj` stores object ownership (`ib_dev`, `obj_id`), destroy command (`dinlen`, `dinbox`), flags, object-specific state (`mkey`, `core_dct`, `core_cq`, or `flow_counter_bulk_size`), and event subscription list.
- `mlx5_ib_devx_create()` / `mlx5_ib_devx_destroy()` manage firmware user contexts.
- `mlx5_ib_devx_init()` / `mlx5_ib_devx_cleanup()` manage device-level DEVX event infrastructure.
- `mlx5_ib_ufile_hw_cleanup()` supports hardware cleanup of DEVX objects during uverbs file teardown.
- Stubs return `-EOPNOTSUPP` or no-op when user access is disabled.

## Control Flow
The header has no direct runtime flow. Build-time `#if IS_ENABLED(CONFIG_INFINIBAND_USER_ACCESS)` selects real DEVX declarations or inline no-op fallbacks, allowing the rest of mlx5 IB to compile when uverbs user access is not enabled.

## State And Persistence
`struct devx_obj` instances persist for the lifetime of DEVX uverbs objects. The embedded destroy mailbox persists the exact command needed to free the hardware object during cleanup, while the union stores auxiliary kernel state for special object classes.

## Dependencies And Integration Points
The header includes `mlx5_ib.h` for mlx5 IB private types and core object wrappers. `devx_obj` is consumed by `devx.c` and by flow steering code that accepts DEVX objects as flow destinations or counters.

## Risks And Edge Cases
The destroy inbox size must remain large enough for every destroy command emitted by `devx_obj_build_destroy_cmd()`. The union relies on flags/opcode context to interpret the active member correctly. If user access is disabled, callers must handle `mlx5_ib_devx_create()` returning `-EOPNOTSUPP`.

## Test Signals
Build with `CONFIG_INFINIBAND_USER_ACCESS=y`, `m`, and disabled to verify real and stub paths. Compile-time checks should cover `struct devx_obj` users in DEVX and flow steering. Runtime tests should validate that every created DEVX object has a correct destroy mailbox within the configured size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.c

## Purpose
Implements mlx5 device memory (`ib_dm`) support for MEMIC device memory and software-owned ICM allocations. It provides uverbs allocation/query/mmap metadata, MEMIC operation-address mapping, and provider `alloc_dm`, `dealloc_dm`, and `reg_dm_mr` hooks.

## Important APIs, Types, And Functions
- MEMIC firmware commands: `mlx5_cmd_alloc_memic()`, `mlx5_cmd_dealloc_memic()`, `mlx5_cmd_alloc_memic_op()`, and `mlx5_cmd_dealloc_memic_op()` allocate/free MEMIC ranges and operation addresses through mlx5 firmware.
- mmap setup: `add_dm_mmap_entry()` inserts RDMA user mmap entries for device memory and MEMIC operation windows.
- MEMIC lifetime: `handle_alloc_dm_memic()`, `mlx5_dm_memic_dealloc()`, `dm_memic_remove_ops()`, `mlx5_ib_dm_memic_free()`, and `mlx5_ib_dm_mmap_free()` manage MEMIC allocation, mmap references, operation mappings, and final hardware deallocation.
- MEMIC op uAPI: `MLX5_IB_METHOD_DM_MAP_OP_ADDR`, `map_existing_op()`, `copy_op_to_user()`, and `mlx5_cmd_alloc_memic_op()` expose operation-specific addresses when firmware supports the requested operation bit.
- SW ICM lifetime: `get_icm_type()`, `handle_alloc_dm_sw_icm()`, and `mlx5_dm_icm_dealloc()` allocate/free software ICM for steering, header modify, modify-header pattern, and encap use cases.
- Public provider entry: `mlx5_ib_alloc_dm()` selects MEMIC or SW ICM by optional uAPI type.
- Query/uAPI registration: `MLX5_IB_METHOD_DM_QUERY`, `mlx5_ib_dm_defs`, and `mlx5_ib_dev_dm_ops` register query, map-op, allocation attributes, and device ops.

## Control Flow
MEMIC allocation validates length and alignment, scans `dev->dm.memic_alloc_pages` under `dm->lock` for a free aligned range, tentatively marks pages busy, then issues `ALLOC_MEMIC`. If firmware returns `-EAGAIN`, the range is unmarked and the scan advances; other errors fail; success returns a BAR-relative physical address adjusted by `dev->bar_addr`. `handle_alloc_dm_memic()` rounds the requested length to MEMIC granularity, allocates a `mlx5_ib_dm_memic`, initializes refcount/xarray/mutex state, allocates MEMIC hardware memory, inserts a user mmap entry, and returns page index/start offset to userspace.

`MLX5_IB_METHOD_DM_MAP_OP_ADDR` validates the requested operation index, checks the firmware operation bitmap, returns an existing mapping if present, or allocates a new operation address. It inserts a separate mmap entry, takes a MEMIC reference before exposing the entry, copies page index/offset to userspace, and stores the op entry in `dm->ops`. Cleanup removes mmap entries first; final hardware MEMIC deallocation occurs only when all mmap references and operation entries drop the MEMIC kref.

SW ICM allocation is capability and privilege gated. It requires both `CAP_SYS_RAWIO` and `CAP_NET_RAW`, validates the requested DM type against `sw_owner`/`sw_owner_v2` capabilities, rounds allocation size to a power-of-two multiple of the device block size, calls `mlx5_dm_sw_icm_alloc()` with the user context DEVX UID, and returns the device address as the start offset.

## State And Persistence
State includes MEMIC allocation bitmap pages in `struct mlx5_dm`, MEMIC device addresses and sizes in `struct mlx5_ib_dm`, per-MEMIC operation xarray, mmap entries stored in RDMA core, krefs that couple mmap lifetime to hardware deallocation, and SW ICM object IDs/device addresses. All state is in-memory plus firmware/BAR allocations; no filesystem persistence exists.

## Dependencies And Integration Points
The file depends on RDMA uverbs named-ioctl, RDMA user mmap entries, mlx5 device-memory firmware capabilities/commands, xarray, kref, Linux capability checks, and `mlx5_ib_reg_dm_mr()` supplied elsewhere. It integrates with the driver's mmap-free path through `mlx5_ib_dm_mmap_free()` and with DEVX/user contexts through SW ICM allocation using `to_mucontext(ctx)->devx_uid`.

## Risks And Edge Cases
MEMIC allocation must keep the bitmap synchronized with firmware allocation/deallocation; `mlx5_cmd_dealloc_memic()` clears the bitmap only after firmware deallocation succeeds, which avoids reuse after failed free but can strand bitmap space if firmware returns an error. `MLX5_IB_METHOD_DM_MAP_OP_ADDR` allocates `op_entry` but on allocation failure after `kzalloc_obj()` the local `err` value must already be meaningful; reviewers should check that path. MEMIC kref/mmap ordering is delicate because user mmap entries can outlive the `ib_dm` handle. SW ICM exposes privileged steering memory and therefore depends on capability and firmware feature gating.

## Test Signals
Run uverbs DM allocation/query/mmap tests for MEMIC, MEMIC operation mapping, and all SW ICM types. Include invalid length/alignment, unsupported operation bits, repeated map-op returning existing entries, mmap close before/after DM dealloc, firmware `-EAGAIN` allocation retry, SW ICM privilege denial, capability-denied paths, DM-backed MR registration, and leak/KASAN checks for mmap and xarray cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.h

## Purpose
Declares mlx5 device-memory types, conversion helpers, uverbs definitions, and firmware deallocation helpers shared by the DM implementation and mmap cleanup paths.

## Important APIs, Types, And Functions
- `mlx5_ib_dev_dm_ops` and `mlx5_ib_dm_defs` expose provider ops and uverbs definitions from `dm.c`.
- `struct mlx5_ib_dm` is the base mlx5 device-memory object with embedded `ib_dm`, uAPI type, device address, and size.
- `struct mlx5_ib_dm_op_entry` tracks one MEMIC operation mmap entry, operation address, owning MEMIC object, and operation ID.
- `struct mlx5_ib_dm_memic` extends the base object with MEMIC mmap entry, operation xarray, operation mutex, kref, and originally requested length.
- `struct mlx5_ib_dm_icm` extends the base object with SW ICM object ID.
- `to_mdm()`, `to_memic()`, and `to_icm()` convert RDMA core `ib_dm` pointers to mlx5 private objects.
- `mlx5_ib_alloc_dm()`, `mlx5_ib_dm_mmap_free()`, `mlx5_cmd_dealloc_memic()`, and `mlx5_cmd_dealloc_memic_op()` are cross-file entry points.

## Control Flow
The header itself has no executable control flow. It defines the object layout used by `dm.c` allocation/deallocation and by the driver's mmap-free dispatch.

## State And Persistence
The declared structures describe in-memory state for active device-memory allocations and mmap entries. They persist until RDMA core destroys the `ib_dm` object and associated mmap entries drop their references.

## Dependencies And Integration Points
The header includes `mlx5_ib.h` for RDMA and mlx5 private types. It integrates DM code with RDMA core object allocation, user mmap cleanup, and MR registration.

## Risks And Edge Cases
The conversion helpers assume the caller knows the concrete DM type; using `to_memic()` on SW ICM or `to_icm()` on MEMIC would corrupt interpretation. The kref in `mlx5_ib_dm_memic` means freeing is not identical to handle deallocation, so callers must remove mmap entries and let `mlx5_ib_dm_mmap_free()` finish hardware deallocation.

## Test Signals
Build coverage should confirm structure users match the definitions. Runtime DM tests should exercise all conversion paths indirectly by allocating/deallocating MEMIC and SW ICM objects and by closing mmap entries in different orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.c

## Purpose
Implements mlx5 RDMA DMA handle (`ib_dmah`) allocation and deallocation for PCIe TPH steering-tag support. It validates mandatory/optional DMAH fields and allocates a mlx5 steering-tag index when requested.

## Important APIs, Types, And Functions
- `mlx5_ib_alloc_dmah()` is the provider allocation callback. It requires processing-hint (`IB_DMAH_PH_EXISTS`) data, validates that CPU ID and memory type are provided as an all-or-nothing pair, and allocates a steering-tag index through `mlx5_st_alloc_index()` when ST fields are present.
- `mlx5_ib_dealloc_dmah()` frees the steering-tag index with `mlx5_st_dealloc_index()` when the DMAH had CPU ID/ST state.
- `mlx5_ib_dev_dmah_ops` registers `.alloc_dmah` and `.dealloc_dmah` with RDMA core.

## Control Flow
Allocation first checks that the PH field is present because PCIe TPH requires a processing hint. It then forms the optional steering-tag field mask from `IB_DMAH_CPU_ID_EXISTS` and `IB_DMAH_MEM_TYPE_EXISTS`; if either optional field appears without the other, allocation fails. If both are present, the mlx5 core steering-tag allocator receives memory type and CPU ID and stores the resulting index in the private DMAH object. Deallocation mirrors this by freeing the stored index only when the optional CPU ID field was present.

## State And Persistence
The only persistent per-object state is `struct mlx5_ib_dmah::st_index`. Hardware or core allocator state for steering tags is owned by mlx5 core after `mlx5_st_alloc_index()` succeeds and released during deallocation. No on-disk persistence exists.

## Dependencies And Integration Points
The file depends on RDMA DMAH core types, uverbs standard types, Linux PCI TPH support, and mlx5 core steering-tag allocation helpers. It integrates with the mlx5 IB device ops table through `mlx5_ib_dev_dmah_ops`.

## Risks And Edge Cases
Optional field validation must remain synchronized with RDMA core's `valid_fields` contract. Deallocation tests only `IB_DMAH_CPU_ID_EXISTS`; because allocation rejects partial optional ST data, this is equivalent to checking the full optional pair, but future fields could change that assumption. The code does not use `attrs` directly, so all validation depends on the prefilled `ib_dmah`.

## Test Signals
Test DMAH allocation with missing PH, PH only, PH plus complete CPU/mem-type ST fields, and partial ST fields. Verify steering-tag allocation/deallocation calls are balanced and that repeated create/destroy cycles do not leak ST indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.h

## Purpose
Declares the mlx5 private DMA handle object and provider ops used for DMAH/TPH support.

## Important APIs, Types, And Functions
- `mlx5_ib_dev_dmah_ops` is the device-ops bundle implemented in `dmah.c`.
- `struct mlx5_ib_dmah` embeds the RDMA core `ib_dmah` and stores the mlx5 steering-tag index.
- `to_mdmah()` converts `struct ib_dmah *` to `struct mlx5_ib_dmah *`.

## Control Flow
The header has no runtime control flow; it provides the object layout and inline conversion helper for the DMAH implementation.

## State And Persistence
Per-DMAH persistent state is limited to the embedded RDMA core object and `st_index`, which is valid when allocation requested steering-tag support.

## Dependencies And Integration Points
The header includes `mlx5_ib.h`, tying DMAH support to mlx5 IB private types and RDMA core definitions. It is consumed by `dmah.c` and by device setup code that installs `mlx5_ib_dev_dmah_ops`.

## Risks And Edge Cases
`to_mdmah()` assumes the `ib_dmah` is embedded in `struct mlx5_ib_dmah`; using it on another provider's object would be invalid. The header is small enough that most risk is in keeping `st_index` semantics aligned with allocation/deallocation logic.

## Test Signals
Provider build coverage and DMAH lifecycle tests should validate the ops declaration and conversion helper indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dmah.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/doorbell.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/doorbell.c

## Purpose
Manages userspace doorbell page pinning and sharing for mlx5 uverbs resources. Multiple CQs/QPs can map doorbell records from the same user page, and this file keeps one pinned UMEM and mm reference per `(mm, page-aligned virtual address)` with a reference count.

## Important APIs, Types, And Functions
- `struct mlx5_ib_user_db_page` stores list linkage, pinned one-page UMEM, page-aligned user virtual address, refcount, owning `mm_struct`, and is protected by the ucontext doorbell-page mutex.
- `mlx5_ib_db_map_user()` finds or pins a user doorbell page, computes the DMA address plus page offset, stores the page in `db->u.user_page`, and increments the page refcount.
- `mlx5_ib_db_unmap_user()` decrements the refcount and on last use removes the list entry, drops the mm reference, releases UMEM, and frees the page descriptor.

## Control Flow
Mapping locks `context->db_page_mutex`, scans `context->db_page_list` for a page matching both `current->mm` and `virt & PAGE_MASK`, and reuses it if found. Otherwise it allocates a page descriptor, pins one page with `ib_umem_get()`, grabs the current mm with `mmgrab()`, and links the descriptor into the context list. In both new and reused cases it computes `db->dma` from the first DMA SG entry plus the intra-page offset and increments `refcnt`. Unmapping takes the same mutex and frees the descriptor only when the decremented refcount reaches zero.

## State And Persistence
State is per-user-context, in-memory, and tied to RDMA object lifetimes. Each mapped doorbell page pins one user page, holds one mm reference, and remains on `context->db_page_list` while at least one mlx5 DB record references it. `struct mlx5_db` stores the DMA address and backpointer to the shared page descriptor.

## Dependencies And Integration Points
The file depends on RDMA UMEM pinning, Linux mm reference helpers, scatter-gather DMA addresses, and mlx5 IB ucontext fields. It is used by user CQ/QP/SRQ creation paths that need firmware doorbell-record DMA addresses and by their destroy paths for cleanup.

## Risks And Edge Cases
The matching key includes `current->mm`, so mapping/unmapping must occur in a context where the original user mm is meaningful. `mlx5_ib_db_unmap_user()` assumes `db->u.user_page` is valid and mapped exactly once for each unmap call. DMA address derivation assumes the one-page UMEM has a usable first SG entry. Refcount and list mutation depend entirely on `db_page_mutex`; missing the mutex in a caller would race page reuse or free.

## Test Signals
Tests should create multiple user resources sharing the same doorbell page, resources on different offsets in that page, resources from different processes with the same virtual address, and destruction in varying order. KASAN/refcount and mm/UMEM leak checks are important, as are fork/exec/process-exit scenarios around uverbs resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/doorbell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.c

## Purpose
Implements mlx5 RDMA flow steering for both legacy RDMA `ib_create_flow()` and mlx5 DEVX/raw-flow uverbs. It parses RDMA flow specs into mlx5 match/action structures, creates/destroys flow tables and rules across NIC RX/TX, FDB, RDMA, and RDMA transport namespaces, manages optional flow-counter rules, exposes raw flow matchers/actions/steering anchors, and installs provider flow ops.

## Important APIs, Types, And Functions
- Match parsing: `parse_flow_attr()` converts `union ib_flow_spec` entries into mlx5 match criteria/value for Ethernet, IPv4/IPv6, TCP/UDP, GRE, MPLS, VXLAN, tags, drop, action handles, and counters. Helpers such as `set_proto()`, `set_tos()`, `set_flow_label()`, `check_mpls_supp_fields()`, `is_valid_ethertype()`, and `get_match_criteria_enable()` validate and compact match criteria.
- Legacy flow lifecycle: `mlx5_ib_create_flow()`, `_create_flow_rule()`, `create_flow_rule()`, `create_leftovers_rule()`, `create_sniffer_rule()`, and `mlx5_ib_destroy_flow()` implement RDMA core flow creation/destruction for normal, default, multicast-default, and sniffer flows.
- Flow table management: `get_flow_table()`, `_get_flow_table()`, `_get_prio()`, `put_flow_table()`, and `ib_prio_to_core_prio()` select namespaces, priorities, capabilities, and flow-table attributes and maintain table refcounts.
- Optional counters: `mlx5_ib_fs_add_op_fc()`, `mlx5_ib_fs_remove_op_fc()`, `mlx5r_fs_bind_op_fc()`, `mlx5r_fs_unbind_op_fc()`, `mlx5r_fs_destroy_fcs()`, `add_op_fc_rules()`, and helpers build RDMA CC/CNP/packet/byte counter rules, including per-QP variants in xarrays.
- Raw flow matcher/rule uAPI: `MLX5_IB_METHOD_FLOW_MATCHER_CREATE`, `flow_matcher_cleanup()`, `raw_fs_rule_add()`, `_create_raw_flow_rule()`, `get_dests()`, `is_flow_dest()`, `is_flow_counter()`, and `MLX5_IB_METHOD_CREATE_FLOW` expose mlx5 match masks, raw match values, DEVX destinations, QP destinations, counters, flags, and action arrays.
- Steering anchors: `MLX5_IB_METHOD_STEERING_ANCHOR_CREATE`, `steering_anchor_create_res()`, the `steering_anchor_create_*` helpers, `steering_anchor_cleanup()`, `mlx5_ib_fs_cleanup_anchor()`, and `fs_cleanup_anchor()` create unmanaged user-visible anchor flow tables with drop and goto-table rules.
- Flow actions: `mlx5_ib_create_modify_header()`, `mlx5_ib_destroy_flow_action()`, `MLX5_IB_METHOD_FLOW_ACTION_CREATE_MODIFY_HEADER`, packet-reformat validation/allocation helpers, and `MLX5_IB_METHOD_FLOW_ACTION_CREATE_PACKET_REFORMAT` implement raw modify-header, decap, and packet-reformat actions.
- Initialization: `mlx5_ib_fs_init()` allocates `dev->flow_db`, RDMA transport priority arrays per port, initializes the flow-db mutex, and registers provider flow ops. `mlx5_ib_flow_defs` exposes raw matcher/action/anchor uverbs objects.

## Control Flow
Legacy flow creation validates optional mlx5 flow-counter udata, priority, flags, and egress/default combinations, allocates a destination, locks `dev->flow_db->lock`, obtains the correct flow table, builds a TIR or port destination, and calls one of the rule constructors based on `flow_attr->type`. `_create_flow_rule()` parses each flow spec in order, applies underlay-QP or eswitch source-port constraints, attaches counter destinations when requested, sets forwarding/drop/allow/action bits, and calls `mlx5_add_flow_rules()`. Destroy walks any secondary handlers, deletes rules, decrements flow-table refs, clears counter descriptions, drops matcher use counts, and frees handlers.

Flow table lookup maps RDMA/IB priorities into mlx5 namespaces and table attributes. Normal flows use bypass or egress namespaces with tunnel decap/reformat flags when supported; leftovers use the leftovers namespace; sniffers use sniffer RX/TX namespaces; raw flows can target NIC RX/TX, FDB, RDMA RX/TX, or RDMA transport RX/TX. Transport namespaces also account for switchdev representatives, vport indices, other-eswitch flags, and other-vhca capability.

Optional flow counters build count+allow rules in RDMA counter namespaces. Global counter rules are per port/type; per-QP rules match source SQN or destination QP and are stored in a caller-provided xarray keyed by QPN. Packet and byte counters share hardware flow-counter objects in paired cases, so bind/unbind and destroy paths avoid double-freeing shared counters.

Raw flow creation requires raw-capable uattrs, obtains a matcher object, validates exactly allowed destination combinations for the namespace, optionally wraps a DEVX flow counter as a local `mlx5_fc`, parses up to two action handles, accepts an optional 24-bit flow tag, and calls `raw_fs_rule_add()`. The matcher object owns the match mask and namespace selection and cannot be destroyed while `usecnt` is nonzero.

Steering anchor creation creates or reuses an unmanaged anchor table and flow table for the requested namespace/priority. The anchor table contains a drop rule and a goto-table rule pointing at the normal table; user-visible anchor table resources are intentionally retained beyond individual anchor destruction until device cleanup, as explained in `fs.h`.

## State And Persistence
State is stored in `dev->flow_db`: priority arrays for bypass, egress, FDB, RDMA RX/TX, sniffer, RDMA transport RX/TX, optional counter priorities, mutex, and table/anchor refs. Individual flow handlers store rule handles, priority/table pointers, optional matcher pointers, counter references, and linked secondary handlers. Raw matcher objects store masks, criteria-enable bits, namespace, priority, port, and use count. Steering anchors store table/rule/group handles and refcounts under `mlx5_ib_flow_prio::anchor`. Per-QP optional counters live in xarrays supplied by the counter/QP code. Hardware flow tables/rules/actions/counters persist until corresponding destroy paths run.

## Dependencies And Integration Points
The file depends on RDMA core flow APIs, uverbs ioctl/object infrastructure, mlx5 flow steering core, mlx5 flow table capability macros, mlx5 eswitch and representor data, counters code, DEVX object definitions, QP raw packet/RSS state, network header helpers, and user capability checks. It integrates with `devx.c` through DEVX objects used as flow destinations/counters, with counters through optional counter flow rules, with QP lifecycle for destination TIRs and per-QP counters, and with `fs.h` cleanup.

## Risks And Edge Cases
Flow parsing is highly order and capability sensitive. Conflicting protocol specs, unsupported trailing fields, invalid ethertype/IP combinations, MPLS field capability gaps, multicast matching that is not multicast-only, and egress/default-flow combinations must be rejected to avoid stealing traffic. Flow-table refcounts must match every successful rule insertion, including multi-rule leftovers, sniffer RX+TX, ECN IPv4+IPv6 rules, and anchor resources. Raw flow destination validation is security-sensitive because DEVX objects can represent flow tables or TIRs; namespace-specific restrictions prevent invalid forwarding. Steering anchors intentionally retain flow tables until device teardown, so cleanup must run at device destruction. Optional counter sharing can double-free counters or leak rules if paired packet/byte types are not handled consistently. Switchdev RDMA transport tables depend on representative/vport metadata and other-eswitch capability.

## Test Signals
Test legacy `ib_create_flow()` for Ethernet/IP/TCP/UDP/GRE/MPLS/VXLAN/tag/drop/counter specs, multicast-only routing, leftovers, sniffer RX/TX, egress flows, raw packet/RSS QP destinations, and invalid field masks. Raw uverbs tests should cover matcher namespaces, FDB/RDMA transport restrictions, DEVX destinations, QP destinations, drop/default-miss flags, counters with offsets, action arrays, and matcher busy destroy. Flow action tests should cover modify-header, decap, packet reformat, unsupported table/type pairs, and action cleanup. Counter tests should cover global and per-QP op counters, shared packet/byte counters, bind/unbind, and port-specific rules. Run with lockdep/KASAN/KCSAN around concurrent create/destroy and with switchdev representor scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.h

## Purpose
Declares mlx5 flow-steering initialization and cleanup helpers and documents the special lifetime rule for user-visible steering anchor flow tables.

## Important APIs, Types, And Functions
- `mlx5_ib_fs_init()` initializes the mlx5 IB flow database and registers flow provider ops.
- `mlx5_ib_fs_cleanup_anchor()` destroys retained steering-anchor resources.
- `mlx5_ib_fs_cleanup()` is an inline full cleanup helper that destroys anchors, frees RDMA transport RX/TX per-priority arrays, and frees `dev->flow_db`.

## Control Flow
The inline cleanup first calls `mlx5_ib_fs_cleanup_anchor(dev)`, then frees every allocated RDMA transport TX and RX priority array up to `MLX5_RDMA_TRANSPORT_BYPASS_PRIO`, and finally frees the `flow_db` container. The comment explains that anchor flow tables may outlive individual user anchor destruction because users can reference the table; they are destroyed only when the RDMA device is destroyed.

## State And Persistence
The header itself stores no state. It defines cleanup for `dev->flow_db`, which owns flow table priority arrays and retained steering-anchor resources allocated by `fs.c`.

## Dependencies And Integration Points
The header includes `mlx5_ib.h` and is used by mlx5 IB device lifecycle code to initialize and tear down flow steering. It pairs with `fs.c`, which allocates the flow database and implements anchor cleanup.

## Risks And Edge Cases
Cleanup assumes `dev->flow_db` was allocated and that RDMA transport arrays are either valid allocations or NULL. Anchor cleanup must precede freeing flow-db memory because anchor state is embedded in the priority arrays. The intentionally delayed anchor table destruction can look like a leak unless the device-level cleanup path is understood and tested.

## Test Signals
Build and unload/reload the mlx5 IB driver with flow steering enabled. Exercise steering anchor create/destroy followed by device teardown and verify retained anchor tables are released only at cleanup. Fault-injection tests for partial `mlx5_ib_fs_init()` allocation should verify cleanup of already allocated transport arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.h -->
