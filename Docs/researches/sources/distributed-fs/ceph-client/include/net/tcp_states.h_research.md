# sources/distributed-fs/ceph-client/include/net/tcp_states.h

## Purpose

`tcp_states.h` defines the numeric values stored in TCP sockets' `sk_state` field and the matching bitmask constants used by TCP, inet diagnostics, polling, timers, and state tests.

## Important APIs, types, and functions

The anonymous state enum declares `TCP_ESTABLISHED`, `TCP_SYN_SENT`, `TCP_SYN_RECV`, `TCP_FIN_WAIT1`, `TCP_FIN_WAIT2`, `TCP_TIME_WAIT`, `TCP_CLOSE`, `TCP_CLOSE_WAIT`, `TCP_LAST_ACK`, `TCP_LISTEN`, `TCP_CLOSING`, `TCP_NEW_SYN_RECV`, `TCP_BOUND_INACTIVE`, and `TCP_MAX_STATES`. It also defines `TCP_STATE_MASK`, `TCP_ACTION_FIN`, and `TCPF_*` bitmask constants for each state.

## Control flow

There are no functions. The control-flow contract is that TCP state-machine code writes one of these numeric states to `sk_state`, while readers compare state values directly or use the `TCPF_*` masks to test allowed sets of states.

## State and persistence behavior

The header owns no state. Its numeric assignments are ABI-like within the kernel: changing them affects socket state tests, diagnostics, tracepoints, and any logic storing state masks.

## Dependencies and integration points

It is included by TCP, inet, time-wait, request-sock, diagnostics, and networking code that needs symbolic TCP state names. `TCP_BOUND_INACTIVE` is a pseudo-state for inet diagnostics rather than a normal TCP wire state.

## Risks and test signals

Risks are mostly compatibility and bitmask correctness. Reordering states or adding states without updating masks can break diagnostics and state transitions. Tests should cover TCP connection lifecycle states, inet_diag state reporting, mask-based filters, time-wait handling, and compile-time consumers expecting `TCP_MAX_STATES` at the end.
