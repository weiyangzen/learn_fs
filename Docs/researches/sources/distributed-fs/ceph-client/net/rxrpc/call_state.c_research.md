# sources/distributed-fs/ceph-client/net/rxrpc/call_state.c

## Purpose
`call_state.c` centralizes terminal call-state changes. It records completion, abort, and local pre-start failure outcomes and provides the single point that wakes waiters and notifies the socket when a call becomes complete.

## Important APIs and functions
- `rxrpc_set_call_completion()` stores completion class, abort code, and errno, transitions the state to `RXRPC_CALL_COMPLETE`, traces, wakes `call->waitq`, and notifies the socket.
- `rxrpc_call_completed()` records normal success.
- `rxrpc_abort_call()` records a local abort and transmits an ABORT packet if the call has been exposed.
- `rxrpc_prefail_call()` marks calls complete and released before they are fully started, used for allocation/attachment failures.

## Control flow
Most files call into this module rather than writing completion fields directly. Input uses it for remote aborts and protocol failures, call event uses it for timeout/reset, connection event uses it when a connection abort propagates to calls, and object/accept code uses prefail for setup errors.

## State and persistence behavior
Completion data is written before the state transition. `rxrpc_set_call_state()` in the header uses release semantics, and readers use acquire semantics through `rxrpc_call_state()`. This permits lockless readers to see consistent `completion`, `abort_code`, and `error` after observing `RXRPC_CALL_COMPLETE`.

## Dependencies and integration points
It depends on output ABORT transmission, socket notification, tracepoints, and wait queues. It intentionally does not release object references; lifecycle cleanup remains in `call_object.c` and `call_event.c`.

## Risks
Double completion must be harmless; `rxrpc_set_call_completion()` returns false if the call is already complete. `rxrpc_prefail_call()` sets `RXRPC_CALL_RELEASED`, so callers must not later release the same call as a normal live socket call.

## Test signals
Check double-completion behavior, abort packet emission only for exposed calls, waiter wakeups, recvmsg notification, memory-ordering assumptions under KCSAN, and setup failure cleanup paths.
