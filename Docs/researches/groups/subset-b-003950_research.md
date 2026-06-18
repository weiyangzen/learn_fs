# subset-b-003950 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_verbs.c

## Purpose
`ocrdma_verbs.c` is the Emulex/Broadcom OCRDMA provider implementation for the Linux RDMA core. It exposes RoCE verbs for device and port queries, user-context mmap setup, protection domains, memory registration, CQs, QPs, SRQs, posting send/recv work requests, CQ polling/arming, and fast-registration MRs. It is the main translation layer between `ib_verbs` objects and OCRDMA mailbox/doorbell hardware state.

## Important APIs, Types, And Functions
The exported verbs include `ocrdma_query_device`, `ocrdma_query_port`, `ocrdma_query_pkey`, `ocrdma_alloc_ucontext`, `ocrdma_dealloc_ucontext`, `ocrdma_mmap`, `ocrdma_alloc_pd`, `ocrdma_dealloc_pd`, `ocrdma_get_dma_mr`, `ocrdma_reg_user_mr`, `ocrdma_dereg_mr`, `ocrdma_create_cq`, `ocrdma_resize_cq`, `ocrdma_destroy_cq`, `ocrdma_create_qp`, `ocrdma_modify_qp`, `ocrdma_query_qp`, `ocrdma_destroy_qp`, `ocrdma_create_srq`, `ocrdma_modify_srq`, `ocrdma_query_srq`, `ocrdma_destroy_srq`, `ocrdma_post_send`, `ocrdma_post_recv`, `ocrdma_post_srq_recv`, `ocrdma_poll_cq`, `ocrdma_arm_cq`, `ocrdma_alloc_mr`, and `ocrdma_map_mr_sg`.

Internal helpers manage mmap authorization (`ocrdma_add_mmap`, `ocrdma_del_mmap`, `ocrdma_search_mmap`), PD bitmap allocation, PBL sizing/allocation, WQE/RQE construction, QPN-to-QP mapping, CQE decoding, QP flush expansion, and SRQ tag allocation. Core state lives in driver objects from `ocrdma.h`: `ocrdma_dev`, `ocrdma_ucontext`, `ocrdma_pd`, `ocrdma_mr`, `ocrdma_cq`, `ocrdma_qp`, and `ocrdma_srq`.

## Control Flow
Device and port queries copy cached hardware attributes and netdev link state into RDMA core structures. User context allocation creates a coherent AH table, registers it in the per-context mmap allow-list, allocates a context PD, and returns ABI fields through `ib_copy_to_udata`. `ocrdma_mmap` only maps pages that were previously inserted into that allow-list, then chooses noncached doorbell, write-combined DPP, or normal remap behavior based on physical address ranges.

PD allocation first tries preallocated bitmap PD ranges when enabled, including DPP-capable PDs for user contexts on supported ASICs; otherwise it uses mailbox allocation. CQ/QP/SRQ creation validates RDMA core attributes, creates hardware resources through mailbox helpers, initializes locks and software queues, exposes user mmap pages when `udata` exists, and records lookup pointers in device tables. Teardown reverses those steps, synchronizes interrupts for CQs, moves QPs to error before destruction, removes QPN mappings under CQ locks, discards or flushes outstanding CQEs, and frees shadow WR tables.

The data path builds OCRDMA WQEs for send, send-with-imm/invalidate, RDMA read/write, local invalidate, and fast MR registration. It stores kernel WR IDs in shadow arrays, converts WQEs to little-endian, uses `wmb()` before ringing SQ/RQ/SRQ doorbells, and advances circular queue heads. CQ polling decodes hardware CQEs into `ib_wc`, updates SQ/RQ tails, handles UD/GSI flags, maps hardware status to `ib_wc_status`, and expands a single hardware error CQE into software flush completions for pending work.

## State And Persistence Behavior
State is volatile kernel/device state, not persistent storage. Important mutable state includes mmap allow-list entries per user context, PD bitmap counts and high-water marks, `dev->cq_tbl` and `dev->qp_tbl`, QP SQ/RQ head/tail indexes, SRQ bitmap tags, per-QP WR-ID shadows, CQ phase/get pointers, flush lists on CQs, and `dev->stag_arr` for fast-registration MRs. Locks are critical: `dev_lock` serializes PD/QP mailbox and state operations, `q_lock` protects QP queues, `cq_lock` protects CQ polling/destruction, `flush_q_lock` protects flush lists, and SRQ `q_lock` protects shared receive queue state.

## Dependencies And Integration Points
This file depends on the RDMA core (`ib_verbs`, `ucontext`, `umem`, `ib_sg_to_pages`, AH helpers), Linux DMA/mmap APIs, netdev state and MTU helpers, OCRDMA mailbox functions in `ocrdma_hw.*`, OCRDMA hardware layouts in `ocrdma_sli.h`, and ABI structs from `<rdma/ocrdma-abi.h>`. It integrates with userspace through uverbs responses and mmap offsets, and with hardware through mailbox commands, coherent DMA PBLs, queue memory, and MMIO doorbells.

## Risks And Test Signals
Primary risks are lifetime and ordering bugs around mmap allow-lists, PD reuse, QP destroy versus in-flight CQ polling, SRQ tag reuse, CQ phase handling, and error CQE expansion. `ocrdma_alloc_wr_id_tbl` leaks the first allocation if the second allocation fails before QP cleanup reaches the common path. `ocrdma_reg_user_mr` releases neither `mr->umem` nor PBLs on some early error paths after `ib_umem_get`, which is a resource-lifetime area to verify against surrounding kernel expectations. Test signals include RDMA core query/mmap tests, userspace PD/CQ/QP/SRQ create/destroy loops, rping/perftest UD/RC traffic, error-state QP flush tests, CQ shared SQ/RQ tests, SRQ receive reuse tests, fast-reg MR registration/invalidation, and fault injection for mailbox and DMA allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_verbs.h

## Purpose
`ocrdma_verbs.h` is the OCRDMA provider's verbs interface header. It declares the functions that `ocrdma_main.c` and the RDMA core operation table use to bind OCRDMA device objects to generic InfiniBand/RDMA verbs.

## Important APIs, Types, And Functions
The header declares posting APIs (`ocrdma_post_send`, `ocrdma_post_recv`, `ocrdma_post_srq_recv`), CQ APIs (`ocrdma_poll_cq`, `ocrdma_arm_cq`, `ocrdma_create_cq`, `ocrdma_resize_cq`, `ocrdma_destroy_cq`), query APIs (`ocrdma_query_device`, `ocrdma_query_port`, `ocrdma_query_protocol`, `ocrdma_query_pkey`), context and mmap APIs, PD APIs, QP APIs including `_ocrdma_modify_qp`, SRQ APIs, and MR APIs (`ocrdma_get_dma_mr`, `ocrdma_reg_user_mr`, `ocrdma_alloc_mr`, `ocrdma_map_mr_sg`, `ocrdma_dereg_mr`). It references RDMA core types such as `ib_qp`, `ib_cq`, `ib_wc`, `ib_udata`, `uverbs_attr_bundle`, `ib_mr`, and `scatterlist`.

## Control Flow
There is no executable control flow in this file. Its declarations define the call surface used by the driver's registration code and by other OCRDMA modules. The functions are implemented mostly in `ocrdma_verbs.c`, while `ocrdma_query_protocol` is expected from another OCRDMA source file.

## State And Persistence Behavior
The header stores no state. Its importance is contractual: prototype drift against RDMA core operation signatures or against `ocrdma_verbs.c` would break compilation or runtime operation registration.

## Dependencies And Integration Points
The file assumes `ocrdma_qp` and RDMA core types are already visible through included OCRDMA/RDMA headers in including translation units. It is integrated by the OCRDMA main provider setup that fills `ib_device_ops`, and it also exposes `ocrdma_del_flush_qp` for flush-list cleanup outside the core verbs implementation.

## Risks And Test Signals
Risks are API mismatch with evolving kernel RDMA signatures, missing include dependencies if the header is included from a narrower context, and stale declarations for functions implemented elsewhere. Test signals are successful kernel build with `CONFIG_INFINIBAND_OCRDMA`, sparse/C=1 prototype checks, and exercising every registered `ib_device_ops` entry through RDMA core smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Kconfig

## Purpose
`Kconfig` defines the build-time configuration symbol for the QLogic/FastLinQ QEDR RDMA driver. It lets kernel configuration select the low-level InfiniBand-over-Ethernet support for QED host channel adapters.

## Important APIs, Types, And Functions
The relevant symbol is `INFINIBAND_QEDR`, a tristate named "QLogic RoCE driver". It depends on `64BIT`, `QEDE`, and `PCI`, and selects `QED_LL2`, `QED_OOO`, and `QED_RDMA`.

## Control Flow
There is no runtime control flow. At configuration time, enabling this symbol causes the build system to compile the QEDR module or link it built-in according to tristate selection. The selected QED feature symbols ensure the lower-layer Ethernet/RDMA and LL2 interfaces used by `main.c`, `qedr_roce_cm.c`, and `qedr_iw_cm.c` are available.

## State And Persistence Behavior
The only state is kernel configuration state in `.config`. It persists across builds through normal kernel config mechanisms and controls whether `qedr.o` is built.

## Dependencies And Integration Points
The dependencies encode that QEDR is a PCI, 64-bit-only RDMA client layered on the `qede`/`qed` networking stack. The selected symbols match the driver's use of QED RDMA operations, LL2 packet paths for RoCE GSI, and out-of-order support.

## Risks And Test Signals
Risk is mostly configuration skew: missing selects would surface as unresolved QED symbols, while overly broad dependencies would offer the driver where the lower layer cannot provide RDMA services. Test signals include `olddefconfig` visibility checks, module build with `CONFIG_INFINIBAND_QEDR=m`, built-in build with `=y`, and dependency builds where `QEDE` or `PCI` are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Makefile

## Purpose
`Makefile` maps the `INFINIBAND_QEDR` kernel config symbol to the QEDR object and lists the translation units that compose the driver.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_INFINIBAND_QEDR) := qedr.o` and builds `qedr-y` from `main.o`, `verbs.o`, `qedr_roce_cm.o`, and `qedr_iw_cm.o`.

## Control Flow
There is no runtime control flow. Kbuild includes the listed objects into the composite `qedr.o` when the config symbol is enabled. This means the core registration/lifecycle code, generic verbs implementation, RoCE GSI connection-management path, and iWARP CM path are always compiled together for QEDR.

## State And Persistence Behavior
No runtime state exists. The file affects build graph state only.

## Dependencies And Integration Points
The file integrates with the kernel Kbuild system and the `Kconfig` symbol in the same directory. It assumes the object names correspond to local source files and that exported symbols between them are resolved inside the composite module.

## Risks And Test Signals
The main risks are omitting a required object or adding an object without matching source, causing unresolved symbols or missing operation implementations. Test signals are clean `M=drivers/infiniband/hw/qedr` builds and link-time coverage of symbols referenced from `main.c` device ops, especially verbs in `verbs.o` and CM callbacks in the two CM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/main.c

## Purpose
`main.c` is the QEDR driver's module entry, device lifecycle, RDMA core registration, interrupt setup, hardware start/stop, asynchronous event dispatch, and qede notification bridge. It turns a `qed_dev` plus `net_device` into an `ib_device` with either RoCE or iWARP operation extensions.

## Important APIs, Types, And Functions
It defines the common `qedr_dev_ops` `ib_device_ops` table, iWARP-specific ops (`iw_connect`, listen, accept/reject, QP ref hooks), and RoCE-specific ops (`query_pkey`, RoCE immutable port flags). Device lifecycle functions include `qedr_add`, `qedr_remove`, `qedr_open`, `qedr_close`, `qedr_shutdown`, and `qedr_notify`. Hardware/resource functions include `qedr_alloc_resources`, `qedr_free_resources`, `qedr_init_hw`, `qedr_stop_hw`, `qedr_setup_irqs`, `qedr_req_msix_irqs`, `qedr_irq_handler`, and `qedr_set_device_attr`.

## Control Flow
Module init registers a `qedr_driver` with qede. On add, the driver allocates an RDMA device, obtains QED RDMA ops, reads device info, rejects iWARP CMT unless lower-layer affinity allows it, determines CNQ count, sets PCI atomic capability, allocates SGID/CNQ/status-block resources, starts QED RDMA with CNQ PBLs and async callbacks, queries device attributes, requests MSI-X interrupts, registers the `ib_device`, and dispatches a port-active event. Remove unregisters the RDMA device first to stop clients, then stops QED RDMA, frees IRQs/resources, restores iWARP affinity if needed, and deallocates the RDMA device.

The IRQ handler disables the status block, reads hardware and software CNQ consumers, consumes CQ handles from the QED chain, validates CQ signatures, invokes RDMA completion handlers, increments `cnq_notif` after handlers finish to coordinate CQ destruction, updates the hardware producer, and re-enables interrupts. Affiliated async events translate QED RoCE/iWARP event codes into `ib_event` callbacks for CQs, QPs, or SRQs.

## State And Persistence Behavior
All state is runtime device state: CNQ arrays, status blocks, SGID table, xarrays for SRQs/QPs, iWARP workqueue, doorbell/DPI information, `enet_state`, GSI pointers, and cached capability attributes. `enet_state` prevents duplicate port-active/port-error events. No persistent on-disk state exists.

## Dependencies And Integration Points
This file depends on RDMA core registration and object-size macros, qede's RDMA driver registration API, QED RDMA/common ops, PCI/MSI-X, DMA coherent memory, QED chains/status blocks, netdev events, and helper functions from `verbs.c`, `qedr_iw_cm.c`, and `qedr_roce_cm.c`. It exports sysfs attributes `hw_rev` and `hca_type` through the RDMA device group.

## Risks And Test Signals
Risks center on lifecycle ordering: clients must be unregistered before hardware teardown, IRQ handlers must not race CQ destruction, and iWARP workqueue/QP references must be drained before resources disappear. `qedr_add` logs through `dev` after `ib_dealloc_device` in the failure path, which should be reviewed for use-after-free risk depending on macro expansion. Test signals include module load/unload loops, qede up/down/change-MTU/change-MAC notifications, MSI-X interrupt traffic under RDMA load, CQ destruction under interrupt pressure, RoCE and iWARP registration smoke tests, and fault injection for each staged add failure label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr.h

## Purpose
`qedr.h` is the central private header for the QEDR driver. It defines device, CQ, QP, SRQ, PD, MR, user-context, mmap, and iWARP endpoint state shared by `main.c`, verbs, RoCE CM, and iWARP CM.

## Important APIs, Types, And Functions
Key types are `qedr_dev`, `qedr_device_attr`, `qedr_cnq`, `qedr_ucontext`, `qedr_userq`, `qedr_cq`, `qedr_pd`, `qedr_xrcd`, `qedr_qp_hwq_info`, `qedr_srq_hwq_info`, `qedr_srq`, `qedr_qp`, `qedr_ah`, `qedr_mr`, `qedr_user_mmap_entry`, `qedr_iw_listener`, and `qedr_iw_ep`. Inline helpers convert RDMA core objects to driver objects and provide queue helpers such as `qedr_inc_sw_cons`, `qedr_inc_sw_prod`, `qedr_qp_has_srq`, `qedr_qp_has_sq`, and `qedr_qp_has_rq`.

## Control Flow
The file has minimal executable flow through inline helpers. `qedr_get_dmac` validates a nonzero GRH destination GID and retrieves the resolved destination MAC from an AH. Queue helpers update circular producer/consumer indexes. Container helpers are used throughout operation tables to recover private objects from embedded RDMA core objects.

## State And Persistence Behavior
The structs describe all volatile QEDR runtime state. `qedr_dev` owns lower-layer handles, interrupt resources, doorbell/DPI mappings, SGID table, GSI QP/CQ references, xarrays, and iWARP workqueue. `qedr_qp` owns hardware queues, shadows for SQ/RQ WR IDs, RDMA state, PSNs, QED QP handles, and iWARP kref/completion state. User objects track umem, PBLs, mmap entries, and doorbell recovery metadata. There is no persistent storage.

## Dependencies And Integration Points
The header includes Linux PCI/xarray/completion, RDMA address helpers, QED public interfaces, QED chains, qede RDMA integration, RoCE common definitions, and local HSI layouts. It is the structural contract between QEDR source files and the lower-layer QED firmware interface.

## Risks And Test Signals
Because many objects embed RDMA core structs, layout assumptions are important; `struct qedr_qp` explicitly requires `ib_qp` first. Queue counters mix hardware chain indexes, software producers/consumers, and GSI-specific consumers, so wraparound bugs are a key risk. The header also centralizes reference-counted iWARP endpoint fields; incorrect ownership in users can leak or prematurely release QPs. Test signals include build coverage for all object-size registrations, lockdep/KASAN during object create/destroy stress, GSI traffic for `gsi_cons`, iWARP connect/disconnect refcount stress, and mmap/doorbell recovery tests for user contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_hsi_rdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_hsi_rdma.h

## Purpose
`qedr_hsi_rdma.h` defines host-side interface layouts for QED RDMA firmware queues. It is a hardware contract header for CNQ elements, CQEs, SQ/RQ/SRQ WQEs, doorbell payloads, status enums, and DIF metadata used by the QEDR verbs implementation.

## Important APIs, Types, And Functions
Important layouts include `rdma_cnqe`, `rdma_cqe_responder`, `rdma_cqe_requester`, `rdma_cqe_common`, `union rdma_cqe`, `rdma_sq_sge`, `rdma_rq_sge`, `rdma_srq_wqe_header`, `rdma_srq_sge`, `union rdma_srq_elm`, `rdma_pwm_val16_data`, `rdma_pwm_val32_data`, `rdma_dif_params`, and WQE structs for atomic, bind, common, FMR, local invalidate, RDMA, and send operations. Enums cover requester/responder CQE status, CQE type, DIF options, and SQ request type.

## Control Flow
There is no runtime control flow. The bit masks and shifts are consumed by code that builds WQEs, rings doorbells, and decodes CQEs. The split "1st/2nd/3rd" WQE structs document 16-byte element boundaries used by hardware chains.

## State And Persistence Behavior
The file stores no live state, but it defines the in-memory DMA-visible state exchanged with firmware. Endianness annotations (`__le16`, `__le32`) are part of the contract and callers must use CPU-to-little-endian conversions correctly.

## Dependencies And Integration Points
The header depends on `<linux/qed/rdma_common.h>` for `regpair` and shared RDMA constants. It is included by `qedr.h`, making the layouts available to QEDR queue structs and verbs code. Firmware compatibility depends on these definitions matching the QED HSI version used by the lower-layer driver.

## Risks And Test Signals
Risks are ABI/firmware layout drift, incorrect bitfield shifts, missing endian conversion, and misuse of the max enum values as real statuses. Because these structs map DMA data, padding or compiler layout changes would be serious; the use of fixed-size fields helps but should be guarded by build-time layout checks where available. Test signals are successful RDMA traffic across every opcode class, CQE error/status injection, doorbell operation, fast MR/FMR operations, and cross-version testing with supported QED firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_hsi_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.c

## Purpose
`qedr_iw_cm.c` implements QEDR's iWARP connection-management glue between Linux `iw_cm` and QED firmware. It handles active connects, passive listens, accept/reject, MPA events, address/VLAN/MAC resolution, iWARP QP reference management, and asynchronous disconnect/close/error events.

## Important APIs, Types, And Functions
The exported RDMA core callbacks are `qedr_iw_connect`, `qedr_iw_create_listen`, `qedr_iw_destroy_listen`, `qedr_iw_accept`, `qedr_iw_reject`, `qedr_iw_qp_add_ref`, `qedr_iw_qp_rem_ref`, and `qedr_iw_get_qp`. Internal callbacks include `qedr_iw_event_handler`, `qedr_iw_mpa_request`, `qedr_iw_active_complete`, `qedr_iw_passive_complete`, `qedr_iw_disconnect_event`, `qedr_iw_disconnect_worker`, `qedr_iw_close_event`, and `qedr_iw_qp_event`.

## Control Flow
For active connect, the code validates ports, allocates an endpoint, loads and references the QP from `dev->qps`, references the `iw_cm_id`, fills QED CM info from IPv4 or IPv6 socket addresses, resolves VLAN and neighbor MAC, computes MSS from the initial iWARP MTU, sets private data/ORD/IRD/QP fields, sets a wait-for-connect bit, and calls `iwarp_connect`. Passive listen allocates a listener, references the CM ID, fills listen parameters from local address and VLAN, and calls `iwarp_create_listen`. MPA request allocates an endpoint and reports `IW_CM_EVENT_CONNECT_REQUEST` with provider data. Accept attaches a QP to that endpoint and calls `iwarp_accept`; reject sends `iwarp_reject` with no QP.

Firmware events are translated into iw_cm or ib_qp events. Active/passive complete signals `qp->iwarp_cm_comp` and sends established/connect-reply events. Disconnect is deferred to `dev->iwarp_wq` because it modifies QP state and calls the upper CM event handler outside atomic callback context. Close drops the endpoint reference. Fatal QP events become `IB_EVENT_QP_FATAL` or `IB_EVENT_QP_ACCESS_ERR`.

## State And Persistence Behavior
State is held in `qedr_iw_ep`, `qedr_iw_listener`, QP krefs/completions, CM ID references, and the `dev->qps` xarray. Endpoint krefs own QP and CM ID references until close or failure. Bits in `qp->iwarp_cm_flags` prevent duplicate connect/disconnect transitions. There is no persistent state.

## Dependencies And Integration Points
The file depends on Linux IPv4/IPv6 route and neighbor APIs, VLAN helper APIs, `iw_cm`, QED iWARP operations, and QEDR private QP/device state. It is registered from `main.c` only for iWARP devices.

## Risks And Test Signals
Risks include refcount imbalance across active failure, passive reject, disconnect work, and close ordering; stale neighbor entries causing unresolved MACs while returning success; address-family corner cases when IPv6 is disabled; and races between QP destruction and CM callbacks. Test signals include active/passive iWARP connection tests for IPv4 and IPv6, private-data propagation, accept/reject paths, listener teardown under pending connects, disconnect while QP destroy waits on completions, route-neighbor miss behavior, VLAN interfaces, and lockdep/KASAN refcount stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.h

## Purpose
`qedr_iw_cm.h` declares QEDR iWARP connection-management callbacks that `main.c` installs into `ib_device_ops`.

## Important APIs, Types, And Functions
It exposes active/passive CM functions (`qedr_iw_connect`, `qedr_iw_create_listen`, `qedr_iw_destroy_listen`, `qedr_iw_accept`, `qedr_iw_reject`) and QP reference/lookup hooks (`qedr_iw_qp_add_ref`, `qedr_iw_qp_rem_ref`, `qedr_iw_get_qp`). It includes `<rdma/iw_cm.h>` for `iw_cm_id` and `iw_cm_conn_param`.

## Control Flow
No executable control flow exists. The declarations are consumed by QEDR device registration so the RDMA core can call into `qedr_iw_cm.c` for iWARP devices.

## State And Persistence Behavior
The header stores no state. It defines the cross-file function contract for CM ID and QP lifetime operations.

## Dependencies And Integration Points
It integrates `main.c` with `qedr_iw_cm.c`, and indirectly with the RDMA iWARP CM core. The header has no include guard in the inspected file, so repeated inclusion would rely on compiler tolerance for duplicate prototypes rather than preprocessor protection.

## Risks And Test Signals
Risks are prototype drift and the missing include guard. Test signals include clean builds with warnings enabled, `CONFIG_INFINIBAND_QEDR` iWARP registration, and RDMA core invoking each installed iWARP callback during connection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.c

## Purpose
`qedr_roce_cm.c` implements the RoCE GSI/QP1 path for QEDR using the QED LL2 interface. It creates and destroys the special GSI QP, builds UD/RoCE packet headers, posts receive buffers through LL2, transmits send WRs through LL2, and synthesizes CQ completions for GSI traffic.

## Important APIs, Types, And Functions
Exported functions are `qedr_inc_sw_gsi_cons`, `qedr_store_gsi_qp_cq`, `qedr_create_gsi_qp`, `qedr_destroy_gsi_qp`, `qedr_gsi_post_send`, `qedr_gsi_post_recv`, and `qedr_gsi_poll_cq`. Internal LL2 callbacks are `qedr_ll2_complete_tx_packet`, `qedr_ll2_complete_rx_packet`, and `qedr_ll2_release_rx_packet`. Internal helpers include `qedr_ll2_start`, `qedr_ll2_stop`, `qedr_ll2_post_tx`, `qedr_gsi_build_header`, and `qedr_gsi_build_packet`.

## Control Flow
Creating a GSI QP validates max WR/SGE limits, starts an LL2 RoCE connection with RX/TX callbacks and MAC filter, assigns QP number 1, allocates SQ/RQ shadow arrays, stores global GSI QP/CQ pointers, records the MAC address, destroys the firmware CQs because GSI completions are driver-synthesized, and marks the receive CQ as `QEDR_CQ_TYPE_GSI`. Destroying stops LL2, removes the MAC filter, terminates and releases the LL2 connection.

Posting send accepts only one `IB_WR_SEND` at a time and only in RTS. It builds an Ethernet/VLAN/GRH-or-IP/UDP/BTH/DETH header based on SGID type, packs it into coherent DMA memory, attaches payload SGEs by DMA address, posts it to LL2, records the WR ID, and advances SQ producer. TX completion frees header DMA memory and packet metadata, advances `gsi_cons`, and calls the CQ completion handler. Posting receive accepts only one receive SGE per WR, posts the buffer to LL2, stores the WR ID and SGE, and advances RQ producer. RX completion records status, VLAN, payload length, source MAC, advances RQ `gsi_cons`, and signals the CQ. Polling first drains RX completions into receive WCs with GRH, checksum, SMAC, and optional VLAN flags, then drains TX completions as send WCs.

## State And Persistence Behavior
State is runtime-only: `dev->gsi_ll2_handle`, `gsi_qp_created`, `gsi_sqcq`, `gsi_rqcq`, `gsi_qp`, `gsi_ll2_mac_address`, QP SQ/RQ producers/consumers/GSI consumers, and shadow WR arrays. Packet header DMA allocations persist from post-send until LL2 TX completion or release callback.

## Dependencies And Integration Points
The file depends on RDMA UD header helpers, `ib_cache` GID attributes, net/IP/IPv6/UDP headers, Linux DMA APIs, QED LL2 operations, QED RoCE packet structs, QEDR AH/QP/CQ state, and RoCE constants. It integrates with verbs QP creation for `IB_QPT_GSI` and with MAC-change notification in `main.c`, which updates the LL2 filter and GID event.

## Risks And Test Signals
Risks include GSI global pointer lifetime during destroy, partial LL2 TX failures where payload posting fails after header posting, unchecked receive WR with zero SGEs despite later using `sg_list[0]`, single-WR send limitation surprises, and header correctness for VLAN/RoCEv1/RoCEv2 IPv4/IPv6. Test signals include SA/CM traffic over QP1, RoCE v1 and v2 IPv4/IPv6 GID types, VLAN-tagged GSI traffic, MAC address changes, LL2 start/stop failure injection, send completion memory leak checks, and CQ polling order with concurrent RX/TX completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.h

## Purpose
`qedr_roce_cm.h` declares the QEDR RoCE GSI connection-management and special-QP helper interface used by the verbs implementation and QEDR main logic.

## Important APIs, Types, And Functions
It defines GSI limits (`QEDR_GSI_MAX_RECV_WR`, `QEDR_GSI_MAX_SEND_WR`, `QEDR_GSI_MAX_RECV_SGE`), RoCEv2 UDP source port constant `QEDR_ROCE_V2_UDP_SPORT`, helper `qedr_get_ipv4_from_gid`, and prototypes for GSI poll/post/create/destroy/store functions.

## Control Flow
Only `qedr_get_ipv4_from_gid` has executable behavior: it reads the IPv4 address bytes from the last four bytes of an IPv4-mapped GID. The rest of the header provides declarations consumed by `qedr_roce_cm.c` and verbs code.

## State And Persistence Behavior
The header has no state. Constants define resource limits enforced during GSI QP creation and receive posting.

## Dependencies And Integration Points
The prototypes reference RDMA core CQ/QP/WR types and QEDR private device/QP/CQ types from including files. The header has an include guard and is the contract between GSI-special handling and the generic QEDR verbs implementation.

## Risks And Test Signals
Risks include unaligned or aliasing-sensitive access in `qedr_get_ipv4_from_gid`, stale GSI limits versus LL2 firmware capability, and prototype drift. Test signals include builds with strict warnings, RoCEv2 IPv4 GID send tests, and GSI QP creation tests at boundary WR/SGE values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.h -->
