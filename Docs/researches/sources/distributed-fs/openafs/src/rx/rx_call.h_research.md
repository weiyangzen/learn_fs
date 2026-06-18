# Research: sources/distributed-fs/openafs/src/rx/rx_call.h

## sources/distributed-fs/openafs/src/rx/rx_call.h

### Purpose
`rx_call.h` defines the internal `struct rx_call` and application-facing per-call substructure used by RX data marshalling, packet queues, scheduling events, retransmission state, congestion control, status, and reference management.

### Important Types and Fields
- `struct rx_call_appl` holds unlocked application-thread state: iovec queue, current packet, current vector position, mode, and byte counters.
- `struct rx_call` contains queue links, transmit/receive queues, channel, state, optional locks/condition variables, parent connection, call number pointer, flags, status/error fields, receive/transmit sequence windows, congestion state, RTT/RTO values, scheduled events, abort throttling state, arrival callback, timing fields, MTU, optional refcount/debug fields, current readv/writev vectors, and xmit list.
- Reference macros `CALL_HOLD`, `CALL_RELE`, `CALL_HOLD_R`, and `CALL_RELE_R` manage refcounts under `rx_refcnt_mutex` when locks are enabled; `RX_REFCOUNT_CHECK` adds per-hold-type diagnostics.

### Control Flow and State
This header defines the state layout manipulated by `rx.c`, `rx_rdwr.c`, `rx_packet.c`, `rx_multi.c`, and event callbacks. A call transitions through states defined in `rx.h`, carries packet queues while active or dallying, and uses scheduled events for resend, keepalive, delayed ACK, delayed abort, and MTU growth. Application marshalling state is intentionally accessible while the call lock is not held, except when `RX_CALL_IOVEC_WAIT` allows other thread intervention.

### Dependencies and Integration Points
The structure depends on `opr_queue`, `rx_packet`, `rx_connection`, `rxevent`, `struct clock`, and RX locking globals. `arrivalProc` is used by multi-RX orchestration and by lower RX receive paths. The layout is central to packet send/receive, read/write, timeout, and debug code.

### Risks and Edge Cases
- Several fields are accessed without the call lock by design; changing ownership rules can introduce races.
- Refcount macros become no-ops without `RX_ENABLE_LOCKS`, so lifetime assumptions differ across builds.
- `xmitList` is bounded by `RX_MAXACKS`; ACK parsing and retransmission must not exceed it.
- Event pointers require careful cancellation and reference handling to avoid use-after-free.

### Test Signals
Regression tests should cover call lifecycle, refcount leak diagnostics, delayed ACK/resend/keepalive cancellation, readv/writev concurrency constraints, and debug packet queue counters when enabled.
