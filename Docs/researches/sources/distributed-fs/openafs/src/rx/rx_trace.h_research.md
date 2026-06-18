# sources/distributed-fs/openafs/src/rx/rx_trace.h

## Purpose
Declares or disables RX call tracing hooks depending on `RXDEBUG`.

## Important APIs, Types, And Functions
Without `RXDEBUG`, `rxi_calltrace(a,b)` and `rxi_flushtrace()` expand to no-ops. With `RXDEBUG`, the header declares both functions and defines event IDs `RX_CALL_ARRIVAL`, `RX_CALL_START`, `RX_CALL_END`, and `RX_TRACE_DROP`.

## Control Flow
The header controls compile-time behavior: production builds compile tracing calls away, while debug builds route them to `rx_trace.c`.

## State And Persistence
No state is stored in the header. Debug builds rely on `rx_trace.c` globals and per-call trace timing fields.

## Dependencies And Integration Points
It forward-uses `struct rx_call` and is included by RX lifecycle code that wants low-cost tracing hooks.

## Risks And Test Signals
Risks are event ID drift and assuming trace side effects in non-debug builds. Compile coverage with and without `RXDEBUG` is the main signal.
