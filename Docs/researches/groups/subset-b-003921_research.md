# subset-b-003921 research

Grouped research for EFA and ERDMA RDMA driver sources. Each section preserves the original source path for reconciliation into one per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.c

## Purpose
Implements the EFA admin-command facade used by the verbs and PCI layers. The file converts driver-facing parameter/result structs into `efa_admin_*` queue entries, submits them through `efa_com_cmd_exec`, and translates completions back into handles, keys, capabilities, stats, and feature data.

## Important APIs, Types, And Functions
- QP commands: `efa_com_create_qp`, `efa_com_modify_qp`, `efa_com_query_qp`, and `efa_com_destroy_qp` marshal QP type, PD, CQ indices, queue depths, UAR, SL, RNR retry, PSN, qkey, and optional unsolicited-write-recv capability.
- CQ commands: `efa_com_create_cq` and `efa_com_destroy_cq` configure entry size, sub-CQ depth/count, optional EQ interrupt mode, SGID source-address reporting, DMA base address, CQ index, and doorbell validity.
- MR commands: `efa_com_register_mr` and `efa_com_dereg_mr` support inline PBL arrays, direct control buffers, and indirect chained control buffers, then return lkey/rkey and interconnect IDs.
- AH, PD, UAR, features, and stats are handled by `efa_com_create_ah`, `efa_com_destroy_ah`, `efa_com_alloc_pd`, `efa_com_dealloc_pd`, `efa_com_alloc_uar`, `efa_com_dealloc_uar`, `efa_com_get_device_attr`, `efa_com_get_hw_hints`, `efa_com_set_aenq_config`, and `efa_com_get_stats`.

## Control Flow
Each public function builds a zeroed admin command, sets `aq_common_desc` or `aq_common_descriptor` opcode, fills device-specific fields, submits to `edev->aq`, and returns early on command failure with ratelimited diagnostics. Feature operations first call `efa_com_check_supported_feature_id`, except device attributes are always allowed so the driver can discover the supported feature bitmap. Device attribute discovery sequences multiple get-feature calls: device attributes, queue attributes 1, optional queue attributes 2, network attributes, and optional event queue attributes.

## State And Persistence Behavior
This file does not persist state outside the device and RDMA object lifetimes. It updates `edev->supported_features` after reading device attributes, returns hardware object identifiers to callers, and reports hardware counters on demand. All persistent kernel object ownership lives in the caller; command results are used by `efa_verbs.c` and `efa_main.c` to populate QPs, CQs, MRs, AHs, PDs, UARs, EQs, and stats.

## Dependencies And Integration Points
The code depends on `efa_com.h`, `efa_com_cmd.h`, generated admin definitions, `efa_com_cmd_exec`, `efa_com_set_dma_addr`, and `EFA_GET`/`EFA_SET` bitfield helpers. It integrates upward with RDMA verbs resource creation and device probing, and downward with the EFA admin queue.

## Risks
Risks are concentrated in bitfield correctness, command flag selection, and result interpretation. Incorrect control-buffer flags for indirect MRs can make firmware read the PBL incorrectly. Optional feature gates must stay synchronized with firmware capabilities. Stats switch handling assumes known stat types from callers and has no default error for unexpected types.

## Test Signals
Useful signals include successful probe capability discovery, QP/CQ/MR/AH create-destroy loops, unsupported feature negative tests, MR registration with inline/direct/indirect PBLs, AENQ group negotiation, and RDMA hw stats queries returning stable values or clear errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.h

## Purpose
Defines the driver-internal API contract for EFA admin-command helpers. It provides small parameter/result structs that isolate verbs code from raw admin queue descriptors.

## Important APIs, Types, And Functions
- QP structs cover create/modify/query/destroy inputs and outputs, including queue ring sizes, depths, CQ indices, UAR, PD, QP handle, QPN, doorbell offsets, LLQ descriptor offset, and sub-CQ indices.
- CQ, AH, PD, UAR, MR, feature, and stats structs define the exact fields consumed by `efa_com_cmd.c`.
- `efa_com_get_device_attr_result` aggregates firmware, queue, network, event queue, and capability data used by `efa_main.c` and `efa_verbs.c`.
- `efa_com_reg_mr_params` captures inline PBL, direct PBL, and indirect PBL modes; `efa_com_reg_mr_result` exposes lkey/rkey plus interconnect IDs.

## Control Flow
The header has no runtime control flow, but its declarations define the direction of control: higher layers allocate or validate RDMA objects, populate these structs, call `efa_com_*`, then store returned hardware handles and limits.

## State And Persistence Behavior
Struct instances are per-command transient state. Returned handles, keys, limits, and feature masks become persistent fields in `struct efa_dev`, QP/CQ/MR/AH objects, user contexts, and RDMA stats.

## Dependencies And Integration Points
Includes `efa_com.h` and depends on admin enums such as `enum efa_admin_aq_feature_id`. It is consumed by EFA verbs and main driver setup and implemented by `efa_com_cmd.c`.

## Risks
The struct layout is a compatibility boundary between driver code and the admin command layer. Field size mismatches, missing optional fields, or incorrect bool/bitfield expectations can silently corrupt command descriptors. MR PBL fields are especially sensitive because inline and control-buffer modes share a union.

## Test Signals
Compile coverage is important because this file feeds many call sites. Runtime signals include correct device attribute population, queue limit reporting, successful object allocation, and MR registration across inline and indirect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_common_defs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_common_defs.h

## Purpose
Provides common EFA wire-format helpers and shared definitions used by generated EFA admin and IO structures. It centralizes spec version constants, bitfield access helpers, and a common 64-bit memory address split into low/high 32-bit words.

## Important APIs, Types, And Functions
- `EFA_COMMON_SPEC_VERSION_MAJOR` and `EFA_COMMON_SPEC_VERSION_MINOR` identify the host info spec version reported to firmware.
- `EFA_GET(ptr, mask)` and `EFA_SET(ptr, mask, value)` wrap Linux `FIELD_GET` and `FIELD_PREP` using the EFA convention that a logical field name has a corresponding `_MASK`.
- `struct efa_common_mem_addr` is the common low/high address representation.

## Control Flow
There is no standalone control flow. The macros are inlined throughout command construction, completion parsing, register interpretation, and host-info setup.

## State And Persistence Behavior
No state is owned here. The macros mutate caller-provided descriptor fields in place; the common memory address struct is embedded in command descriptors and copied to firmware-visible memory.

## Dependencies And Integration Points
Depends on `<linux/bitfield.h>`. Integrated by EFA command, register, and generated definition files wherever bitfield masks are used.

## Risks
The macros assume `mask##_MASK` exists and that the pointed-to field has the expected integer width. Passing a field with stale bits or an incompatible mask can corrupt adjacent fields. Because `EFA_SET` preserves unrelated bits, callers must initialize descriptors when required.

## Test Signals
Build failures catch missing mask symbols. Runtime signals include correct decoded capabilities, proper host-info spec version fields, and successful command descriptors where multiple flags share one word.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_common_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_io_defs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_io_defs.h

## Purpose
Defines EFA IO queue descriptor formats for send, receive, fast memory registration/invalidation, RDMA read/write, and completions. These are the hardware-visible WQE and CQE layouts shared with userspace and the device.

## Important APIs, Types, And Functions
- Enums define queue types, send opcodes, completion statuses, and fast-registration PBL modes.
- `struct efa_io_tx_meta_desc`, `efa_io_tx_buf_desc`, `efa_io_remote_mem_addr`, `efa_io_rdma_req`, `efa_io_fast_mr_reg_req`, `efa_io_fast_mr_inv_req`, and `efa_io_tx_wqe` model transmit WQEs.
- `struct efa_io_rx_desc` models receive descriptors.
- `struct efa_io_cdesc_common`, `efa_io_tx_cdesc`, `efa_io_rx_cdesc`, `efa_io_rx_cdesc_rdma_write`, and `efa_io_rx_cdesc_ex` model completions.
- Mask macros describe all packed control, status, LKey, phase, queue type, immediate-data, unsolicited, and PBL-mode fields.

## Control Flow
The header has no executable control flow. It controls how `efa_verbs.c` validates CQ entry sizes and how userspace libraries compose or parse queue entries mapped through doorbells, LLQ memory, and DMA-backed queues.

## State And Persistence Behavior
The descriptors are ring-buffer state exchanged between userspace/kernel and hardware. Phase bits, request IDs, queue type flags, completion status, and WQE indexes form the persistent queue protocol while QPs/CQs are alive.

## Dependencies And Integration Points
Consumed by `efa_verbs.c` for CQ entry-size validation and by userspace ABI code that understands EFA queues. It depends on Linux bit macros through included project headers.

## Risks
Any layout drift breaks ABI and device interpretation. Inline data, immediate data, and RDMA local/remote memory fields overlap in unions, so opcode and flag correctness is critical. Completion status mappings must remain aligned with verbs error handling in userspace.

## Test Signals
Signals include successful CQ creation with base and extended RX completion sizes, send/recv completion parsing in userspace, RDMA read/write status reporting, immediate-data delivery, and fast-MR register/invalidate operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_io_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_main.c

## Purpose
Owns EFA PCI probe/remove/shutdown, BAR and MSI-X setup, admin/AENQ initialization, event queue creation, and RDMA core device registration.

## Important APIs, Types, And Functions
- PCI entry points are `efa_probe`, `efa_remove`, and `efa_shutdown`; `efa_pci_driver` binds Amazon EFA VF device IDs.
- Device setup flows through `efa_probe_device`, `efa_device_init`, `efa_enable_msix`, `efa_set_mgmnt_irq`, `efa_com_admin_init`, and `efa_ib_device_add`.
- Event handling uses `efa_intr_msix_mgmnt`, `efa_intr_msix_comp`, `efa_process_eqe`, `efa_process_comp_eqe`, `efa_create_eqs`, and `efa_destroy_eqs`.
- `efa_dev_ops` registers the verbs implemented in `efa_verbs.c`.

## Control Flow
Probe enables the PCI memory function, allocates `struct efa_dev`, requests register and memory BARs, maps the register BAR, initializes readless MMIO, resets and validates the device, configures DMA width, enables MSI-X, requests the management IRQ, and initializes admin queues. RDMA registration then fetches device attributes, requests the doorbell BAR, applies hardware hints, enables AENQ groups, creates completion EQs, sets host info, installs verbs ops, and calls `ib_register_device`. Remove unregisters the IB device first, then destroys EQs, releases doorbells, resets/admin-destroys the device, frees IRQs/vectors, unmaps BARs, destroys the CQ xarray, and disables PCI.

## State And Persistence Behavior
Persistent runtime state includes PCI BAR addresses/lengths, mapped `edev->reg_bar`, doorbell BAR metadata, MSI-X vector assignments, admin IRQ, completion EQ array, CQ xarray, device attributes, stats, and node GUID. Keep-alive AENQ events increment an atomic stats counter.

## Dependencies And Integration Points
Integrates Linux PCI, IRQ, DMA, RDMA core, EFA admin queue, AENQ, EQ, and verbs layers. Completion events use `dev->cqs_xa` to locate CQs and invoke RDMA completion handlers. Host info uses kernel release/version and PCI BDF fields.

## Risks
Probe and unwind ordering is critical because IRQs can race with CQ/EQ destruction. Doorbell BAR selection may differ from base BARs and must be separately requested/released. `efa_shutdown` destroys EQs and resets without unregistering the IB device, so shutdown ordering assumes system teardown. Hardware hint units are converted for MMIO timeout and must remain consistent with firmware.

## Test Signals
Signals include clean probe/remove under repeated module load/unload, `ibv_devinfo` visibility, MSI-X vector allocation across CPU counts, CQ notification delivery, AENQ keep-alive stats increments, deferred probe on reset timeout, and fault-injected failures at each setup label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_regs_defs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_regs_defs.h

## Purpose
Defines the EFA register ABI: reset reasons, BAR register offsets, and bit masks for version, capabilities, admin queues, AENQ, interrupt mask, device control/status, MMIO register reads, and EQ doorbells.

## Important APIs, Types, And Functions
- `enum efa_regs_reset_reason_types` lists reset reasons used by probe, remove, shutdown, and error paths.
- Offset macros describe register BAR layout from version through EQ doorbell.
- Mask macros describe fields for controller version, DMA width, reset/admin timeouts, queue depths and entry sizes, AENQ vector info, interrupt enable, reset status, fatal error, MMIO read request/response, and EQ doorbell arm/number.

## Control Flow
No executable control flow exists here. These constants drive control flow in lower-level EFA common code and `efa_main.c`, especially reset, version validation, queue initialization, interrupt masking, and EQ notification.

## State And Persistence Behavior
Register fields are persistent device state. Driver writes to control and doorbell registers and polls status/read-response registers; the header defines how those fields are interpreted.

## Dependencies And Integration Points
Consumed by `efa_com` and `efa_main.c`. It integrates the driver with the PCI register BAR and firmware/device reset protocol.

## Risks
Incorrect masks or offsets can cause destructive device control writes or missed status transitions. Reset reason values must match firmware expectations to support diagnostics and safe shutdown.

## Test Signals
Signals include successful version validation, admin queue initialization, reset completion polling, MMIO register-read responses, interrupt enable behavior, and EQ doorbell notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_regs_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_verbs.c

## Purpose
Implements EFA RDMA core verbs and custom uverbs: device/port queries, PD/UAR allocation, QP/CQ creation and destruction, QP state changes, user MR and dmabuf MR registration, mmap, AH management, hardware stats, and MR interconnect-ID query.

## Important APIs, Types, And Functions
- Object helpers convert RDMA core objects to EFA objects; `efa_user_mmap_entry` tracks mmap offsets, physical/BAR addresses, and mapping cache mode.
- Query and allocation functions include `efa_query_device`, `efa_query_port`, `efa_query_gid`, `efa_query_pkey`, `efa_alloc_pd`, `efa_dealloc_pd`, `efa_alloc_ucontext`, and `efa_dealloc_ucontext`.
- Queue functions include `efa_create_qp`, `efa_destroy_qp`, `efa_modify_qp`, `efa_query_qp`, `efa_create_user_cq`, and `efa_destroy_cq`.
- MR/PBL functions include `pbl_create`, `pbl_chunk_list_create`, `efa_register_mr`, `efa_reg_mr`, `efa_reg_user_mr_dmabuf`, `efa_dereg_mr`, and the `EFA_IB_METHOD_MR_QUERY` uverbs method.
- MMAP/AH/stats functions include `efa_mmap`, `efa_mmap_free`, `efa_create_ah`, `efa_destroy_ah`, `efa_get_hw_stats`, and `efa_port_link_layer`.

## Control Flow
Resource creation validates userspace ABI padding and capabilities, allocates kernel/DMA backing when needed, posts an admin command through `efa_com_cmd.c`, installs mmap entries or xarray entries, copies response data to userspace, and unwinds in reverse order on failure. QP creation maps RQ memory if requested, creates the hardware QP, exposes SQ/RQ doorbells, LLQ descriptors, and RQ memory to userspace, then stores QP handles and limits. CQ creation supports external contiguous `ib_umem` or driver-allocated DMA memory, optional completion channels backed by EQs, xarray lookup for interrupts, and mmap response keys.

## State And Persistence Behavior
Persistent object state includes PD numbers, UAR numbers, QP handles/QPNs/state/capabilities/RQ DMA buffers, CQ indices/DMA buffers/EQ association, MR umem/lkey/rkey/interconnect IDs, AH firmware handles, mmap entries, and atomic error/stat counters. PBLs are temporary command-time state and are destroyed after MR registration. CQ xarray entries persist only while interrupt-driven CQs are alive.

## Dependencies And Integration Points
Depends on RDMA core APIs, uverbs named ioctl definitions, DMA mapping, umem/dmabuf helpers, xarray lookup from `efa_main.c`, EFA admin commands, and EFA IO descriptor definitions. It exposes kernel objects to userspace through `rdma_user_mmap_entry_insert` and custom uverbs.

## Risks
Major risks include ABI padding mistakes, mmap lifetime leaks, DMA mapping failures, incomplete unwind after hardware object creation, interrupt races during CQ destruction, and PBL chunk chaining bugs for large MRs. QP state validation differs for SRD driver QPs and UD QPs; unsupported masks must stay strict. `vm_insert_page` for DMA-backed pages assumes the allocated pages remain alive until mmap entry removal.

## Test Signals
Signals include rdma-core EFA provider tests, PD/UAR leak checks, CQ/QP create-destroy with and without completion channels, mmap of doorbells/LLQ/RQ/CQ memory, QP state transition matrix tests, MR registration for small inline and large indirect PBLs, dmabuf MR registration, AH create/destroy, and hw stats reads under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Kconfig

## Purpose
Adds the Kconfig entry for Alibaba Elastic RDMA Adapter support under InfiniBand/RDMA hardware drivers.

## Important APIs, Types, And Functions
- `config INFINIBAND_ERDMA` is a tristate option with prompt text and module help.
- Dependencies require `PCI_MSI`, `64BIT`, `INFINIBAND_ADDR_TRANS`, and `INFINIBAND_USER_ACCESS`.

## Control Flow
There is no runtime control flow. The option controls whether the ERDMA objects in the local Makefile are built into the kernel, built as `erdma.ko`, or omitted.

## State And Persistence Behavior
The selected config state persists in the kernel `.config`. At runtime it determines whether PCI device IDs can bind to the ERDMA driver and whether user access and address translation support are available.

## Dependencies And Integration Points
Integrates with Kbuild, RDMA core configuration, PCI MSI support, and 64-bit architectures. The help text declares the module name `erdma`.

## Risks
Missing dependencies would produce build failures or a driver without required RDMA user/address facilities. Overly strict dependencies may hide the driver on otherwise capable systems.

## Test Signals
Signals include Kconfig visibility under expected architectures, successful `M` module builds, and absence of ERDMA objects when the option is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Makefile

## Purpose
Defines the ERDMA module build target and its constituent object files.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_INFINIBAND_ERDMA) := erdma.o` ties the module to the Kconfig option.
- `erdma-y` links CM, main, command queue, CQ, verbs, QP, and EQ objects into the driver.

## Control Flow
No runtime control flow. Kbuild composes `erdma.o` from the listed translation units when the config is enabled.

## State And Persistence Behavior
The file determines build artifact composition only. Runtime state comes from the included C files.

## Dependencies And Integration Points
Integrates with Kbuild and depends on the source files named in `erdma-y`; notably `erdma_verbs.o` is part of the module even though it is outside this work item.

## Risks
Omitting an object causes unresolved symbols or missing RDMA operations. Adding order-sensitive initialization to object file constructors would be risky, but current code uses explicit module init paths.

## Test Signals
Signals include successful kernel/module builds and symbol resolution for functions referenced across `erdma_main.c`, `erdma_cm.c`, `erdma_cmdq.c`, `erdma_cq.c`, `erdma_qp.c`, and `erdma_eq.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma.h

## Purpose
Defines core ERDMA driver state, queue structs, device attributes, resource allocators, register accessors, and cross-file function prototypes.

## Important APIs, Types, And Functions
- Queue structs include `erdma_eq`, `erdma_cmdq_sq`, `erdma_cmdq_cq`, `erdma_comp_wait`, and `erdma_cmdq`.
- Device and resource structs include `erdma_devattr`, `erdma_irq`, `erdma_eq_cb`, `erdma_resource_cb`, and `erdma_dev`.
- Helpers include `get_queue_entry`, `to_edev`, register read/write wrappers, `ERDMA_GET`, and prototypes for command queue, EQ, CEQ, AEQ, and completion handlers.

## Control Flow
The header defines the shared call graph between main probe, command queue setup, event queue setup, verbs, QP, CQ, and CM. Inline register helpers are used throughout initialization and doorbell paths.

## State And Persistence Behavior
`struct erdma_dev` is the persistent per-device root containing PCI/netdev bindings, BAR mapping, attributes, command and event queues, resource bitmaps, QP/CQ xarrays, context count, CEP list, DMA pools, workqueue, and protocol type. Queue structs persist DMA buffers, doorbell records, indices, depths, locks, and counters.

## Dependencies And Integration Points
Includes Linux bitfield/netdevice/PCI/xarray and RDMA core headers plus `erdma_hw.h`. It is the common internal header for the ERDMA module.

## Risks
Because this header defines shared ownership, lifetime mistakes cascade across files. Queue index fields are 16/32-bit ring positions and must align with power-of-two depths. Register access helpers assume `dev->func_bar` is mapped and valid.

## Test Signals
Signals include clean compile across all ERDMA objects, probe/remove without leaks, xarray QP/CQ lookup under interrupts, command queue completion waits, and resource bitmap exhaustion/reuse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.c

## Purpose
Implements ERDMA iWARP connection management over TCP sockets, including socket callback interception, MPA request/reply negotiation, IWCM upcalls, listen/connect/accept/reject operations, endpoint lifetime, timers, and QP transition coupling.

## Important APIs, Types, And Functions
- Socket callback management: `erdma_sk_assign_cm_upcalls`, `erdma_sk_save_upcalls`, `erdma_sk_restore_upcalls`, `erdma_socket_disassoc`, and `erdma_cep_socket_assoc`.
- CEP lifetime/work management: `erdma_cep_alloc`, `erdma_cep_get`, `erdma_cep_put`, `erdma_cep_set_inuse`, `erdma_cep_set_free`, `erdma_cm_alloc_work`, `erdma_cm_queue_work`, and `erdma_cm_work_handler`.
- MPA handling: `erdma_send_mpareqrep`, `erdma_recv_mpa_rr`, `erdma_proc_mpareq`, `erdma_proc_mpareply`, revision and congestion-control helpers.
- IWCM entry points: `erdma_connect`, `erdma_accept`, `erdma_reject`, `erdma_create_listen`, `erdma_destroy_listen`, plus `erdma_cm_init` and `erdma_cm_exit`.

## Control Flow
Active connect allocates a CEP and socket, associates it with a QP and IWCM ID, installs socket callbacks, optionally copies private data, binds/connects nonblocking, and queues connected or timeout work. Once TCP is established, it sends an MPA request and waits for a reply; on success it moves the QP to RTS and reports `IW_CM_EVENT_CONNECT_REPLY`. Passive listen creates a listening CEP; accepted sockets allocate child CEPs, wait for MPA requests, issue `CONNECT_REQUEST`, and later `erdma_accept` moves the QP to RTS, sends an MPA reply, and reports established. Socket state/data callbacks enqueue work that serializes on `cep->in_use`.

## State And Persistence Behavior
Persistent state includes global `erdma_cm_wq`, per-device CEP list, per-CEP socket, IWCM ID, QP pointer, state enum, refcount, work freelist, MPA buffers, timers, ORD/IRD values, private data, and saved socket callbacks. CEP references are held by sockets, work items, QPs, IWCM IDs, listen parents, and provider data paths.

## Dependencies And Integration Points
Depends on Linux sockets/TCP, workqueues, IWCM, ERDMA QP state functions, device attributes, and `erdma_cm.h`. It integrates with `erdma_main.c` through protocol-specific device ops and with `erdma_qp.c` through LLP close/drop and RTS transitions.

## Risks
This is a high-concurrency file. Risks include socket callback restore races, CEP refcount imbalance, work item reuse while delayed work is queued, MPA partial-read handling, private-data bounds, listen parent references, and QP/CEP teardown races. IPv6 is rejected, and marker/CRC MPA features are explicitly unsupported. In `erdma_accept`, the IRD check compares to `max_ord`, which deserves scrutiny against the intended `max_ird`.

## Test Signals
Signals include active/passive iWARP connection establishment, reject paths, private-data exchange, timeout paths, peer close during MPA negotiation, simultaneous QP destroy and socket close, listen backlog handling, IPv6 negative tests, marker/CRC rejection, and KASAN/KCSAN/refcount testing around CEP teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.h

## Purpose
Defines ERDMA iWARP CM protocol constants, MPA headers, endpoint states, socket callback storage, CM work types, CEP state, and IWCM function prototypes.

## Important APIs, Types, And Functions
- MPA definitions include revision, max private data, request/reply keys, header length, flags, `struct mpa_rr`, and `struct erdma_mpa_ext`.
- `struct erdma_cep` is the connection endpoint object tying IWCM IDs, device list membership, socket, QP, listen hierarchy, MPA buffers, timers, private data, and saved socket callbacks together.
- Work types enumerate accept, MPA read, close, peer close, MPA timeout, connected, and connect timeout operations.
- Prototypes expose connect/accept/reject/listen lifecycle and CEP reference helpers.

## Control Flow
The header describes the CM state machine used by `erdma_cm.c`: idle, listening, connecting, awaiting MPA request/reply, received request, RDMA mode, and closed.

## State And Persistence Behavior
CEP state is persistent for the lifetime of a connection or listener. The MPA info tracks partial header/private-data receipt across nonblocking socket callbacks. Saved callback pointers persist until socket disassociation restores them.

## Dependencies And Integration Points
Includes TCP/socket and IWCM headers. It is consumed by `erdma_cm.c`, `erdma_qp.c`, and `erdma_main.c` protocol-specific iWARP ops.

## Risks
The header encodes assumptions that only IPv4 and MPA revision 129 are supported by the implementation. `sk_to_cep` relies on `sk_user_data` ownership, so collisions with other socket users would be unsafe.

## Test Signals
Signals include state-machine coverage, compile checks for all iWARP ops, MPA private-data limits, callback association/disassociation, and reference counting under connection churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cmdq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cmdq.c

## Purpose
Implements the ERDMA firmware command queue: SQ/CQ/EQ allocation, command submission, doorbell ringing, completion polling/interrupt handling, wait context management, timeouts, and response extraction.

## Important APIs, Types, And Functions
- Initialization and teardown: `erdma_cmdq_init`, `erdma_finish_cmdq_init`, `erdma_cmdq_destroy`, and SQ/CQ/EQ helper initializers.
- Submission path: `erdma_cmdq_build_reqhdr`, `erdma_post_cmd_wait`, `get_comp_wait`, `push_cmdq_sqe`, `kick_cmdq_db`, and `put_comp_wait`.
- Completion path: `erdma_cmdq_completion_handler`, `erdma_polling_cmd_completions`, `erdma_poll_single_cmd_completion`, `erdma_wait_cmd_completion`, and `erdma_poll_cmd_completion`.

## Control Flow
Initialization allocates a wait pool/bitmap, coherent SQ and CQ buffers, doorbell records from the DMA pool, a command EQ, writes queue addresses/depths/doorbell-record DMA addresses to BAR registers, and marks the command queue OK. Command submission takes a credit, allocates a wait context cookie, writes the SQE with header fields for opcode, WQEBB count, WQE index, and context cookie, rings the SQ doorbell, then waits by completion or polling depending on sleepability. Interrupt handling drains command EQEs, polls CQEs, completes waiters, rearms the CQ, and notifies the EQ.

## State And Persistence Behavior
Persistent command queue state includes SQ/CQ/EQ DMA buffers, producer/consumer indices, doorbell records, completion wait bitmap/pool, semaphore credits, command serial number, and state bits. A timeout clears `ERDMA_CMDQ_STATE_OK_BIT`, blocking future commands.

## Dependencies And Integration Points
Depends on `erdma.h`, register macros from `erdma_hw.h`, coherent DMA, DMA pools, completions, semaphores, and EQ helpers. All higher-level device, queue, MR, QP, AH, GID, stats, and MTU commands go through this file.

## Risks
Timeout handling intentionally poisons the command queue; recovery depends on higher-level reset/remove. Non-sleepable submission busy-waits on credits and completion, so it must remain bounded and used only where required. Cookie extraction reads the original SQE header by SQE index; corruption there breaks waiter matching. Unwind paths must free DMA pool records as well as coherent buffers.

## Test Signals
Signals include firmware query success during probe, concurrent command submissions up to 128 outstanding, forced completion status errors, command timeout behavior, interrupt and polling command paths, and module unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cmdq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cq.c

## Purpose
Implements ERDMA kernel CQ notification, CQE polling, CQE-to-`ib_wc` translation, UD metadata extraction, and CQE cleanup for QP reset/destroy.

## Important APIs, Types, And Functions
- `erdma_req_notify_cq` arms a CQ and optionally reports missed events.
- `erdma_poll_cq` and `erdma_poll_one_cqe` consume CQEs and fill `struct ib_wc`.
- `erdma_process_ud_cqe` fills RoCEv2 UD source QP, SL, PKey, and network header type.
- `erdma_remove_cqes_of_qp` compacts pending CQEs to remove entries belonging to a QP.

## Control Flow
Polling locks the kernel CQ, repeatedly checks owner bits against the consumer index, advances CI, reads CQE fields after `dma_rmb`, resolves the QP by QPN, chooses send or receive WR ID tables, updates SQ CI for send completions, maps hardware opcodes/statuses to RDMA core values, and returns the number of valid completions. Notification builds a CQ doorbell with notify count, CQN, arm/solicited bits, command serial number, and CI.

## State And Persistence Behavior
CQ state includes kernel CQ buffer, CI, notification count, command serial number, doorbell record, CQN, and QP WR ID tables indirectly referenced during polling. CQE removal mutates the CQ ring to discard stale QP completions and adjusts CI.

## Dependencies And Integration Points
Depends on `erdma_verbs.h`, hardware CQE formats, QP/CQ xarray lookup helpers, RDMA core CQ APIs, and CEQ event handling in `erdma_eq.c`.

## Risks
Invalid CQEs for missing QPs are ignored after consuming CI, which is intentional but can hide teardown races. Opcode table indexing assumes hardware opcodes are within `ERDMA_NUM_OPCODES`. CQE compaction must preserve owner bits to avoid corrupting ring phase semantics. RQ overflow is not explicitly checked in post-recv code, making completion behavior under overposting worth testing with the QP path.

## Test Signals
Signals include send/recv/RDMA/atomic/REG_MR completion status mapping, solicited and missed-event notification behavior, UD GRH metadata, polling while QPs are destroyed, and CQE cleanup on QP reset/error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_eq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_eq.c

## Purpose
Implements ERDMA event queues: common EQ allocation/notification, asynchronous event handling, completion event queue handling, CEQ IRQ/tasklet setup, firmware create/destroy EQ commands, and CEQ array lifecycle.

## Important APIs, Types, And Functions
- Common helpers: `notify_eq`, `get_next_valid_eqe`, `erdma_eq_common_init`, and `erdma_eq_destroy`.
- AEQ: `erdma_aeq_init` and `erdma_aeq_event_handler`.
- CEQ: `erdma_ceq_completion_handler`, `erdma_set_ceq_irq`, `erdma_free_ceq_irq`, `erdma_ceq_init_one`, `erdma_ceq_uninit_one`, `erdma_ceqs_init`, and `erdma_ceqs_uninit`.

## Control Flow
Common init allocates coherent EQ memory and a DMA-pool doorbell record. AEQ init writes AEQ buffer address/depth and DB record to registers. CEQ init creates one EQ per completion vector, writes a command queue create-EQ request, then requests an IRQ whose handler schedules a tasklet. CEQ handling drains bounded chunks of EQEs, looks up CQs by CQN, advances CQ command serial for kernel CQs, and invokes completion handlers. AEQ handling maps CQ error events to `IB_EVENT_CQ_ERR` and other QP events to `IB_EVENT_QP_FATAL`.

## State And Persistence Behavior
EQ state persists DMA queue memory, CI, depth, doorbell address, DB record, and event/notify counters. `erdma_eq_cb.ready` gates CEQ event handling while create/destroy races are possible.

## Dependencies And Integration Points
Depends on command queue submission for CEQ create/destroy, IRQ APIs, tasklets, RDMA event callbacks, QP/CQ xarray lookup helpers, and BAR doorbell registers.

## Risks
AEQ/CEQ handlers run in interrupt or tasklet context and must tolerate objects disappearing. `erdma_ceq_uninit_one` returns early without freeing EQ memory if destroy-EQ command fails, which avoids freeing active hardware memory but can leak during error removal. Bounded polling limits interrupt work but can leave pending events for later notifications.

## Test Signals
Signals include CQ completion interrupts across all vectors, CQ error and QP fatal event delivery, CEQ init partial-failure unwind, tasklet cleanup on module unload, EQ notification counters, and command failure injection for destroy-EQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_eq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_hw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_hw.h

## Purpose
Defines ERDMA hardware ABI constants, register offsets, doorbell layouts, command queue opcodes and request/response structures, WQE/CQE/EQE formats, capability masks, protocol enums, and status/opcode mappings.

## Important APIs, Types, And Functions
- PCI/register constants cover BARs, MSI-X vectors, device control/status, queue address/depth registers, stats registers, and doorbell spaces.
- Command queue definitions cover common and RDMA submodules, opcodes, command header masks, create/destroy EQ/CQ/QP/AH, MR registration, device config, MTU, GID, stats/query, and DB allocation requests.
- Queue formats include `erdma_cqe`, `erdma_sge`, `erdma_rqe`, send/write/read/atomic/reg-mr SQEs, AEQE/CEQE formats, opcodes, WC statuses, and vendor errors.

## Control Flow
The header has no executable flow, but every command submission and queue parser relies on these layouts. `erdma_cmdq.c`, `erdma_eq.c`, `erdma_cq.c`, `erdma_qp.c`, `erdma_main.c`, and verbs code build control flow around these masks and structures.

## State And Persistence Behavior
The defined structures are persistent hardware-visible state in coherent queues, BAR registers, and doorbell records. Owner bits, phase/index fields, WQEBB counts, command cookies, and queue depths form the ring protocols.

## Dependencies And Integration Points
Depends on Linux kernel types and Ethernet address size. It is the central hardware contract for the ERDMA module and must align with firmware.

## Risks
ABI drift is the core risk. Incorrect masks or endian annotations can corrupt WQEs/CQEs or decode capabilities incorrectly. Some masks pack queue sizes as logarithms while runtime fields use counts, so conversions must be tested. Doorbell offsets and vector indexing must align with BAR layout.

## Test Signals
Signals include successful probe capability decode, command queue operations, QP/CQ/EQ creation, all verbs WQE opcodes, CQE status mapping, GID/AH commands for RoCEv2, iWARP QP modify commands, and hardware stats queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_main.c

## Purpose
Owns ERDMA module init/exit, PCI probe/remove, BAR/IRQ/DMA-pool setup, command/event queue bring-up, capability discovery, device configuration, RDMA core registration, netdev association, resource allocator setup, and protocol-specific ops selection.

## Important APIs, Types, And Functions
- PCI/device setup: `erdma_probe_dev`, `erdma_remove_dev`, `erdma_device_init`, `erdma_request_vectors`, `erdma_comm_irq_init`, `erdma_wait_hw_init_done`, and `erdma_hw_reset`.
- RDMA registration: `erdma_dev_attrs_init`, `erdma_device_config`, `erdma_res_cb_init`, `erdma_ib_device_add`, `erdma_ib_device_remove`, and `erdma_device_register`.
- Netdev integration: `erdma_enum_and_get_netdev` and `erdma_netdev_event`.
- Module entry points: `erdma_init_module` initializes CM before PCI registration; `erdma_exit_module` unregisters PCI then exits CM.

## Control Flow
Probe enables PCI, allocates `struct erdma_dev`, requests BARs, maps function BAR, rejects nonfunctional functions with zero version, creates response and DB DMA pools, sets 64-bit DMA, allocates MSI-X vectors, requests the common IRQ, initializes AEQ and CMDQ, waits for hardware init done, initializes CEQs, and arms the command queue. RDMA add then queries capabilities and firmware info through CMDQ, optionally configures extended doorbells, selects iWARP or RoCEv2 ops, initializes xarrays/resources/workqueue, reads peer MAC, binds to matching netdev, registers the IB device, and registers a netdev notifier.

## State And Persistence Behavior
Persistent state includes BAR mapping, DMA pools, MSI-X vector count, common IRQ, AEQ/CMDQ/CEQs, device attributes, resource bitmaps, QP/CQ xarrays, CEP list, context count, peer netdev, MTU, and reflush workqueue. Netdev MTU changes are propagated via command-backed `erdma_set_mtu`.

## Dependencies And Integration Points
Integrates Linux PCI/MSI-X/DMA pools, RDMA core, netdevice notifier and EUI-48 GUID helpers, ERDMA command queue, EQ, CM, QP/CQ/verbs implementation, and protocol-specific iWARP/RoCEv2 ops.

## Risks
Probe unwind spans many hardware and RDMA resources; ordering must keep IRQs from observing freed queues. Netdev association relies on matching permanent MAC address and returns `-EPROBE_DEFER` until the peer netdev exists. Resource max values must be initialized before bitmap allocation. Common IRQ shares CMDQ and AEQ handling, so interrupt storms or stuck command queue can affect async events.

## Test Signals
Signals include probe deferral until netdev appears, clean load/unload, MTU change propagation, iWARP and RoCEv2 op registration, capability decode, extended DB config on capable devices, partial probe failure unwind, and PCI remove while RDMA objects are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_qp.c

## Purpose
Implements ERDMA QP state transitions and kernel post-send/post-recv paths. It covers iWARP LLP close/drop transitions, RoCEv2 modify/reset/error behavior, QP reference safety, SQE/RQE construction, doorbell ringing, inline/SGL handling, and reflush scheduling for kernel QPs.

## Important APIs, Types, And Functions
- QP state and lifetime: `erdma_qp_llp_close`, `erdma_get_ibqp`, `erdma_modify_qp_state_iwarp`, `erdma_modify_qp_state_rocev2`, `erdma_qp_get`, `erdma_qp_put`, and `erdma_qp_safe_free`.
- Modify helpers: `erdma_modify_qp_state_to_rts`, `erdma_modify_qp_state_to_stop`, `modify_qp_cmd_rocev2`, and `erdma_reset_qp`.
- Send path: `erdma_post_send`, `erdma_push_one_sqe`, `fill_inline_data`, `fill_sgl`, opcode-specific SQE initializers, and `kick_sq_db`.
- Receive path: `erdma_post_recv`, `erdma_post_recv_one`, and RQ doorbell writes.

## Control Flow
iWARP RTS transition validates LLP and MPA attributes, reads local/peer socket addresses and TCP sequence numbers, builds a modify-QP command, adjusts server send sequence for the MPA response, and stores ORD/IRD/CC. Stop/error transitions post modify-QP commands, drop CM state, and schedule reflush for kernel resources. RoCEv2 modify builds a protocol-specific command from attr masks, updates cached state/qkey/destination/AV, resets kernel queues on RESET, and schedules reflush on ERROR. Posting send locks the QP, checks SQ space, formats SQEs per opcode, updates WR ID tables, advances PI, and rings the SQ doorbell. Posting recv writes one zero-or-single-SGE RQE, updates the RQ WR ID table, advances PI, and rings the RQ doorbell.

## State And Persistence Behavior
Persistent QP state includes protocol state, CC, ORD/IRD, CM CEP pointer, kref/safe-free completion, SQ/RQ producer and consumer indices, WR ID tables, queue buffers, doorbell records, flags, and delayed reflush work. Reset clears queue buffers and removes pending CQEs for the QP.

## Dependencies And Integration Points
Depends on `erdma_cm.h`, `erdma_verbs.h`, command queue modify-QP opcodes, CQ cleanup, RDMA core WR formats, TCP socket state for iWARP, AH data for UD sends, MR data for REG_MR, and the device reflush workqueue.

## Risks
Send WQE formatting is dense and opcode-specific; wrong WQEBB counts or offsets corrupt later WQEs. `erdma_post_recv_one` accepts only 0 or 1 SGE and does not visibly check RQ fullness in this file. Atomic and RDMA read paths assume required SGE counts. CM/QP teardown races are mitigated with refs and locks but remain high-risk. Inline data copies from kernel virtual addresses and must respect `ERDMA_MAX_INLINE`.

## Test Signals
Signals include post-send for SEND, SEND_WITH_IMM/INV, RDMA read/write, write-with-imm, atomics, REG_MR, LOCAL_INV, inline sends, SQ full behavior, post-recv SGE validation, QP reset CQE cleanup, iWARP active/passive RTS, RoCEv2 state changes, and destroy during flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_qp.c -->
