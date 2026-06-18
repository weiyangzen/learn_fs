# subset-b-005277 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_context.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_context.c

Purpose: implements the runtime remote node context (RNC) state machine for the Intel ISCI SAS/SATA controller. An RNC is the driver's software owner for a remote-node SRAM image in the SCU hardware. This file builds that image, posts and invalidates it, reacts to SCU RNC events, gates I/O start eligibility, and coordinates suspend/resume/destruct callbacks.

Important APIs/functions: `rnc_state_name()` stringifies `SCI_RNC_*` states. `sci_remote_node_context_construct()` initializes an RNC with an RNI and state machine. `sci_remote_node_context_resume()`, `sci_remote_node_context_suspend()`, and `sci_remote_node_context_destruct()` are the main transition requests. `sci_remote_node_context_event_handler()` consumes SCU event codes such as `SCU_EVENT_POST_RNC_COMPLETE`, `SCU_EVENT_POST_RNC_INVALIDATE_COMPLETE`, `SCU_EVENT_POST_RCN_RELEASE`, and suspend notifications. `sci_remote_node_context_start_io()` allows normal I/O only in `SCI_RNC_READY`; `sci_remote_node_context_start_task()` resumes the RNC for task-management work; `sci_remote_node_context_is_safe_to_abort()` allows abort posting only while invalidating or TX/RX suspended.

Control flow: construction starts in `SCI_RNC_INITIAL`. A resume from initial builds the SCU context buffer and posts it, moving to `SCI_RNC_POSTING`; post completion moves to `SCI_RNC_READY`. Ready entry consumes deferred destination state: it can notify the caller, immediately request suspension, or suppress notification until a suspend/resume sequence returns to ready. Destruct sets `RNC_DEST_FINAL`, wakes the host event queue, and usually moves to `SCI_RNC_INVALIDATING`, whose enter hook terminates outstanding requests and posts RNC invalidation. Invalidate completion either returns to initial for final destruction or reposts the context. Resume from suspended uses a direct RNC resume except expander-attached SATA, which invalidates and reposts to clear the TCi-to-NCQ mapping. Software suspension posts `SCI_SOFTWARE_SUSPEND_CMD`; hardware suspension events move ready/awaiting states to TX or TX/RX suspended.

State and persistence behavior: persistent device-visible state is the SCU remote-node context table entry selected by `remote_node_index`. `sci_remote_node_context_construct_buffer()` zeroes the RNC slot(s), writes RNI, port width, logical port, little-endian SAS address, timeout parameters, connection rate, and flags, then posting marks `is_valid`. Invalidation clears `is_valid`. In-memory state includes destination state, suspend type/reason/count, callback/cookie, and the state machine. Memory barriers and event queue wakeups make suspend/destruct progress visible to waiters.

Dependencies/integration: depends on `remote_device` helpers for `rnc_to_dev()`, request termination/abort, post requests, transport setup, and hang detection; on host fields for context RAM and user timeouts; on libsas `domain_device` and SATA detection; on `scu_event_codes.h` and `scu_task_context.h` for event and command encodings.

Risks: state transitions are hardware-event-driven, so missed or misclassified events can strand callbacks. The `destination_state` logic is subtle around post/invalidate/resume races and final destruction. SATA paths differ for direct-attached versus expander-attached devices, and incorrect handling can leave stale NCQ tag mappings. Aborting before RNC safe states can corrupt request cleanup. Test signals include resume from initial, suspend requested during posting, resume requested while awaiting suspension, hardware TX and TX/RX suspend events, direct and expander SATA resume, final destruct while invalidating, callback invocation once, and event queue wakeups after suspend/destruct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_context.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_context.h

Purpose: declares the software model for SCU remote node contexts and the API used by remote-device and request code to post, suspend, resume, destroy, and query RNCs.

Important APIs/types: `SCIC_SDS_REMOTE_NODE_CONTEXT_INVALID_INDEX` is the invalid RNI value, also used when programming SATA direct-attached state. `enum sci_remote_node_suspension_reasons` distinguishes hardware suspend, normal software suspend, and link-hang-detection suspend. `SCI_SOFTWARE_SUSPEND_CMD` and `SCI_SOFTWARE_SUSPEND_EXPECTED_EVENT` bind software suspend to TX/RX suspend command/event encodings. `RNC_STATES` defines `SCI_RNC_INITIAL`, `POSTING`, `INVALIDATING`, `RESUMING`, `READY`, `TX_SUSPENDED`, `TX_RX_SUSPENDED`, and `AWAIT_SUSPENSION`. `enum sci_remote_node_context_destination_state` records deferred transition targets including final destruction and suspended-then-resume. `struct sci_remote_node_context` stores the RNI, suspend metadata, destination state, one completion callback/cookie, and a `sci_base_state_machine`.

Control flow: callers construct with `sci_remote_node_context_construct()`, then request transitions via `sci_remote_node_context_resume()`, `sci_remote_node_context_suspend()`, or `sci_remote_node_context_destruct()`. Hardware completions/events feed `sci_remote_node_context_event_handler()`. I/O paths call `sci_remote_node_context_start_io()` or `start_task()` before posting work. Destroy detection is exposed through `sci_remote_node_context_is_being_destroyed()`, which treats final destination and quiescent initial/unspecified state as unavailable.

State and persistence behavior: this header documents the RNC as volatile driver state that controls a persistent SCU context-table entry. The struct itself persists for the device lifetime, while callbacks represent one outstanding transition request. The `suspend_count` is an in-memory observation counter rather than hardware state.

Dependencies/integration: includes `isci.h` for SCI status/state-machine definitions and forward-declares `isci_request` and `isci_remote_device`. It is consumed by `remote_node_context.c`, remote device management, request abort paths, and any code that needs to know whether an RNC is ready or suspended.

Risks: destination-state values are part of a cross-file protocol; adding states or changing callback semantics without updating `remote_node_context.c` can produce missed wakeups or double notifications. `is_suspended()` only tests TX/RX suspended, not TX-only suspended, so callers must understand the narrower meaning. Test signals include API behavior for each state, invalid RNI resume failure, software suspend reason handling, destroy detection, and task-start resume callback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_table.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_table.c

Purpose: implements allocation and release of SCU remote node indexes (RNIs). The SCU requires expander-attached STP devices to reserve three consecutive remote node entries, while SSP and direct SATA use one; this allocator tracks both individual availability and grouped availability.

Important APIs/functions: `sci_remote_node_table_initialize()` zeros the tables, marks every configured RNI available, and seeds group selector bitmaps. `sci_remote_node_table_allocate_remote_node()` allocates either one RNI (`SCU_SSP_REMOTE_NODE_COUNT`) or a triple (`SCU_STP_REMOTE_NODE_COUNT`). `sci_remote_node_table_release_remote_node_index()` returns either one or three entries. Private helpers manipulate bitsets: `get_group_index()`, `set/clear_group_index()`, `set/clear_node_index()`, `set/clear_group()`, `get_group_value()`, and specialized single/triple allocation and release functions.

Control flow: initialization fills `available_remote_nodes` one RNI at a time, computes the number of dwords in the node and group arrays, then marks full groups in selector 2 and any partial remainder in selector 0 or 1. Single allocation searches selector 0 first, then 1, then 2, so it prefers groups with the fewest available entries and preserves full triples for STP. Once a bit is selected, it clears the old group selector, clears the node bit, and if the group still has free nodes moves it down to the next smaller selector. Triple allocation searches only selector 2, returns the first group's base RNI, clears selector 2, and clears all three node bits. Single release computes the group value and moves the group from empty to single, single to dual, or dual to triple before setting the node bit. Triple release marks the whole group available and sets selector 2.

State and persistence behavior: all allocator state is in-memory under `struct sci_remote_node_table`: a nibble-packed `available_remote_nodes` bitmap and three selector bitmaps indexed by group population. There is no disk persistence; correctness persists only for the controller lifetime. The code uses `BUG_ON` for impossible indices and double-free of a full group.

Dependencies/integration: depends on constants in `remote_node_table.h`, `SCI_MAX_REMOTE_DEVICES`, and the invalid index from `remote_node_context.h`. Remote-device discovery and teardown use this allocator before constructing RNCs and after destroying them.

Risks: the table assumes groups of exactly three entries and nibble layouts; off-by-one errors corrupt availability globally. Partial group initialization must match hardware capacity. Releasing the wrong count for an allocated RNI can create overlapping allocations. Test signals include capacities not divisible by three, allocation exhaustion, single allocation preference order, triple allocation preserving consecutive alignment, release-after-single/triple, double-release BUG conditions, and repeated allocate/free cycles preserving all bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_table.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_table.h

Purpose: defines the RNI allocation table layout and constants for SCU remote node allocation. It encodes the hardware constraint that STP may require three consecutive remote node contexts.

Important APIs/types: `SCIC_SDS_REMOTE_NODE_SETS_PER_BYTE`, `SCIC_SDS_REMOTE_NODE_SETS_PER_DWORD`, `SCIC_SDS_REMOTE_NODES_PER_BYTE`, and `SCIC_SDS_REMOTE_NODES_PER_DWORD` describe the nibble packing. `SCIC_SDS_REMOTE_NODE_TABLE_FULL_SLOT_VALUE` is `0x07`, meaning all three bits in a group are available; `EMPTY_SLOT_VALUE` is `0`. `SCU_STP_REMOTE_NODE_COUNT`, `SCU_SSP_REMOTE_NODE_COUNT`, and `SCU_SATA_REMOTE_NODE_COUNT` express allocation sizes. `struct sci_remote_node_table` stores `available_nodes_array_size`, `group_array_size`, the packed node bitmap, and three selector bitmaps keyed by one-, two-, and three-entry availability. Public APIs initialize, allocate, and release entries.

Control flow: users initialize with the controller's remote-node capacity. Allocation callers pass the required count and receive a base RNI or invalid index. Release callers must provide the same count used at allocation time.

State and persistence behavior: table contents are volatile controller-lifetime allocation state. The source-tree-level invariant is that selector bitmaps mirror the nibble bitmap: selector 0 means one bit set, selector 1 means two bits set, selector 2 means three bits set. The arrays are sized from `SCI_MAX_REMOTE_DEVICES`, so runtime capacities smaller than the maximum use prefixes of the arrays.

Dependencies/integration: includes `isci.h` for maximum device count and integer types. The table backs remote-device construction, which then programs matching hardware contexts through `remote_node_context.c`.

Risks: callers must not mix STP triple and SSP single release semantics. Any future hardware with a different STP RNC count would require updating packing constants and implementation logic together. Test signals include struct sizing for maximum devices, initialization for odd capacities, selector consistency after operations, and invalid-index handling when no group of requested size exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/request.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/request.c

Purpose: implements ISCI request construction, state management, frame handling, task-context posting, completion decoding, and libsas/libata completion translation for SSP, SMP, SATA/STP, ATAPI, PIO, DMA, NCQ, and task-management requests.

Important APIs/functions: `sci_request_start()`, `sci_io_request_terminate()`, `sci_request_complete()`, `sci_io_request_tc_completion()`, and `sci_io_request_frame_handler()` are the central runtime entry points. Construction flows include `isci_request_execute()`, `isci_io_request_build()`, `sci_io_request_construct()`, `sci_io_request_construct_basic_ssp()`, `sci_io_request_construct_basic_sata()`, `sci_io_request_construct_smp()`, and `sci_task_request_construct()`. Protocol builders include `sci_request_build_sgl()`, `sci_io_request_build_ssp_command_iu()`, `sci_task_request_build_ssp_task_iu()`, `scu_ssp_*_construct_task_context()`, `scu_sata_request_construct_task_context()`, `sci_stp_optimized_request_construct()`, `sci_stp_pio_request_construct()`, and ATAPI reconstruction helpers. Completion helpers map controller status to SCI/libsas status, handle suspending completions, and process SSP/STP responses.

Control flow: `isci_request_execute()` builds the request, locks the controller, and starts I/O or task work. General construction initializes the request state machine, target, protocol, response frame index, SCU status, and task context. SSP builds command or task IUs and fills SSP task context fields. SMP byte-swaps the SMP request, maps the request sg, programs SMP TC fields, and waits for response UF plus TC completion. STP copies the ATA FIS, sets NCQ tag fields if needed, and chooses raw non-data, NCQ/DMA accelerated, PIO, or ATAPI paths. `sci_request_start()` writes TCi/tag fields and enters `SCI_REQ_STARTED`; the started-state enter hook immediately fans out unaccelerated protocols into substates such as SMP wait response, STP non-data H2D/D2H, PIO wait/data-in/data-out, UDMA wait, and ATAPI waits.

State and persistence behavior: per-request state is held in `struct isci_request`, its SCU task context, DMA addresses, status fields, flags, SGL table, saved unsolicited frame index, and protocol-specific SSP/STP unions. Hardware-visible persistence is the task context table entry and posted context command. The request state machine ends in `SCI_REQ_FINAL` after `sci_request_complete()` releases saved frames. DMA mappings are undone on completion for SSP and SMP paths; SATA mappings are owned by libata. STP PIO state persists progress in `stp.req.pio_len`, status, SGL index/set/offset. ATAPI may synthesize a D2H FIS for underrun workarounds and transitions the remote device to an ATAPI error state.

Dependencies/integration: integrates deeply with libsas `sas_task`, libata ATA queued commands/FIS fields, the SCSI protection API, Linux DMA and scatterlist APIs, SCU completion/event codes, SCU task-context layout, remote device/RNC suspend and abort paths, unsolicited frame control, and controller posting/completion helpers. Completion translation sets `task_status`, `SAS_TASK_NEED_DEV_RESET`, residuals, open-reject reasons, and calls `ireq_done()`.

Risks: this file is state-machine dense. Frame ownership must be exact: most UF paths release immediately, while saved PIO frames must be released later. SGL building writes initial pairs into the task context and overflow pairs into request memory; bad DMA offsets or zero-scatter mapping can break hardware DMA. DIF insert/strip alters transfer length and block-guard fields and depends on supported sector sizes. SCU completion aliases share numeric values, so protocol context decides whether the target completed, should retry, or needs reset. STP/ATAPI corner cases synthesize or wait for D2H frames based on hardware behavior. Abort safety depends on RNC suspension state and `IREQ_PENDING_ABORT`. Test signals include SSP read/write/no-data, DIF read strip/write insert, SMP response timeout/retry, SATA NCQ tag programming, UDMA unexpected-FIS path, non-data D2H error, PIO data-in/out multi-frame transfers, ATAPI data/no-data/underrun, abort from constructed/started/substates, remote-device-reset-required propagation, DMA unmap coverage, and unsolicited frame release on every exit path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/request.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/request.h

Purpose: declares the ISCI request object, protocol-specific request storage, request state machine states, public request APIs, and small helpers used by controller, task, and remote-device code.

Important APIs/types: `struct isci_stp_request` tracks PIO length, ending status, and current SGL position for STP PIO/ATAPI handling. `struct isci_request` stores request flags (`IREQ_COMPLETE_IN_TARGET`, `IREQ_TERMINATED`, `IREQ_TMF`, `IREQ_ACTIVE`, `IREQ_PENDING_ABORT`, `IREQ_TC_ABORT_POSTED`, `IREQ_ABORT_PATH_ACTIVE`, `IREQ_NO_AUTO_FREE_TAG`), task or TMF pointer, host pointers, DMA addresses, request completion, state machine, target device, IO tag, protocol, SCU/SCI status, post context, task context pointer, local SGL overflow table, saved unsolicited frame index, and SSP/STP command/response unions. `REQUEST_STATES` enumerates initial/constructed/started protocol substates, completed, aborting, and final states. Public functions cover start, terminate, frame/TC completion, task construction, tag lookup, and execution.

Control flow: callers obtain a request object from a tag via `isci_io_request_from_tag()` or `isci_tmf_request_from_tag()`, attach task/TMF state, build and execute it, then route hardware completions into `sci_io_request_tc_completion()` and unsolicited frames into `sci_io_request_frame_handler()`. `sci_io_request_get_dma_addr()` computes a DMA address for embedded buffers by offsetting from the request's DMA base, and `to_ireq()` converts embedded STP state back to the enclosing request.

State and persistence behavior: the request struct is a controller-lifetime pool object reused by tag. Each use clears flags/status and reinitializes the state machine. The request owns embedded protocol buffers and SGL-pair overflow memory for hardware DMA. `saved_rx_frame_index` persists a controller frame-buffer reference until completion releases it.

Dependencies/integration: includes `isci.h`, `host.h`, and `scu_task_context.h`; uses libsas `sas_task`, TMF structures, SCSI/ATA protocol fields, controller tag encoding, and hardware task-context definitions.

Risks: the union of IO task and TMF task is manually discriminated by `IREQ_TMF`; misuse can corrupt completion handling. `sci_io_request_get_dma_addr()` assumes the target virtual address is inside `struct isci_request`. State additions must remain synchronized with `request.c`'s state table and handlers. Test signals include tag reuse clearing all per-use fields, TMF versus normal completion, embedded-buffer DMA address bounds, NCQ recovery detection, and no stale saved frame index across reused requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/sas.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/sas.h

Purpose: provides local SAS/SATA protocol constants and packed wire-format structures used by the ISCI request path where equivalent libsas definitions were absent or insufficient in this codebase.

Important APIs/types: SATA FIS type constants define register H2D/D2H, set-device-bits, DMA activate/setup, BIST activate, PIO setup, and data FIS values. `SSP_RESP_IU_MAX_SIZE` fixes the maximum response IU copy size at 280 bytes. `struct ssp_cmd_iu` models an SSP command IU with LUN, task attributes, and 16-byte CDB. `struct ssp_task_iu` models an SSP task-management IU with LUN, task function, and task tag. SMP request payload structs cover phy-id requests, configure route info, phy control, and generic `struct smp_req` with flexible data. `struct sci_sas_address` represents a SAS address as high/low u32 words.

Control flow: `request.c` fills `ssp_cmd_iu` for normal SSP I/O, `ssp_task_iu` for task management, inspects and byte-swaps `smp_req` for SMP construction, and compares FIS constants while processing unsolicited SATA/STP frames. Response-size constants bound SSP response copying and byte-swapping.

State and persistence behavior: these are packed on-wire or hardware-DMA layouts, not persistent driver state. Their field layout and endianness handling are part of the request/task-context ABI between driver, libsas buffers, and SCU hardware.

Dependencies/integration: includes only `<linux/kernel.h>` but is included by `request.c` alongside libsas/libata headers. Several comments note these definitions ideally belong in common SCSI/SAS headers, so this file is compatibility glue.

Risks: packed bitfields and protocol layouts must match SAS/SATA specifications. CDB length is fixed at 16 bytes here, so extended CDB support would require changes. SMP request default-length fixups in `request.c` assume `struct smp_req` header layout. Test signals include byte-for-byte SSP command/task IU contents, FIS type dispatch for every STP substate, SMP request length defaults, and response IU copy bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_completion_codes.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_completion_codes.h

Purpose: defines SCU hardware completion-code bitfields, extraction macros, and normalized transport-layer completion status constants used by request completion handling.

Important APIs/macros: completion type bits live at bits 28-30 and distinguish task, SDMA, unsolicited frame, event, and notify completions. Status masks split transport-layer status, SDMA status, PEG/port/protocol-engine fields, and completion index. `SCU_GET_COMPLETION_TYPE()`, `SCU_GET_COMPLETION_STATUS()`, `SCU_GET_COMPLETION_TL_STATUS()`, `SCU_MAKE_COMPLETION_STATUS()`, `SCU_NORMALIZE_COMPLETION_STATUS()`, `SCU_GET_COMPLETION_SDMA_STATUS()`, `SCU_GET_COMPLETION_INDEX()`, `SCU_GET_FRAME_INDEX()`, and `SCU_GET_FRAME_ERROR()` are the main decoders. Status constants cover success, response/check-response, CRC/NAK/link/FIS/data errors, SMP errors, task abort, open rejects, invalid VIIT/IIT/RNC, and STP resource/protocol/rate rejects.

Control flow: `request.c` compares `SCU_GET_COMPLETION_TL_STATUS(code)` against `SCU_MAKE_COMPLETION_STATUS(status)` in request-state handlers, normalizes unknown failures into `scu_status`, detects suspending completion classes, and maps open rejects into libsas open-reject reasons. Controller code can use type/index macros to dispatch completions to request, frame, event, or notification handlers.

State and persistence behavior: no runtime state; the header is an ABI contract for decoding hardware completion dwords. Aliased constants intentionally share numeric values where hardware meaning depends on protocol or context, for example CRC/check-response and ACK/NAK/link errors.

Dependencies/integration: relies on `u32` definitions from includers. It integrates with `scu_event_codes.h`, `scu_task_context.h`, and request/RNC state machines that post commands and decode completions.

Risks: the header contains two constants cast as `U32` rather than `u32`; if those paths compile in a context without `U32`, they are hazardous. Aliased numeric values require protocol-aware handling; a flat mapping can mark incomplete target tasks as complete or vice versa. Test signals include macro extraction for representative completion dwords, all request completion switch cases, frame index decoding, open-reject mapping, and suspend-trigger classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_completion_codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_event_codes.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_event_codes.h

Purpose: defines SCU event-code construction, masks, event type/specifier constants, and decoding macros for non-task hardware events, especially remote-node events consumed by the RNC state machine.

Important APIs/macros: event type occupies bits 24-27 and event specifier bits 18-23. `SCU_EVENT_TYPE()`, `SCU_EVENT_SPECIFIC()`, and `SCU_EVENT_MESSAGE()` construct event codes. `scu_get_event_type()`, `scu_get_event_specifier()`, and `scu_get_event_code()` decode incoming event dwords. Event families include SMU command/PCQ/register/PCIe/reset errors, transport ACK/NAK timeout, broadcast changes, OSSP link/phy/rate events, fatal internal memory errors, RNC TX/TX_RX suspend, RNC misc operations, error-count events, PTX schedule events, task timeout, and I_T nexus timeout.

Control flow: `remote_node_context.c` uses combined event codes to recognize post complete, invalidate complete, and RNC release events; it uses event types to accept suspend notifications during invalidate/resume and to transition ready/awaiting RNCs to suspended states. Request completion handling uses `SCU_EVENT_TL_RNC_SUSPEND_TX` and `SCU_EVENT_TL_RNC_SUSPEND_TX_RX` as suspend-type arguments when a completion implies upcoming hardware suspension.

State and persistence behavior: no state is stored here. The constants define hardware event ABI values. The event code is a transient dword received from the controller and routed to state machines.

Dependencies/integration: relies on `u32` from includers. It pairs with context commands in `scu_task_context.h`, because post/invalidate/resume commands produce corresponding events. It also supports broader controller/port/link event dispatch outside this subset.

Risks: typo-compatible naming matters: `SCU_EVENT_POST_RCN_RELEASE` omits the second "N" and must match current users. Confusing type-only versus full-code comparisons can accept the wrong event. Test signals include RNC post/invalidate/resume event transitions, driver-posted suspend event decoding, broadcast/link event routing, and masking of unrelated low bits in hardware event dwords.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_event_codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_remote_node_context.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_remote_node_context.h

Purpose: defines the SCU hardware SRAM layout for remote node contexts. The driver writes these structures before posting RNC commands so the controller can open connections to SAS/STP targets.

Important APIs/types: `struct ssp_remote_node_context` is the real layout used by current code. It contains the RNI, remote port width, logical port, nexus-loss timer enable, validity and context-type bits, remote SAS address low/high words, function number, arbitration wait fields, occupancy and inactivity timeouts, open-address-frame connection rate/features/source-zone/more-compatibility fields, and reserved words. `struct stp_remote_node_context` is a placeholder `u32 data[8]`. `union scu_remote_node_context` overlays SSP and STP formats.

Control flow: `remote_node_context.c` obtains the union entry from `ihost->remote_node_context_table`, zeroes one or more entries, fills the SSP view for both SAS and SATA devices, sets `is_valid` on post, clears it on invalidate, and posts 32-byte or 96-byte RNC commands depending on device type/topology. SAS address conversion is handled before writing the high/low fields.

State and persistence behavior: this header models hardware-visible persistent context RAM for the lifetime of an active remote device. The `is_valid` bit is the transition boundary between a staged context and one the SCU may consume. Timeout and OAF fields persist until the RNC is invalidated or rebuilt.

Dependencies/integration: consumed by host context-table storage and RNC construction. Values are coordinated with `scu_task_context.h` context commands and remote-node table allocation. Device parameters come from libsas domain devices and host user parameters.

Risks: C bitfield layout is compiler- and endian-sensitive, but this driver relies on it matching the SCU dword format. The STP structure is a placeholder while code still writes the SSP view for SATA-style devices, so future STP-specific fields would need coordinated changes. Incorrect `is_valid`, SAS address endianness, or port index fields can make every request fail with open reject or invalid RNC. Test signals include raw context dword inspection for SAS and SATA devices, post/invalidate bit toggling, direct versus expander SATA 32/96-byte posting, and timeout parameter propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_remote_node_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_task_context.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_task_context.h

Purpose: defines SCU hardware task-context command encodings, protocol task types, SGL formats, protocol-specific task-context overlays, and the packed 256-byte `struct scu_task_context` used for every posted request.

Important APIs/types: SSP task types include IO read/write, SMP request, response, raw frame, and primitive; SATA task types include DMA in/out, FPDMAQ read/write, packet DMA, and raw frame. Context command macros build post/dump TC, post/dump RNC, invalidate, suspend, resume, and nexus timer commands. Protocol constants select SMP, SSP, STP, or none. `struct ssp_task_context`, `stp_task_context`, `smp_task_context`, and `primitive_task_context` occupy the protocol-specific area. `struct scu_sgl_element` and `struct scu_sgl_element_pair` define SCU DMA SGL pairs. `struct transport_snapshot` and block-guard fields expose hardware progress and DIF state. The packed `struct scu_task_context` lays out common words, protocol union, command/response DMA addresses, task phase/status, SGL pairs, snapshots, and block protection controls.

Control flow: `request.c` zeroes and fills this structure before posting a TC. SSP sets protocol, remote node, frame type, IU lengths, command/response DMA pointers, task type, transfer length, SGLs, and optional DIF controls. SMP uses command IU address from the mapped SMP request and expects response via unsolicited frame. STP/SATA writes the first H2D FIS dword into the protocol area, points command IU past the first dword, programs FIS type, NCQ tag, transfer length, and SGLs. Abort handling sets `tc->abort = 1` before posting termination.

State and persistence behavior: each task context is hardware-visible DMA/SRAM state for one active TCi. Some fields are driver-written inputs, while snapshots, active SGL, task status, and block-guard error fields are hardware-updated/read-only from the driver's perspective. The first two SGL pairs live inside the TC; more pairs are chained from request-owned memory.

Dependencies/integration: included by `request.h` and `request.c`, and its RNC command macros are used by `remote_node_context.c`. It depends on exact controller specification offsets and on controller tag/RNI allocation. Linux DMA mapping provides the physical addresses programmed into command, response, and SGL fields.

Risks: this is a fragile hardware ABI: packing, bitfield order, field widths, and offsets must remain exact. `transfer_length_bytes` and SGL element lengths are 24-bit fields, so oversized transfers need splitting before reaching this layer. Command macro typo `SCU_CONTEXT_COMMAND_REQUST_POST_TC` is preserved and could confuse future users. DIF fields must be initialized consistently, or protection errors become hard to diagnose. Test signals include `sizeof(struct scu_task_context) == 256`, offset checks for SGL pairs and protocol union, SSP/SMP/STP task-context dumps, abort-bit posting, chained SGL DMA addresses, NCQ tag programming, and DIF read-strip/write-insert context values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_task_context.h -->
