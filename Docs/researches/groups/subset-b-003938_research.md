<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.c

## Purpose
This file implements the Intel IRDMA privileged UDA helper queues used for iWARP/RoCE exception traffic: ILQ and IEQ. It owns PUDA resource creation/destruction, buffer-pool management, send and receive posting, CQ polling, and IEQ-specific reassembly of partial MPA FPDUs before sending completed data back through a loopback UDA send.

## Important APIs, Types, And Functions
- Public PUDA lifecycle and I/O APIs: `irdma_puda_create_rsrc()`, `irdma_puda_dele_rsrc()`, `irdma_puda_poll_cmpl()`, `irdma_puda_get_bufpool()`, `irdma_puda_ret_bufpool()`, `irdma_puda_send()`, and `irdma_puda_send_buf()`.
- Resource helpers allocate coherent CQ/QP memory, initialize `struct irdma_sc_cq` and `struct irdma_sc_qp`, issue CQP create/destroy commands, register PUDA CQs in `dev->ilq_cq`/`dev->ieq_cq`, and allocate `struct irdma_puda_buf` DMA buffers.
- Receive-path helpers include `irdma_puda_poll_info()`, `irdma_puda_post_recvbuf()`, `irdma_puda_replenish_rq()`, and `irdma_ilq_putback_rcvbuf()`.
- IEQ partial-FPDU handling is in `irdma_ieq_process_fpdus()`, `irdma_ieq_process_buf()`, `irdma_ieq_handle_partial()`, `irdma_ieq_get_fpdu_len()`, `irdma_ieq_compl_pfpdu()`, `irdma_ieq_handle_exception()`, `irdma_ieq_receive()`, and `irdma_ieq_cleanup_qp()`.
- The code depends on helpers declared elsewhere for TCP/IP parsing, AH creation/free, CRC checks, QP lookup, AE generation, and IEQ ACKs.

## Control Flow
`irdma_puda_create_rsrc()` allocates one resource per VSI, wires SQ/RQ tracking arrays after the resource object, initializes the PD, creates the CQ, creates the UDA QP, allocates `tx_buf_cnt + rq_size` DMA buffers, posts the initial receive queue, enables CRC checking for IEQ, and arms the CQ. Error paths call `irdma_puda_dele_rsrc()` to unwind by the `rsrc->cmpl` milestone.

Receive completions flow through `irdma_puda_poll_cmpl()`. It decodes a CQE with `irdma_puda_poll_info()`, validates the completion context and QP id, synchronizes the DMA buffer for CPU access, parses TCP/IP metadata, dispatches to the ILQ or IEQ receive callback, and either puts the ILQ receive buffer back in place or replenishes IEQ RQ entries. Send completions recover the buffer from SQ tracking, call the transmit completion callback, advance SQ availability, and drain `txpend` if queued buffers exist.

`irdma_puda_send_buf()` serializes SQ availability with `bufpool_lock`. If no send WQE is available or earlier buffers are pending, it queues the buffer on `txpend`; otherwise it builds `irdma_puda_send_info`, synchronizes the buffer, and calls `irdma_puda_send()` to write the UDA SEND WQE and ring the doorbell.

IEQ receives identify the real QP with `irdma_ieq_get_qp()` and then process exception traffic under `qp->pfpdu.lock`. The first buffer for a partial mode initializes `pfpdu->rcv_nxt`, `fps`, `max_fpdu_data`, and `rxlist`. Buffers are appended only when sequence and receive-window checks pass. GEN2+ may first create an AH from the received packet, then `irdma_ieq_process_fpdus()` walks ordered buffers, validates MPA markers and CRC, copies complete or reassembled FPDUs into transmit buffers, updates TCP/IP header fields, marks loopback, and sends them through the PUDA SQ.

## State And Persistence
State is in memory and hardware queues only. Persistent per-resource state includes the CQ, QP, PD, DMA memory blocks, SQ/RQ tracking arrays, receive indexes, invalid receive count, transmit availability, buffer pool, pending transmit list, allocation list, stats counters, and IEQ CRC/partial counters. Per-QP IEQ state lives in `struct irdma_pfpdu`: ordered receive list, next sequence state, first partial sequence, marker length, AH pointer, CRC/error flags, and counters. Memory barriers (`dma_wmb()`, `dma_rmb()`) and DMA sync calls protect device/CPU ownership transitions.

## Dependencies And Integration Points
The file integrates with the lower UK queue helpers in `uk.c`, SC object definitions in `type.h`, UDA hardware field macros in `uda_d.h`, CQP command helpers, work scheduler/QoS hooks, device/VSI state, TCP/IP parser helpers, AH management, and hardware generation checks. It publishes PUDA CQs through `struct irdma_sc_dev` so interrupt/CEQ paths can find the correct CQ.

## Risks And Edge Cases
The main risks are queue accounting errors, wrong polarity/valid-bit ordering, DMA ownership mistakes, and partial-FPDU list lifetime bugs. `avail_buf_count` is incremented outside the spinlock in `irdma_puda_ret_bufpool()`, so it is a snapshot rather than a strictly locked counter. IEQ partial handling must return all buffers to the pool on CRC, sequence, AH creation, or no-buffer failures. GEN1 and GEN2 WQE layouts diverge in several paths, increasing regression risk. Destruction skips CQP destroy on reset but still frees host memory, so callers must guarantee hardware is quiesced.

## Test Signals
Useful signals include module builds with both GEN1 and GEN2+ paths, PUDA resource create/destroy under injected CQP and allocation failures, CQ poll tests for RQ/SQ/error/extended CQEs, KASAN/KCSAN/leak checks on IEQ error cleanup, packet tests with IPv4/IPv6/VLAN/source-MAC extended CQEs, MPA marker and CRC fault injection, out-of-order IEQ sequence tests, and runtime counters for `stats_buf_alloc_fail`, `stats_rcvd_pkt_err`, `crc_err`, `bad_seq_num`, `partials_handled`, and `stats_sent_pkt_q`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.h

## Purpose
This header defines the PUDA contract for ILQ and IEQ resources: resource types, completion milestones, completion/send descriptors, DMA buffer layout, resource configuration, runtime resource state, and external PUDA/IEQ entry points.

## Important APIs, Types, And Functions
- `enum puda_rsrc_type` distinguishes ILQ and IEQ resources; `enum puda_rsrc_complete` tracks creation milestones used by cleanup.
- `struct irdma_puda_cmpl_info` captures decoded CQE metadata, including QP id, WQE index, payload length, protocol flags, VLAN, source MAC, and error code.
- `struct irdma_puda_send_info` is the compact send descriptor consumed by `irdma_puda_send()`.
- `struct irdma_puda_buf` represents one DMA-backed packet buffer and carries parsed header pointers, payload length, VLAN/source MAC flags, AH id, sequence number, loopback flag, and list/refcount state.
- `struct irdma_puda_rsrc_info` is the create-time input, while `struct irdma_puda_rsrc` is the long-lived CQ/QP/buffer-pool/statistics object.
- Prototypes expose PUDA resource creation, destruction, send, CQ polling, buffer-pool operations, IEQ QP lookup, TCP/IP update/parsing, MPA CRC handling, AH lifecycle, and IEQ cleanup.

## Control Flow
The header has no executable flow, but it defines the data flow used by `puda.c`: callers fill `irdma_puda_rsrc_info`, `irdma_puda_create_rsrc()` allocates and initializes `irdma_puda_rsrc`, receive completions populate `irdma_puda_cmpl_info`, packet buffers move among `bufpool`, RQ, `txpend`, and IEQ partial lists, and `irdma_puda_send_info` is assembled from a buffer before WQE emission.

## State And Persistence
All state is runtime kernel memory. `irdma_puda_rsrc` persists for the VSI ILQ/IEQ lifetime and owns coherent CQ/QP memory, virtual bookkeeping memory, allocated buffer list, free and pending lists, queue indexes, callbacks, and stats. `irdma_puda_buf` persists until resource teardown and is recycled across receive and transmit operations.

## Dependencies And Integration Points
The header depends on Linux list and refcount primitives, DMA and virtual memory wrappers, Ethernet address sizing, and IRDMA SC types from neighboring headers. It is included by PUDA implementation and by connection-management/offload code that needs IEQ cleanup, AH construction, or PUDA sends.

## Risks And Edge Cases
The comment that `list` must be first in `irdma_puda_buf` is a real ABI-with-local-code constraint because list nodes are cast back to buffers. Mis-sizing `buf_size`, SQ/RQ counts, or callback pointers in `irdma_puda_rsrc_info` can break resource creation or packet processing. Counters are plain `u64` and mostly diagnostic, not synchronized accounting.

## Test Signals
Compile coverage should catch prototype drift. Runtime signals are successful ILQ/IEQ creation, nonzero buffer pool counts, correct callback dispatch, no list corruption under debug list/KASAN, and cleanup that frees all `alloc_buf_count` buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace.c

## Purpose
This file instantiates the IRDMA connection-management tracepoints and provides string/format helpers used by `trace_cm.h` trace events.

## Important APIs, Types, And Functions
- `CREATE_TRACE_POINTS` plus `#include "trace.h"` causes the tracepoint definitions included through `trace_cm.h` to be emitted in exactly one C translation unit.
- `print_ip_addr()` formats IPv4 or IPv6 address and port data into a `trace_seq`.
- `parse_iw_event_type()` maps `enum iw_cm_event_type` values to readable strings.
- `parse_cm_event_type()` maps IRDMA internal CM event values to readable strings.
- `parse_cm_state()` maps `enum irdma_cm_node_state` values to readable strings.

## Control Flow
Trace events call these helpers during `TP_printk` rendering. `print_ip_addr()` takes the current trace sequence buffer pointer, appends the formatted address, terminates it with NUL, and returns the original pointer. The parse helpers use switch statements and return `"Unknown"` or `"Bad state"` for out-of-range values.

## State And Persistence
There is no persistent driver state. The only state is transient `trace_seq` output while a trace record is rendered. The tracepoint objects generated by the include are kernel tracing infrastructure state.

## Dependencies And Integration Points
The file depends on `trace.h`, which includes `trace_cm.h`, Linux trace sequence APIs, CM enums from `main.h`, and IW CM event enums. It integrates with ftrace/perf tracepoint consumers and all CM code sites that invoke the generated `trace_irdma_*` functions.

## Risks And Edge Cases
The IPv4 path uses network-byte-order conversion before `%pI4`; port formatting uses `htons(port)`, so any caller already passing network-order ports would display incorrectly. Missing enum cases degrade to generic strings, which is safe but can hide new states in logs.

## Test Signals
Build success confirms single tracepoint instantiation. Enabling `irdma_cm:*` trace events should show readable CM states/events and correct IPv4/IPv6 address strings during connection setup, teardown, listener creation, and AH activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace.h

## Purpose
This tiny umbrella header connects the IRDMA trace translation unit to the connection-management tracepoint definitions.

## Important APIs, Types, And Functions
- It contains only the SPDX/copyright header and `#include "trace_cm.h"`.
- Its role is to give `trace.c` a stable include target while keeping actual trace event definitions in `trace_cm.h`.

## Control Flow
There is no runtime flow. At compile time, including this header includes all `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` declarations from `trace_cm.h`.

## State And Persistence
No state is declared here. Generated tracepoint state comes from `trace_cm.h` when included with `CREATE_TRACE_POINTS`.

## Dependencies And Integration Points
It depends directly on `trace_cm.h` and indirectly on Linux tracepoint headers and `main.h`. It integrates the single-instantiation pattern used by kernel tracepoints.

## Risks And Edge Cases
Because it is only an include shim, the main risk is accidental addition of unrelated declarations or include ordering that breaks `CREATE_TRACE_POINTS`. If future trace categories are added, this header may need to include more trace headers.

## Test Signals
Successful compilation of `trace.c` and availability of `irdma_cm` trace events are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace_cm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace_cm.h

## Purpose
This header defines Linux tracepoints for IRDMA connection-management activity. It covers listener lifecycle, TOS/DCB decisions, multicast/qhash setup, address resolution, IW CM event delivery, internal CM node transitions, open errors, and AH creation/free events.

## Important APIs, Types, And Functions
- Helper declarations: `print_ip_addr()`, `parse_iw_event_type()`, `parse_cm_event_type()`, and `parse_cm_state()`.
- `TRACE_SYSTEM irdma_cm` names the tracepoint subsystem.
- Standalone events include `irdma_create_listen`, `irdma_dec_refcnt_listen`, `irdma_negotiate_mpa_v2`, `irdma_addr_resolve`, `irdma_send_cm_event`, and `irdma_send_cm_event_no_node`.
- Event classes reduce duplication: `listener_template`, `tos_template`, `qhash_template`, `cm_node_template`, `open_err_template`, and `cm_node_ah_template`.
- Derived events include `irdma_find_listener`, `irdma_del_multiple_qhash`, `irdma_listener_tos`, `irdma_dcb_tos`, `irdma_add_mqh_6`, `irdma_add_mqh_4`, `irdma_create_event`, `irdma_accept`, `irdma_connect`, `irdma_reject`, `irdma_find_node`, `irdma_send_reset`, `irdma_rem_ref_cm_node`, `irdma_cm_event_handler`, `irdma_active_open_err`, `irdma_passive_open_err`, `irdma_cm_free_ah`, and `irdma_create_ah`.

## Control Flow
Each tracepoint defines a `TP_PROTO`, `TP_ARGS`, record layout, fast assignment block, and print format. CM code invokes generated `trace_irdma_*()` functions; the fast assignment copies pointer values, refcounts, ports, VLANs, state, acceleration flags, MAC addresses, and local/remote IP arrays into the trace record. Print formatting then calls the helper functions from `trace.c`.

## State And Persistence
Trace records are transient kernel tracing data. The header itself persists no driver state, but it snapshots CM object fields such as listener state, CM node refcount, CM node state, address tuples, VLAN id, AH pointer, and caller symbol for postmortem analysis.

## Dependencies And Integration Points
The file depends on Linux tracepoint and trace sequence APIs, `main.h` definitions for `struct irdma_device`, `struct irdma_cm_listener`, `struct irdma_cm_node`, `struct irdma_cm_info`, and IW CM types. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` are set so `<trace/define_trace.h>` can generate tracepoint code from the driver directory.

## Risks And Edge Cases
Tracepoint layouts are a userspace-observable diagnostics ABI; field renames or semantic changes can break scripts. Dynamic arrays copy four `u32` address slots for both IPv4 and IPv6, so callers must keep address storage compatible. The `irdma_dec_refcnt_listen` event records a `refcnt` field but does not assign it in the visible fast assignment, so printed or consumed refcount data would be uninitialized if used. Pointer and caller-symbol logging is diagnostic only and should not be treated as stable identity across lifetimes.

## Test Signals
Build with tracing enabled, inspect `/sys/kernel/tracing/events/irdma_cm`, and exercise active/passive connection setup, listener lookup/deletion, MPA negotiation, qhash programming, open errors, and AH creation/free while confirming event fields and formatted addresses are coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/type.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/type.h

## Purpose
This is the central shared type and prototype header for the IRDMA low-level hardware driver. It defines debug categories, protocol/error enums, hardware stats indexes, SC object layouts, QP/CQ/CEQ/AEQ/CQP/VSI/device state, offload context structures, CQP command payload unions, and SC-layer function prototypes.

## Important APIs, Types, And Functions
- Enumerations cover page sizes, terminate layers/errors, hardware statistics, firmware features, scheduling priority, VF/PF identity, HMC profiles, qhash entry/manage types, reserved CQ/QP ids, and queue types.
- Core runtime types include `struct irdma_hw`, `irdma_sc_dev`, `irdma_sc_vsi`, `irdma_sc_cqp`, `irdma_sc_qp`, `irdma_sc_cq`, `irdma_sc_srq`, `irdma_sc_ceq`, `irdma_sc_aeq`, `irdma_sc_pd`, and `irdma_pfpdu`.
- Offload and context types include TCP, UDP, RoCE, iWARP, QP host context, AEQE, MR/STag, qhash, ARP, APBVT, push-page, stats, QoS, and work-scheduler payloads.
- `union cqp_info` inside `struct cqp_info` models the parameter set for each CQP operation, and `struct cqp_cmds_info` is the queued command wrapper.
- Prototypes expose SC operations for CCQ/CEQ/AEQ/CQP/QP/CQ/SRQ lifecycle, QP modify/flush, fast register, static HMC pages, stats updates, and queue context setup.
- `irdma_sc_cqp_get_next_send_wqe()` is an inline wrapper around the indexed CQP WQE allocator.

## Control Flow
The header does not execute logic beyond the inline CQP WQE wrapper, but it defines the control contracts used by the driver. Initialization code fills `irdma_device_init_info`, `irdma_cqp_init_info`, `irdma_vsi_init_info`, and queue init info structs. CQP producers fill a `cqp_cmds_info` union arm, queue or post it, and CQP completion handling uses `irdma_ccq_cqe_info`. QP/CQ creation uses host context info and UK init substructures, then lower functions emit hardware WQEs using the fields defined here.

## State And Persistence
All structures describe in-memory kernel and hardware-facing state. `irdma_sc_dev` persists for device lifetime and owns MMIO doorbells, feature registers, HMC/FPM buffers, CQP/AEQ/CEQ/CCQ pointers, PUDA CQ pointers, QoS/work-scheduler state, virtual channel state, and locks. `irdma_sc_vsi` persists per virtual station interface and owns ILQ/IEQ resources, QoS mappings, MTU, stats, and callbacks. `irdma_sc_qp` and `irdma_sc_cq` persist per queue object and embed UK-level rings plus hardware addresses. `irdma_pfpdu` persists per QP for IEQ partial-FPDU processing.

## Dependencies And Integration Points
The header includes `osdep.h`, `irdma.h`, `user.h`, `hmc.h`, `uda.h`, `ws.h`, and `virtchnl.h`. It is consumed by most IRDMA implementation files and bridges Linux RDMA core objects to hardware command formats. It also integrates PUDA by storing `ilq`, `ieq`, `ilq_cq`, and `ieq_cq` pointers in VSI/device structs.

## Risks And Edge Cases
Because this file centralizes shared structure layout, small field changes can break many hardware WQE/context writers. Bitfield state such as `ceq_valid`, `stats_idx_valid`, `flush_sq/rq`, `virtual_map`, and offload-valid flags must match hardware command construction. Stats indexes vary by hardware generation. The CQP union requires callers and command dispatchers to agree exactly on `cqp_cmd`. Some fields are protected by specific locks or mutexes noted in comments, and misuse can cause races in QoS, CQP queues, virtual channel messaging, or PUDA CQ pointers.

## Test Signals
Full driver build coverage is the first signal. Runtime validation should cover device init/teardown, VSI creation, CQP command submission/completion, QP/CQ/SRQ lifecycle, stats gather, QoS/work-scheduler changes, virtual channel paths, IEQ partial mode, and sparse/pahole-style layout checks when hardware context code changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.c

## Purpose
This file implements UDA CQP operations for address handles and multicast groups. It writes hardware WQEs for create/destroy AH and create/modify/destroy multicast group contexts, and maintains the software multicast group membership array.

## Important APIs, Types, And Functions
- `irdma_sc_access_ah()` builds and posts a Manage Address Vector CQP WQE from `struct irdma_ah_info`.
- `irdma_access_mcast_grp()` builds and posts a Manage Multicast Group CQP WQE from `struct irdma_mcast_grp_info`.
- `irdma_create_mg_ctx()` serializes valid multicast group entries into the DMA context block consumed by hardware.
- `irdma_sc_add_mcast_grp()` adds or reference-counts a `(dest_port, qp_id)` entry in software context.
- `irdma_sc_del_mcast_grp()` decrements use count, invalidates entries, decrements `no_of_mgs`, and compacts the array when removing a non-last entry.
- `irdma_compare_mgs()` is the equality predicate used by add/delete.

## Control Flow
AH access gets the next CQP SQ WQE, writes destination MAC, PD index, traffic class or hop limit, VLAN, ARP index, flow label, IPv4 or IPv6 source/destination addresses, then publishes the WQE header with valid bit, opcode, loopback, IPv4, AH index, and VLAN insertion flags before posting the CQP SQ.

Multicast access validates `mg_id`, allocates a CQP WQE, rebuilds the DMA multicast context from current valid entries, writes context physical address, VLAN/QS handle, destination MAC, HMC function id, destination IP address, and finally publishes a header containing opcode, multicast group index, VLAN validity, and IP version.

Software add scans for an identical valid entry first and increments `use_cnt` if found; otherwise it records the first free slot and initializes it. Delete scans for a matching valid entry, decrements `use_cnt`, invalidates it when the count reaches zero, and moves the last valid entry into the gap to keep packed context ordering.

## State And Persistence
AH state is held in hardware after the CQP command and described by caller-owned `irdma_ah_info`/`irdma_sc_ah`. Multicast software state is `mg_ctx_info[]`, `valid_entry`, `use_cnt`, and `no_of_mgs`; hardware-facing state is the DMA buffer `dma_mem_mc`. CQP WQEs are transient but posted to persistent hardware queues.

## Dependencies And Integration Points
The file depends on `type.h`, `protos.h`, `uda.h`, `uda_d.h`, CQP WQE allocation/posting, `FIELD_PREP` bitfield macros, DMA ordering, and Ethernet address conversion. It is used by RDMA verbs/CM paths that create AHs and join/leave multicast groups, and by IEQ GEN2+ AH creation in `puda.c`.

## Risks And Edge Cases
The add/delete functions do not lock the multicast context, so callers must serialize membership changes. `irdma_sc_del_mcast_grp()` compaction assumes valid entries are packed in the first `no_of_mgs` slots; external mutation could break that invariant. AH and multicast WQE field placement is generation/hardware-contract sensitive. `mg_id` is range checked, but AH indexes and PD/ARP values are trusted inputs.

## Test Signals
Test AH create/destroy for IPv4, IPv6, VLAN insertion, loopback, and varied PD indexes. Test multicast add/delete duplicate membership, last-entry removal, middle-entry compaction, full context returning `-ENOMEM`, invalid `mg_id`, and emitted CQP completions for create/modify/destroy operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.h

## Purpose
This header declares UDA address-handle and multicast management interfaces and defines the software address-handle structures used by the IRDMA SC layer.

## Important APIs, Types, And Functions
- Constants define UDA scaling limits: `IRDMA_UDA_MAX_FSI_MGS`, `IRDMA_UDA_MAX_PFS`, and `IRDMA_UDA_MAX_VFS`.
- `struct irdma_ah_info` contains VSI, PD index, ARP index, source/destination IP addresses, flow label, AH index, VLAN tag, insert-VLAN flag, traffic class/TOS, hop limit/TTL, destination MAC, and validity flags.
- `struct irdma_sc_ah` binds an AH info block to the SC device.
- Function declarations cover AH access and multicast access plus software multicast add/delete.
- Inline wrappers translate create/destroy AH and create/modify/destroy multicast group calls into CQP opcodes.

## Control Flow
Callers initialize `irdma_sc_ah` with `irdma_sc_init_ah()`, fill `irdma_ah_info`, and then call inline create/destroy wrappers that delegate to `irdma_sc_access_ah()`. Multicast callers fill `irdma_mcast_grp_info`, update the software group entries with add/delete helpers, and issue create/modify/destroy through `irdma_access_mcast_grp()`.

## State And Persistence
The header defines no storage. AH state persists in caller-owned `struct irdma_sc_ah` and hardware address-vector table entries. Multicast state persists in `irdma_mcast_grp_info` structures defined elsewhere and in hardware after CQP commands.

## Dependencies And Integration Points
It depends on SC device/VSI and CQP types, multicast group types from other IRDMA headers, and CQP opcode constants. It is included by `type.h`, `uda.c`, and other code that needs AH creation for CM, RoCE UD, multicast, or IEQ handling.

## Risks And Edge Cases
The inline wrappers hide opcode selection but do not validate inputs. `irdma_ah_info` contains both IPv4/IPv6 arrays and validity flags; callers must fill the correct lanes and byte order expected by hardware WQE construction.

## Test Signals
Compile checks should catch signature drift. Runtime signals are successful AH create/destroy CQP completions and multicast group create/modify/destroy flows using the inline wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda_d.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda_d.h

## Purpose
This header defines UDA hardware descriptor bit constants for SQ WQEs, UDA QP context fields, Manage Address Vector CQP WQEs, multicast group context/WQEs, and qhash programming.

## Important APIs, Types, And Functions
- L4 and inner IP packet type constants define values used in UDA send descriptors.
- `IRDMA_UDA_QPSQ_*` macros describe UDA SQ WQE fields such as push, inline data, fragment count, checksum, AH index, protocol, MAC/IP/L4 lengths, multicast, loopback, and immediate data.
- `IRDMA_UDAQPC_*` macros describe UDA QP context fields, many aliased to generic QP context masks.
- `IRDMA_UDA_CQPSQ_MAV_*` macros define address-vector CQP WQE fields used by `irdma_sc_access_ah()`.
- `IRDMA_UDA_MGCTX_*` and `IRDMA_UDA_CQPSQ_MG_*` define multicast context and multicast CQP WQE fields.
- `IRDMA_UDA_CQPSQ_QHASH_*` defines qhash table programming fields for destination/source ports, addresses, QPN, management operation, IP version, LAN forwarding, and entry type.

## Control Flow
There is no executable flow. The macros are consumed by WQE/context writers through `FIELD_PREP()` and `FIELD_GET()` so numeric values are placed into exact hardware bit positions.

## State And Persistence
No runtime state is stored here. The constants determine the persistent binary layout written into device-visible WQEs, QP contexts, multicast contexts, and qhash commands.

## Dependencies And Integration Points
The header relies on Linux bit macros such as `BIT_ULL()` and `GENMASK_ULL()` and generic IRDMA QP context masks. It is included by `uda.c` and other WQE writers for UDA and qhash operations.

## Risks And Edge Cases
Any incorrect mask or line selector corrupts hardware descriptors in ways that may surface as CQP failures, malformed packets, or silent offload misbehavior. Several macros alias generic QP context fields, so changes in generic definitions affect UDA. The typo-like `IRDMA_UDA_CQPSQ_MAV_DOLOOPBACKK` name is part of local API use and should not be casually renamed without updating consumers.

## Test Signals
Build coverage catches missing macro names. Hardware or emulation tests should validate AH programming, UDA send WQEs, multicast group programming, qhash programming, VLAN and IPv4/IPv6 variants, and descriptor dumps against hardware specifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda_d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uk.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uk.c

## Purpose
This file implements the IRDMA user/kernel shared queue mechanics: SQ/RQ/SRQ WQE construction, CQ polling, ring advancement, inline-data packing, generation-specific WQE helpers, queue depth/shift calculation, and QP/CQ/SRQ UK initialization.

## Important APIs, Types, And Functions
- WQE allocation/posting helpers: `irdma_qp_get_next_send_wqe()`, `irdma_qp_get_next_recv_wqe()`, `irdma_srq_get_next_recv_wqe()`, `irdma_uk_qp_post_wr()`, `irdma_nop()`, and internal `irdma_nop_1()`.
- Send operations: `irdma_uk_rdma_write()`, `irdma_uk_rdma_read()`, `irdma_uk_send()`, `irdma_uk_inline_rdma_write()`, `irdma_uk_inline_send()`, `irdma_uk_atomic_fetch_add()`, `irdma_uk_atomic_compare_swap()`, and `irdma_uk_stag_local_invalidate()`.
- Receive operations: `irdma_uk_post_receive()` and `irdma_uk_srq_post_receive()`.
- Completion operations: `irdma_uk_cq_poll_cmpl()`, `irdma_uk_cq_empty()`, `irdma_uk_cq_request_notification()`, `irdma_uk_cq_resize()`, `irdma_uk_cq_set_resized_cnt()`, and `irdma_uk_clean_cq()`.
- Init/sizing helpers: `irdma_get_wqe_shift()`, `irdma_get_sqdepth()`, `irdma_get_rqdepth()`, `irdma_get_srqdepth()`, `irdma_uk_qp_init()`, `irdma_uk_cq_init()`, `irdma_uk_srq_init()`, `irdma_uk_calc_shift_wq()`, and depth/fragment conversion helpers.
- `iw_wqe_uk_ops` and `iw_wqe_uk_ops_gen_1` select generation-specific fragment, inline, and memory-window writers.

## Control Flow
SQ posting starts by validating SGE counts and inline sizes, calculating total transfer length and required WQE quanta, then calling `irdma_qp_get_next_send_wqe()`. That allocator ensures the WQE does not cross an unsupported hardware chunk boundary by padding with NOPs when needed, advances the SQ head by quanta, toggles polarity on wrap, and records WR tracking. Operation-specific code writes fragments, remote addresses, immediate data, AH/QKey/QPN fields, fences, opcode, completion-signaling, and valid bit after `dma_wmb()`. Optional `post_sq` rings the doorbell.

RQ and SRQ posting atomically advance the receive ring head, write fragment descriptors, store WR ids, publish the valid bit after a DMA barrier, and update SRQ shadow state. CQ polling validates polarity, handles extended CQEs, decodes immediate data, UD VLAN/source MAC, QP context, status, operation, WQE index, payload length, invalidated STag, and solicited events. It advances SQ/RQ/SRQ tails and CQ head/tail, but during flush it can park the CQ head and synthesize additional software completions for remaining WQEs on older hardware.

Initialization functions install ring bases, doorbells, shadow areas, queue sizes, fragment limits, WQE-size multipliers, polarity defaults, generation-specific ops, and connection-reserved WQE handling.

## State And Persistence
The persistent state is the UK portions of QPs, CQs, and SRQs: ring head/tail, base pointers, doorbells, shadow areas, WR tracking arrays, receive WR id arrays, polarity bits, flush flags, max fragment/inline limits, WQE operation table, and queue sizes. WQEs and CQEs are hardware-visible memory, so valid-bit ordering and DMA barriers are part of state correctness.

## Dependencies And Integration Points
The file depends on `user.h` for operation structures and status enums, `irdma.h`/`defs.h` for bit masks and ring macros, Linux RDMA `ib_sge`, MMIO `writel()`, and memory barriers. It is used by both kernel and user-mapped queue paths and by higher SC/PUDA code that embeds `struct irdma_qp_uk` and `struct irdma_cq_uk`.

## Risks And Edge Cases
High-risk areas are WQE quanta calculation, chunk padding, valid-bit polarity on wrap, GEN1 versus GEN2+ layout differences, inline-data packing, flush CQE synthesis, and keeping SQ/RQ tails synchronized with hardware CQEs. Unsigned ring arithmetic and untrusted SGE counts are guarded, but regressions can produce memory corruption or stuck queues. CQ polling treats non-signaled SQ completions as unexpected except in flush paths, so caller expectations must match signaled tracking.

## Test Signals
Test RDMA write/read/send, inline variants, immediate data, atomics, local invalidate, RQ and SRQ receives, CQ notification, CQ resize, clean CQ, flush completions, queue wrap, chunk-boundary padding, maximum SGE limits, max inline limits, GEN1 and GEN2+ descriptor layouts, and doorbell/ring state under stress. KASAN/KCSAN and hardware CQE dumps are valuable for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/user.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/user.h

## Purpose
This header defines the IRDMA shared user/kernel queue ABI types and constants: handles, access flags, operation codes, async event codes, device limits, completion status enums, post structures, CQ poll results, UK QP/CQ/SRQ structures, function prototypes, and AE-to-flush error mapping.

## Important APIs, Types, And Functions
- Handle aliases and memory access flags define local/remote read/write, bind-window, and zero-based access semantics.
- Operation codes cover RDMA write/read, send variants, bind MW, fast register, invalidate, NOP, atomics, and receive completions.
- Async event constants classify AMP, UDA, CQ, RDMA/DDP/RoCE, LLP, reset, terminate, catastrophic, suspend, and adapter failures.
- Device capability constants define WQE/CQE/AEQE sizes, max QP/CQ/CEQ ids, max fragments, max message sizes, max inline data, Q2/QP context sizes, and queue limits.
- Work request structures include `irdma_post_sq_info`, `irdma_post_send`, `irdma_rdma_write`, `irdma_rdma_read`, `irdma_bind_window`, atomics, local invalidate, and `irdma_post_rq_info`.
- Queue structures include `irdma_ring`, `irdma_qp_uk`, `irdma_cq_uk`, `irdma_srq_uk`, init-info structs, `irdma_sq_uk_wr_trk_info`, `irdma_qp_quanta`, `irdma_cqe`, and `irdma_extended_cqe`.
- `irdma_ae_to_qp_err_code()` maps hardware AE ids to flush codes and QP event types.

## Control Flow
The header is mostly declarative. `uk.c` consumes these structures to post WQEs and poll CQEs. Callers fill `irdma_post_sq_info` with operation-specific union data and flags; post functions validate and encode it. Completion polling fills `irdma_cq_poll_info`. The inline AE mapping switch converts low-level AE ids into the completion flush code/event type exposed to upper layers.

## State And Persistence
The UK structures persist for QP/CQ/SRQ lifetimes and may be shared with user mappings depending on the wider driver path. They store ring positions, queue bases, doorbells, WR ids, shadow areas, polarity, flush/destroy state, queue caps, and generation-specific operation tables. Constants here define the stable numeric protocol between driver code, hardware descriptors, and user/kernel queue handling.

## Dependencies And Integration Points
The header depends on Linux integer types, `struct ib_sge`, spinlocks, MMIO pointers, and hardware attribute definitions from other IRDMA headers. It is included by `uk.c`, `type.h`, and higher layers that construct WRs or interpret completions.

## Risks And Edge Cases
Because this file is ABI-like, changing constants, enum numeric values, structure layout, or operation codes can break userspace/provider compatibility. AE mapping defaults unknown events to general fatal/catastrophic behavior, which is conservative but may hide new precise error types. Queue structures hold raw pointers and MMIO addresses, so initialization must be complete before use.

## Test Signals
Compile tests should catch prototype drift. ABI/layout review, userspace verbs tests, CQ error/flush tests for many AE codes, max-SGE and inline boundary tests, and mixed kernel/user queue operation coverage are the important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/user.h -->
