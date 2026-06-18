# Research: subset-b-005254

Grouped research report for the EFCT Fibre Channel target/HW path under `sources/distributed-fs/ceph-client/drivers/scsi/elx/efct`. Each source file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw.c

## Purpose
`efct_hw.c` is the main hardware abstraction for the EFCT SLI-4 Fibre Channel adapter. It initializes the SLI port, configures receive filters, owns mailbox command submission, manages hardware IO/XRI objects, submits target WQEs, processes queue completions, sends ELS/CT/BLS/send-frame traffic, exposes link/host statistics, writes firmware objects, controls link state, and tears the hardware down or resets it.

## Important APIs, Types, and Functions
The exported setup/lifecycle calls are `efct_hw_setup`, `efct_hw_init`, `efct_hw_teardown`, and `efct_hw_reset`. Link identity and filter helpers are `efct_hw_parse_filter`, `efct_get_wwnn`, and `efct_get_wwpn`. RX-buffer lifecycle is `efct_hw_rx_allocate`, `efct_hw_rx_post`, and `efct_hw_rx_free`. Mailbox command APIs are `efct_hw_command` and `efct_issue_mbox_rqst`, backed by `efct_hw_command_process`, `efct_hw_mq_process`, and `efct_hw_command_cancel`.

IO-facing exports include `efct_hw_io_alloc`, `efct_hw_io_free`, `efct_hw_io_lookup`, `efct_hw_io_init_sges`, `efct_hw_io_add_sge`, `efct_hw_io_send`, `efct_hw_io_abort`, and `efct_hw_io_abort_all`. Completion dispatch is centered on `efct_hw_process`, `efct_hw_eq_process`, `efct_hw_cq_process`, `efct_hw_wq_process`, and `efct_hw_xabt_process`. Request-tag management uses `efct_hw_reqtag_pool_alloc`, `efct_hw_reqtag_alloc`, `efct_hw_reqtag_free`, and `efct_hw_reqtag_get_instance`. Fabric/discovery send helpers are `efct_els_hw_srrs_send`, `efct_efc_bls_send`, `efct_hw_bls_send`, and `efct_hw_send_frame`.

## Control Flow
`efct_hw_setup` zeroes and initializes `struct efct_hw`, creates mailbox context mempools, initializes IO lists and locks, calls `sli_setup`, registers the SLI link callback, sizes queues, derives `n_io` from XRI resources, sets `n_eq` from CPU count, and reads dump sizing. `efct_hw_init` validates that command queues are empty, frees stale RX buffers, clears IO lists left by reset, initializes SLI, optionally enables health check/FDT hint, creates queues through `efct_hw_init_queues`, maps WQs to CPUs, allocates/posts RQ buffers, registers FCFI/MRQ filters, allocates request tags, sets up and initializes hardware IO objects, allocates loop-map DMA, arms EQ/CQ queues, builds queue hashes, marks state active, and reserves a send-frame IO.

Runtime interrupts enter `efct_hw_process`, select an EQ, and call `efct_hw_eq_process`. EQ entries identify CQs; CQ processing parses async, mailbox, WQ, WQ release, RQ, and XABT completions. WQ completions use the request tag to call the registered callback. RQ completions are delegated to queue code and then to `efct_unsolicited_cb`. XABT completions clear `xbusy`, invoke any latched internal-abort callback, and move wait-free XRIs back to free state.

Target data WQEs flow through `efct_hw_io_send`: format TRECEIVE, TSEND, or TRSP WQEs, set continuation when the XRI is already busy, mark `xbusy`, update WQ stats, and submit through `efct_hw_wq_write`. Abort flow takes a ref on the target HIO, atomically sets `abort_in_progress`, allocates an abort request tag, either marks a pending WQE for later abort submission or emits an abort WQE immediately, and completes in `efct_hw_wq_process_abort`.

## State and Persistence Behavior
All state is in-kernel and volatile. Persistent device identity comes from SLI/FW WWNN/WWPN, but this file does not persist configuration to disk. Hardware state is tracked by `hw->state`, command lists (`cmd_head`, `cmd_pending`), IO lists (`io_free`, `io_inuse`, `io_wait_free`), `xbusy`, callback request tags, queue hashes, DMA buffers, counters, and link state. Mailbox commands are serialized by `bmbx_lock` for polling and `cmd_lock` for async MQ queuing. IO free behavior is refcount based; an IO whose exchange is still busy moves to `WAIT_FREE` until an XABT completion returns the XRI.

## Dependencies and Integration Points
The file depends heavily on `../libefc_sli/sli4.h` and SLI helpers for queue allocation, mailbox formats, WQE formatting, CQ parsing, and link events. It integrates upward with `efc_domain_cb`, `efc_disc_io_complete`, `efct_unsolicited_cb`, and EFC discovery mailbox callbacks. It also depends on Linux PCI DMA APIs, mempools, spinlocks, mutexes, atomics, krefs, and FC frame definitions.

## Risks
Important risks are ordering and lifetime bugs: WQ completions can arrive while submission paths are still unwinding, so callbacks are cleared before invocation and lists are updated under locks. Abort paths are subtle because pending WQEs, internal aborts, saved status, XABT completions, and WQ callback tags all share one HIO. RX buffer allocation failure can leak already allocated per-buffer DMA because `efct_hw_rx_buffer_alloc` frees only the array on mid-loop failure. Request-tag pool allocation can partially allocate and return a smaller live pool without explicit failure cleanup. `efct_hw_io_lookup` assumes the XRI is within the first base range and does not bounds-check the computed index. Teardown must be tested under active mailbox, WQ, RQ, and reset conditions because it destroys DMA, queues, IOs, mempools, and tags.

## Test Signals
Useful tests include link-up/link-down domain callbacks, loop topology `READ_TOPOLOGY`, FCFI/MRQ registration, queue arming and CQ/EQ processing under load, target read/write/response WQE success and error completions, XRI abort races, WQ full/pending-list drain, RQ buffer consume/repost, mailbox queue saturation, stats read/reset callbacks, firmware write callback status, and reset/teardown with outstanding commands. Fault injection should cover DMA allocation failure, request-tag exhaustion, SLI command failure, local reject with XB set, and invalid RQ/CQ/WQ IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw.h

## Purpose
`efct_hw.h` defines the public hardware-layer contract used by the EFCT transport, SCSI, unsolicited-frame, and EFC discovery layers. It declares PCI IDs, queue sizing limits, HW IO types/states, mailbox command options, link/stat enums, queue wrapper structures, request-tag objects, hardware configuration/state containers, and all exported hardware APIs.

## Important APIs, Types, and Functions
Core types are `struct efct_hw`, `struct efct_hw_io`, `struct efct_hw_config`, `struct efct_command_ctx`, `struct reqtag_pool`, `struct hw_eq`, `struct hw_cq`, `struct hw_mq`, `struct hw_wq`, and `struct hw_rq`. `struct efct_hw_io` holds the HW exchange/XRI state, WQE buffer, callback pointers, abort state, request tag, WQ assignment, SGL DMA, continuation state, saved completion status, and refcount. `struct efct_hw` aggregates SLI state, queue arrays and wrapper pointers, queue hashes, command queues, IO lists, DMA pools, counters, and request-tag pool.

The header exports setup/init/teardown/reset, RX allocation/post/free, mailbox command submission, HW IO allocation/free/send/abort/SGL setup, completion processing, request-tag allocation, RQ sequence free, BLS/ELS/send-frame helpers, statistics APIs, firmware write, async NOP calls, and queue construction/destruction helpers.

## Control Flow
The header reflects a layered control model. Callers first use `efct_hw_setup`, `efct_hw_init`, and `efct_hw_port_control` to configure the adapter. Interrupt handlers call `efct_hw_process`, which dispatches EQ/CQ/WQ/RQ/XABT handlers. SCSI and discovery users allocate `struct efct_hw_io`, build SGLs, submit WQEs through `efct_hw_io_send` or protocol-specific helpers, and receive completion through `efct_hw_done_t`.

## State and Persistence Behavior
No data is persisted by the header. State exists in the `struct efct_hw` graph and is reset across driver detach/reset. Queue and IO state are explicitly modeled by enum values, list heads, DMA descriptors, counters, atomics, and hashes. Refcounted IO lifetime is exposed through `efct_hw_io_free_internal`.

## Dependencies and Integration Points
The header includes SLI-4 definitions from `../libefc_sli/sli4.h` and references EFC/EFCT types from the wider driver. It is included by HW implementation files, SCSI dispatch, unsolicited frame handling, xport lifecycle, and target glue. Because the structs are public within the driver, changes to layout or semantics affect most EFCT files.

## Risks
`struct efct_hw` exposes many mutable fields directly, so invariants are distributed across implementation files rather than encapsulated. Queue count constants must stay consistent with firmware/SLI limits. Request tags are 16-bit and indexed directly. `efct_hw_io_lookup` users rely on XRI/resource base assumptions. Any change to `struct efct_hw_io` lifetime fields, SGL fields, or callback fields can break abort and completion races.

## Test Signals
Compile coverage should catch most signature mismatches. Runtime validation should assert queue counts, WQ/RQ/CQ hash lookup, IO state transitions, request tag allocation/free symmetry, and correct linkage between SCSI-layer flags and HW IO/WQ steering fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw_queues.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw_queues.c

## Purpose
`efct_hw_queues.c` builds and tears down SLI queue topology for EFCT. It creates EQ, CQ, MQ, WQ, and RQ-pair objects, maps WQs to CPU interrupt affinities, tracks RQ buffer ownership, processes RQ completions, and reposts consumed receive buffer pairs.

## Important APIs, Types, and Functions
Top-level exports are `efct_hw_init_queues`, `efct_hw_map_wq_cpu`, queue constructors (`efct_hw_new_eq`, `efct_hw_new_cq`, `efct_hw_new_cq_set`, `efct_hw_new_mq`, `efct_hw_new_wq`, `efct_hw_new_rq_set`), destructors (`efct_hw_del_eq`, `efct_hw_del_cq`, `efct_hw_del_mq`, `efct_hw_del_wq`, `efct_hw_del_rq`, `efct_hw_queue_teardown`), and RQ helpers (`efct_hw_rqpair_process_rq`, `efct_hw_rqpair_sequence_free`, `efct_efc_hw_sequence_free`). Internal helpers `efct_hw_rqpair_find`, `efct_hw_rqpair_get`, and `efct_hw_rqpair_put` manage RQ tracker state.

## Control Flow
`efct_hw_init_queues` resets queue counters, initializes the EQ list, creates one EQ per configured vector, creates a single MQ on the first EQ, creates one WQ per EQ, allocates a CQ set for RQs, and allocates an RQ-pair set. Each RQ object owns a header queue and a data queue, plus an `rq_tracker` indexed by ring position. All RQs are marked MRQ with the first RQ header ID as the base MRQ ID.

RQ completion flow starts in HW CQ processing and enters `efct_hw_rqpair_process_rq`. It parses RQ ID/index/status, handles buffer length/DMA errors by retrieving and reposting the consumed buffer, finds the RQ wrapper through the RQ hash and lookup table, removes the `struct efc_hw_sequence` from `rq_tracker`, fills lengths/fcfi/EQ private pointer, and calls `efct_unsolicited_cb`. Freeing a sequence posts payload then header DMA addresses back to the paired RQ and restores the tracker entry.

## State and Persistence Behavior
Queue topology is volatile driver state under `struct efct_hw`. Queue wrapper objects are heap allocated and linked into EQ/CQ lists. RQ state persists while hardware is active through `rq_tracker`, which is protected by the header RQ lock and must mirror what was posted to firmware. `wq_cpu_array` maps Linux CPUs to WQs based on PCI IRQ affinity.

## Dependencies and Integration Points
The file depends on SLI queue allocation APIs (`sli_queue_alloc`, `sli_cq_alloc_set`, `sli_fc_rq_set_alloc`, `sli_rq_write`), PCI IRQ affinity, EFC unsolicited callback dispatch, and the shared queue hash helpers in `efct_hw.c`. It is called by `efct_hw_init` and `efct_hw_teardown`.

## Risks
Queue allocation failure paths free wrapper objects but rely on later teardown/free calls for SLI queue resources in some cases. `efct_hw_new_mq` stores `entry_size = EFCT_HW_MQ_DEPTH` instead of an explicit MQ entry byte size, which is worth checking against SLI expectations. `efct_hw_map_wq_cpu` leaves CPUs unmapped if affinity masks are unavailable; HW allocation falls back to WQ 0. RQ tracker corruption causes dropped frames or double-posted buffers. Error cases in RQ processing need careful buffer reposting to avoid RQ starvation.

## Test Signals
Tests should validate queue counts for one and multiple EQs, CQ-set/RQ-set allocation, CPU-to-WQ mapping with missing affinity, RQ completion/repost parity, RQ error status handling, queue teardown after partial allocation, and unsolicited frame dispatch after RQ processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw_queues.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.c

## Purpose
`efct_io.c` manages the software SCSI IO pool used above the HW XRI pool. It preallocates `struct efct_io` objects, response DMA buffers, and SGL arrays, hands IOs to the SCSI target path, returns them to a freelist, and finds active target IOs by FC exchange IDs for ABTS/TMF handling.

## Important APIs, Types, and Functions
`struct efct_io_pool` contains the owning `struct efct`, a spinlock, a fixed array of up to `EFCT_NUM_SCSI_IOS`, and a freelist. Public functions are `efct_io_pool_create`, `efct_io_pool_free`, `efct_io_pool_allocated`, `efct_io_pool_io_alloc`, `efct_io_pool_io_free`, and `efct_io_find_tgt_io`.

## Control Flow
Pool creation allocates the pool, initializes its freelist/lock, then loops over `EFCT_NUM_SCSI_IOS`, allocating one `struct efct_io`, a coherent response buffer sized for FCP response plus sense data, and a software SGL array sized by HW capability. Each IO is tagged by index and added to the freelist. Allocation removes the first freelist entry under lock, resets per-command fields, assigns EFCT context, and increments active/total allocation counters. Freeing removes any associated HW IO after the software IO is returned to the freelist and updates active/free counters. `efct_io_find_tgt_io` scans a node's active IO list for matching OX_ID and optional RX_ID and takes a kref before returning.

## State and Persistence Behavior
The IO pool is volatile memory owned by `efct->xport->io_pool`. Per-IO response DMA and SGL allocations persist across individual commands until pool free. Per-command fields are reset on allocation, while the allocated buffers and tag/index remain stable. Active IO membership is not managed by this file except through `efct_io_find_tgt_io`; SCSI allocation/free add/remove active node list entries.

## Dependencies and Integration Points
This file depends on `efct_hw_io_free` for returning associated HW exchanges, Linux DMA coherent allocation, spinlocks, and node active IO lists. It is created by `efct_xport_attach`, used by `efct_scsi_io_alloc` and abort helper allocation, and freed by xport shutdown.

## Risks
Partial pool creation can silently create fewer than `EFCT_NUM_SCSI_IOS` IOs if `kzalloc_obj` fails, but callers may assume the configured pool size. A failed SGL allocation calls `efct_io_pool_free`, which expects prior DMA fields to be valid. Returning the software IO to the freelist before freeing the associated HIO creates a window where the IO object is visible as free while HW cleanup is still happening, although the lock protects list state. `efct_io_find_tgt_io` relies on active list and kref discipline from `efct_scsi.c`.

## Test Signals
Validate pool creation/free under allocation failures, DMA buffer lifetime, allocation/free counter symmetry, HIO release on software IO free, ABTS lookup by OX_ID and wildcard/specific RX_ID, and behavior when pool exhaustion occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.h

## Purpose
`efct_io.h` defines the software IO object shared by unsolicited frame handling, SCSI target dispatch, LIO target glue, and HW submission. It also declares the IO pool APIs and target IO lookup helper.

## Important APIs, Types, and Functions
Key constants are `SCSI_CMD_BUF_LENGTH`, `SCSI_RSP_BUF_LENGTH`, and `EFCT_NUM_SCSI_IOS`. `enum efct_io_type` distinguishes SCSI IO, ELS, CT, BLS response, and abort software objects. `enum efct_els_state` tracks ELS request/abort states. `struct efct_io` is the central per-command object: it contains EFCT/node pointers, active/pending list links, kref, FC tags, software SGL, LIO private target IO, expected/transferred lengths, HW IO pointer, callback state, flags for target/initiator/abort behavior, HW IO parameters, response buffer DMA, timeout, priority, and app ID. `struct efct_io_cb_arg` carries generic completion status. Declared functions create/free pools, allocate/free IOs, count allocated entries, and find target IOs.

## Control Flow
Callers allocate `struct efct_io` from `efct_io_pool_io_alloc`, fill FC/SCSI/LIO fields, optionally associate a `struct efct_hw_io`, submit through `efct_scsi_io_dispatch`, then complete through SCSI/LIO callbacks and finally call `efct_scsi_io_complete` or pool free paths.

## State and Persistence Behavior
`struct efct_io` is reused across commands. Its DMA response buffer and SGL allocation persist for the lifetime of the pool, while command-specific fields must be reset before use. Krefs protect active command lifetime. The `io_free` flag is a defensive marker used to detect duplicate completion/free.

## Dependencies and Integration Points
The header includes `efct_lio.h`, which in turn includes SCSI target definitions. It references `efct_hw_io`, `efct_node`, `efct_scsi_sgl`, `efct_scsi_tgt_io`, and callback typedefs from the SCSI target layer. The dependency direction makes this file part of the tight SCSI/LIO/HW coupling.

## Risks
Because `struct efct_io` carries state for multiple protocols and phases, stale fields are a major risk if allocation reset misses a field. Including `efct_lio.h` from this generic IO header creates circular conceptual coupling. `EFCT_NUM_SCSI_IOS` is fixed at 8192 and can diverge from HW `n_io` if not considered by users.

## Test Signals
Compile tests should catch callback/type mismatches. Runtime checks should verify allocation reset coverage, response buffer sizing, SGL bounds, refcount transitions, duplicate-free detection, and IO reuse after abort or error completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.c

## Purpose
`efct_lio.c` binds EFCT Fibre Channel target IOs to Linux target core (LIO). It implements configfs fabric templates for physical and NPIV EFCT fabrics, creates/destroys target portal groups, handles initiator session setup/removal, translates FCP commands and TMFs into `se_cmd`/TMR submissions, maps target-core scatterlists to EFCT SGLs, drives read/write/status/TMF responses, and handles abort/free callbacks.

## Important APIs, Types, and Functions
Configuration helpers include WWN formatting/parsing, TPG enable attributes, NPIV enable handling, TPG attribute macros, and fabric operations tables `efct_lio_ops` and `efct_lio_npiv_ops`. Nport/TPG lifecycle is implemented by `efct_lio_make_nport`, `efct_lio_drop_nport`, `efct_lio_npiv_make_nport`, `efct_lio_npiv_drop_nport`, `efct_lio_make_tpg`, `efct_lio_drop_tpg`, `efct_lio_npiv_make_tpg`, and `efct_lio_npiv_drop_tpg`.

Session management is `efct_session_cb`, `efct_lio_setup_session`, `efct_scsi_new_initiator`, `efct_lio_remove_session`, and `efct_scsi_del_initiator`. Target device lifecycle is `efct_scsi_tgt_new_device`, `efct_scsi_tgt_del_device`, `efct_scsi_tgt_new_nport`, and `efct_scsi_tgt_del_nport`. IO datapath functions are `efct_scsi_recv_cmd`, `efct_scsi_recv_tmf`, `efct_lio_write_pending`, `efct_lio_queue_data_in`, `efct_lio_queue_status`, `efct_lio_queue_tm_rsp`, `efct_lio_datamove_done`, `efct_lio_send_resp`, and `efct_lio_status_done`.

## Control Flow
Driver init registers two target-core fabric templates: `efct` for the physical port and `efct_npiv` for NPIV. Configfs creates WWNs and TPGs; enabling a physical TPG brings the xport online, while enabling an NPIV TPG creates or requests a vport. When the EFC layer discovers an initiator, `efct_scsi_new_initiator` queues ordered work. The work selects a vport TPG if applicable, otherwise the physical TPG, calls `target_setup_session`, creates an `efct_node`, stores it in `efct->lookup` keyed by port FCID and initiator FCID, completes EFC registration, and adjusts IO watermarks.

Incoming FCP commands arrive from `efct_unsol.c` through `efct_scsi_recv_cmd`. This clears `tgt_io`, records state, increments `ios_in_use`, maps FCP task attributes and data direction to target-core values, initializes `se_cmd`, prepares submission with the CDB, and calls `target_submit`. Target core later calls fabric ops: writes use `write_pending` to DMA-map SGs and call `efct_scsi_recv_wr_data`; reads use `queue_data_in` to map and segment SGs and call `efct_scsi_send_rd_data`; status uses `queue_status`/`efct_lio_send_resp`; TMFs use `queue_tm_rsp` and `efct_scsi_send_tmf_resp`.

Completion flows unmap DMA SGs, continue segmented transfers if more SG entries remain, execute write commands after successful data-in from initiator, send final status for reads, or free the target command. Abort callbacks set `aborting`, call `efct_scsi_tgt_abort_io`, and rely on target-core release to complete IO object lifetime.

## State and Persistence Behavior
Configfs state creates in-kernel nport, vport, and TPG objects. There is no file-backed persistence here. `efct->tgt_efct` tracks max SGE/SGL, initiator count, IO high watermark, vport list, LIO nport, TPG, and counters. Sessions are serialized on a global ordered `lio_wq`. Active initiators are mapped through `efct->lookup` xarray. Each `efct_scsi_tgt_io` tracks target-core command state, DMA direction, TMF, SG map/count/current segment, error status, aborting flag, response-sent flag, and transferred length. The bitmask state in `tgt_io.state` is diagnostic and cumulative.

## Dependencies and Integration Points
The file integrates with Linux target core (`target_register_template`, `core_tpg_register`, `target_setup_session`, `target_init_cmd`, `target_submit`, `target_submit_tmr`, `transport_generic_free_cmd`, `target_execute_cmd`, session stop/wait/remove APIs), SCSI/FC helpers, EFCT xport, EFC node/session callbacks, fc_vport APIs, DMA SG mapping, atomics, workqueues, configfs, and xarray lookup.

## Risks
`lio_wq` is a single static workqueue shared by devices; teardown only flushes it and driver exit does not visibly destroy it here. Several error paths after `target_submit_prep` or `target_init_cmd` can leak `ios_in_use` or IO references if they return without target-core release. Segment handling must keep `seg_map_cnt`, `seg_cnt`, `cur_seg`, and `transferred_len` consistent or reads/writes can underrun, overrun, or double-unmap. NPIV creation and configfs teardown involve multiple ownership systems (`fc_vport`, vport list, TPG) and require strict ordering. `efct_lio_drop_nport` frees `efct->tgt_efct.lio_nport` rather than the container derived from `wwn`, so stale pointer assumptions matter. Watermark adjustments rely on balanced initiator add/remove callbacks.

## Test Signals
Test with configfs physical and NPIV fabric create/drop, TPG enable/disable with and without link/domain, initiator login/logout, session deletion while IOs are active, read/write/no-data commands, residual/sense responses, segmented SG transfers larger than `io->sgl_allocated`, TMF abort task and LUN reset, ABTS-driven aborts, target-core command failure paths, and DMA map/unmap fault injection. Counters to watch include `ios_in_use`, initiator count, watermarks, `rsp_sent`, and active IO list emptiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.h

## Purpose
`efct_lio.h` defines EFCT's private target-core data structures and diagnostic state flags. It bridges `struct efct_io` to `struct se_cmd`, describes target device/session/nport/vport/TPG objects, and declares target driver init/exit.

## Important APIs, Types, and Functions
Logging macros `efct_lio_io_printf` and `efct_lio_tmfio_printf` print command identity. `efct_set_lio_io_state` ORs state bits into `io->tgt_io.state`. `struct efct_scsi_tgt` stores target-wide max SGE/SGL, initiator/IO counters, watermarks, LIO objects, vport list, lock, and WWNN. `struct efct_node` is EFCT's target session node containing a kref, EFC node pointer, target-core session, active IO list, FC IDs, VPI/RPI, and abort count. `struct efct_scsi_tgt_io` embeds `struct se_cmd` and tracks DMA direction, task attribute, LUN, TMF/abort state, SG mapping progress, error, response sent, and transfer count. The header also defines LIO nport, vport, TPG attributes, TPG, node ACL, and vport list entries.

## Control Flow
The structures are populated by `efct_lio.c`: configfs allocates nports/vports/TPGs; session setup allocates `efct_node`; command receive clears and fills `efct_scsi_tgt_io`; target-core callbacks mutate state bits and SG progress; release paths free commands and IOs.

## State and Persistence Behavior
All state is in-kernel and mostly configfs/session scoped. State bits are cumulative diagnostics rather than an exclusive finite-state machine. TPG attributes mirror configfs booleans. Active IO lists and krefs protect session command lifetime.

## Dependencies and Integration Points
The header includes `efct_scsi.h` and `<target/target_core_base.h>`, exposing Linux target-core types to EFCT IO structures. Any layout changes affect command allocation, `container_of` conversions, and fabric ops.

## Risks
The cumulative state bitmask can hide ordering bugs because old bits are never cleared. `struct efct_scsi_tgt_io` embeds `se_cmd`, so alignment and lifetime must stay compatible with target-core expectations. `efct_node` lifetime depends on active IO krefs and target session teardown ordering.

## Test Signals
Build tests should cover `container_of` usage. Runtime tests should verify state bits through representative command paths, active IO list/kref balance, TPG attribute toggling, NPIV vport list management, and command release decrementing target IO counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_lio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.c

## Purpose
`efct_scsi.c` is the transport-independent SCSI target dispatch layer between LIO/unsolicited FCP parsing and the EFCT HW layer. It allocates active SCSI IOs, builds HW SGLs, manages pending IO dispatch when HW XRIs are exhausted, translates HW completion status to SCSI status, sends target read/write/status/TMF responses, and handles target abort/BLS responses.

## Important APIs, Types, and Functions
Public allocation/lifetime functions are `efct_scsi_io_alloc`, `efct_scsi_io_free`, `_efct_scsi_io_free`, and `efct_scsi_io_complete`. Dispatch functions are `efct_scsi_io_dispatch`, `efct_scsi_io_dispatch_abort`, and `efct_scsi_check_pending`. Data/status APIs are `efct_scsi_send_rd_data`, `efct_scsi_recv_wr_data`, `efct_scsi_send_resp`, `efct_scsi_send_tmf_resp`, and `efct_scsi_tgt_abort_io`. BLS helpers are `efct_bls_send_rjt` and internal BA_ACC/BA_RJT callbacks. Internal helpers map SGs to HW SGEs, perform pending-list dispatch, and translate completion status.

## Control Flow
`efct_scsi_io_alloc` pulls a software IO from the pool, initializes a kref and generic fields, grabs a node reference, marks target command mode, and links the IO onto the node active list. Data movement APIs set `hio_type`, callbacks, transfer lengths, residual/auto-response flags, WQ steering flags, and FCP target parameters before calling `efct_scsi_io_dispatch`.

Dispatch first reuses an existing HIO for continuation phases. If pending work exists, it queues the IO, honoring low-latency insertion for data IOs. Otherwise it tries to allocate a HW IO. If allocation fails, it queues the IO and returns success to the upper layer. `efct_scsi_check_pending` drains pending IOs without recursion; abort IOs do not need a new HIO but are ordered through the pending list. Dispatch failure is reported asynchronously through a NOP mailbox callback.

Completion enters `efct_target_io_cb`, updates transferred length, maps SLI WCQE status/ext status to `enum efct_scsi_io_status`, sets completion flags, invokes the target callback, and then tries pending work. Abort completion maps abort-specific statuses, calls the saved abort callback on the original IO, drops the original IO reference, frees the abort software IO, and drains pending work.

## State and Persistence Behavior
State is volatile and command scoped. Pending dispatch is held in `xport->io_pending_list` protected by `io_pending_lock` with counters and a recursion guard. Active IO lifetime is protected by `io->ref`, node refs, and pool ownership. `io->transferred`, `wire_len`, `xfer_req`, `auto_resp`, callbacks, and HW fields track multi-phase commands.

## Dependencies and Integration Points
This file calls the IO pool, HW IO/SGL/send/abort APIs, LIO callbacks through function pointers, xport pending counters/stats, and FC/FCP response structures. It is called by `efct_lio.c` for target-core operations and by `efct_unsol.c` for BA_RJT/TMF flows.

## Risks
Pending-list ordering is central: an IO queued because no HIO was available must later dispatch with the correct callback and stale fields cleared. The low-latency insertion uses `list_add(&xport->io_pending_list, &io->io_pending_link)`, whose argument order appears reversed relative to normal Linux list API usage and is a high-value review target. Residual trimming mutates the caller-provided SGL entries for overrun handling. Abort IO allocation bypasses `efct_scsi_io_alloc`, so it has different active-list/refcount behavior. Error paths in `efct_hw_bls_send` and `efct_els_hw_srrs_send` can leave allocated HIOs if WQE formatting fails unless caller cleanup handles it.

## Test Signals
Exercise HW IO exhaustion and pending-list drain, low-latency queue insertion, continuation data phases, read/write residual and auto-good-response behavior, sense/status response formatting, local reject/DIF/timeout/shutdown status mapping, abort before HW IO allocation, abort while HW IO active, ABTS BA_ACC/BA_RJT flows, and pool/refcount balance after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.h

## Purpose
`efct_scsi.h` defines the EFCT SCSI target-facing API. It provides command/data flags, SCSI completion status enums, TMF enums, SGL shape, callback typedefs, vport structure, and prototypes used by unsolicited frame parsing, LIO target glue, xport registration, and HW dispatch.

## Important APIs, Types, and Functions
Flag groups describe received FCP command direction/task attributes, data/status submission behavior, auto-response disabling, low-latency, and WQ steering/class selection. `struct efct_scsi_cmd_resp` describes status, sense, residual, and wire response length. `struct efct_vport` wraps Scsi_Host/fc_vport state and FC statistics. `enum efct_scsi_io_status` normalizes HW completion statuses. Callback typedefs model data/status completions. `enum efct_scsi_tmf_cmd` and `enum efct_scsi_tmf_resp` mirror FCP task management operations. Function prototypes cover IO alloc/free, target driver/device/session events, command/TMF receive, data/status/TMF send, abort, FC transport registration, Scsi_Host/vport lifecycle, and pending dispatch.

## Control Flow
`efct_unsol.c` uses receive prototypes for FCP and TMF frames. `efct_lio.c` uses send/abort APIs from target-core callbacks. `efct_xport.c` uses target driver and FC transport registration/device functions. `efct_scsi.c` implements the data path declared here.

## State and Persistence Behavior
The header itself stores no state, but defines the enums and flags that drive `struct efct_io` and `struct efct_scsi_tgt_io` state transitions. `struct efct_vport` persists while a Scsi_Host or NPIV vport exists.

## Dependencies and Integration Points
It includes Linux SCSI host and FC transport headers and references EFCT/EFC structures. It is one of the public contracts for cross-file EFCT target integration.

## Risks
The command direction flag naming is easy to misread: FCP write data maps to initiator-to-target and the LIO code maps that to `DMA_TO_DEVICE`. WQ steering and class masks share high bits with the flags argument, so new flags must avoid bit collisions. Status enum changes require synchronized completion translation in `efct_scsi.c` and response handling in `efct_lio.c`.

## Test Signals
Compile signature checks, command flag translation tests, status mapping tests, TMF command/response mapping, vport lifecycle tests, and WQ steering flag propagation into HW IO fields are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.c

## Purpose
`efct_unsol.c` handles unsolicited FC frames received from RQ processing. It routes FCP command frames to the SCSI target path, routes BLS ABTS frames to abort handling, rejects unsupported TMFs when necessary, sends task-set-full/busy responses with send-frame when IO allocation fails, and forwards non-local frames to the EFC discovery library.

## Important APIs, Types, and Functions
The public entry points are `efct_unsolicited_cb`, `efct_dispatch_fcp_cmd`, and `efct_node_recv_abts_frame`. Internal helpers include `efct_node_find`, `efct_dispatch_frame`, `efct_dispatch_unsol_tmf`, `efct_validate_fcp_cmd`, `efct_populate_io_fcp_cmd`, `efct_get_flags_fcp_cmd`, send-frame response helpers, `efct_process_abts`, and rejection callbacks.

## Control Flow
HW RQ completion passes a sequence to `efct_unsolicited_cb`. `efct_dispatch_frame` inspects the FC header. FCP frames look up an `efct_node` by destination FCID and source FCID in `efct->lookup`; if found, `efct_dispatch_fcp_cmd` validates payload length, extracts LUN/CDB/task flags, allocates a SCSI IO, populates FC exchange metadata, and calls either `efct_scsi_recv_tmf` or `efct_scsi_recv_cmd`. If IO allocation fails, it constructs an FCP response with BUSY or TASK_SET_FULL and sends it via `efct_hw_send_frame`.

BLS frames are treated as ABTS. The code looks up the node, allocates a manufactured SCSI IO, finds the target IO by OX_ID/RX_ID, and if found submits an abort-task TMF. If not found, it sends BA_RJT. Frames not handled as FCP/BLS are forwarded to `efc_dispatch_frame`.

## State and Persistence Behavior
No persistent state is stored here. It consumes one RQ sequence at a time and uses `efct->lookup` to map FCID pairs to active target nodes. It increments `node->abort_cnt` for ABTS frames. Send-frame response context is carved out of the received payload buffer and freed when the send-frame callback reposts the original sequence.

## Dependencies and Integration Points
This file depends on HW sequence/RQ free APIs, SCSI IO/TMF/response APIs, EFC discovery dispatch, xarray node lookup, FC/FCP frame structures, and send-frame WQE support. It is invoked by `efct_hw_rqpair_process_rq`.

## Risks
Node lookup failures for ABTS return `-EIO` without freeing the sequence in the BLS not-found path handled by `efct_dispatch_frame`, which should be checked against caller free behavior. Unsupported additional CDB length returns `-EIO` after IO allocation without clearly freeing the IO. Send-frame response context reuses the payload DMA buffer as heap; insufficient buffer size errors must ensure the original sequence is eventually reposted. Direction flag naming can be confusing and should be tested against real FCP read/write commands.

## Test Signals
Test valid FCP read/write/no-data commands, invalid short payloads, invalid LUN conversion, additional CDB rejection, IO allocation failure busy/task-set-full response, TMF flag mapping/rejection, ABTS found/not-found paths, node lookup races during shutdown, and fallback to EFC discovery for non-FCP/BLS frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.h

## Purpose
`efct_unsol.h` declares the unsolicited receive entry points shared between HW RQ completion processing and the SCSI/FCP frame handling implementation.

## Important APIs, Types, and Functions
The header declares `efct_unsolicited_cb`, `efct_dispatch_fcp_cmd`, and `efct_node_recv_abts_frame`. These functions cover generic unsolicited frame dispatch, FCP command dispatch for a resolved target node, and ABTS/BLS abort frame handling for a resolved target node.

## Control Flow
`efct_hw_queues.c` calls `efct_unsolicited_cb` after parsing an RQ completion into an `efc_hw_sequence`. The implementation may call the FCP command or ABTS-specific helpers declared here, then return/repost the sequence through HW APIs.

## State and Persistence Behavior
No state is defined in the header. The declared functions operate on transient `struct efc_hw_sequence` objects and active `struct efct_node` references.

## Dependencies and Integration Points
The declarations depend on `struct efc_hw_sequence` and `struct efct_node` definitions available through including driver headers. The include guard name uses `__OSC_UNSOL_H__`, which differs from the EFCT naming style but is functionally harmless.

## Risks
The small API surface means most risks are ownership conventions: callers and implementations must agree exactly when a sequence is freed/reposted and when node references are held. Any signature change affects HW queue processing and unsolicited frame handling together.

## Test Signals
Build coverage for declarations, RQ-to-unsolicited integration tests, and ownership checks around sequence free/repost are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_unsol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.c

## Purpose
`efct_xport.c` is the EFCT transport/lifecycle bridge between PCI driver probe/remove, HW initialization, SCSI/FC transport registration, target-core setup, debugfs, link control, stats, Scsi_Host objects, and NPIV vports. It owns the top-level `struct efct_xport` allocation, attach/initialize/detach/free flow, FC transport templates, and host attribute callbacks.

## Important APIs, Types, and Functions
Lifecycle APIs are `efct_xport_alloc`, `efct_xport_attach`, `efct_xport_initialize`, `efct_xport_detach`, `efct_xport_control`, `efct_xport_status`, and `efct_xport_free`. SCSI/FC registration APIs are `efct_scsi_new_device`, `efct_scsi_del_device`, `efct_scsi_reg_fc_transport`, `efct_scsi_release_fc_transport`, `efct_scsi_new_vport`, and `efct_scsi_del_vport`. FC transport callbacks include host port ID/type/state/speed/fabric name, stats get/reset, LIP issue, and vport create/delete/disable. Debugfs helpers create/remove an `efct/sessions` tree.

## Control Flow
Probe-side attach calls `efct_hw_setup`, parses receive filters, and creates the software IO pool sized by HW SGL capability. Initialize sets pending-IO counters/lists, calls `efct_hw_init`, initializes the target device and Scsi_Host, starts the stats timer, and creates debugfs. Detach tears target and Scsi_Host state down, deletes the stats timer, tears HW down, and removes debugfs. Free releases the IO pool and xport object.

Port control maps xport commands to HW link init/shutdown. Shutdown gracefully downs the link unless a reset is required, registers a domain-free completion callback, waits for domain shutdown with timeout, unregisters the callback, and deletes saved vports. Status calls return configured state, derived online/offline state from link speed, cached stats, or synchronous stat reset via mailbox completion callbacks.

FC host setup allocates a target-mode `Scsi_Host`, stores `struct efct_vport` in hostdata, sets queue depth/SGL/CDB limits, attaches the FC transport template, adds the host with DMA, and fills symbolic name, classes, supported speeds, WWNN/WWPN, and NPIV limit. NPIV vport creation allocates a separate Scsi_Host with the vport transport template and stores it in `fc_vport->dd_data`.

## State and Persistence Behavior
All state is volatile. `struct efct_xport` holds pending IO list/counters, configured link state, requested WWNs, cached FC stats, FCP counters, and stats timer. Static globals hold FC transport templates and debugfs root/count. Stats are refreshed every 3 seconds through asynchronous HW mailbox calls and copied into FC host statistics on request.

## Dependencies and Integration Points
This file integrates with the PCI-owned `struct efct`, HW layer, IO pool, target-core glue, SCSI midlayer, FC transport class, fc_vport APIs, EFC domain shutdown callbacks, debugfs, timers, completions, and SLI link capability reporting. Probe/remove paths in `efct_driver.c` call into this lifecycle.

## Risks
The stats timer reinitializes with `timer_setup` on each refresh before `mod_timer`, which is unusual and should be checked for races with detach. Detach uses `timer_delete` only if pending; a callback already running may still access xport/HW. `efct_scsi_new_device` and `efct_scsi_new_vport` can leak `Scsi_Host` allocations if `scsi_add_host_with_dma` fails without `scsi_host_put`. Debugfs root refcounting is global and assumes balanced per-device session dirs. `dd_fcvport_size` is hard-coded to 128 with a comment indicating it should be a real sizeof. Shutdown timeout still proceeds after warning, so tests should ensure resources remain valid.

## Test Signals
Probe/remove, attach failure, HW init failure, target init failure, Scsi_Host add failure, debugfs create/remove with multiple devices, stats timer during detach, FC transport register/unregister, link online/offline/LIP, domain shutdown timeout, NPIV create/delete, host attribute reads under no-domain and online-domain states, and stats reset completion behavior are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.c -->
