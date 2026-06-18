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
