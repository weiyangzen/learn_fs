# sources/distributed-fs/openafs/src/rx/rx_trace.c

## Purpose
Implements optional RX call tracing under `RXDEBUG` and a `DUMPTRACE` reader utility.

## Important APIs, Types, And Functions
When tracing is disabled, it defines `rxi_tracename` as a diagnostic string and optional no-op `main`. Under `RXDEBUG`, it defines `rxi_tracename`, `rxi_logfd`, `rxi_tracebuf`, `rxi_tracepos`, private `struct rx_trace`, `rxi_flushtrace`, `rxi_calltrace`, and optionally a dump utility `main`.

## Control Flow
`rxi_calltrace` returns immediately when tracing is disabled by a leading NUL in `rxi_tracename`. Otherwise it lazily opens the trace file, timestamps the event, records connection ID, call number, queue length, service/wait timings depending on event type, appends the binary record to a 4096-byte buffer, and flushes when nearly full. `rxi_flushtrace` writes buffered bytes and resets the position. `DUMPTRACE` reads records and prints human-readable event lines.

## State And Persistence
Runtime state includes the trace file path, file descriptor, buffer, buffer offset, and per-call `traceStart`/`traceWait` fields. When enabled, trace records persist to the configured file path.

## Dependencies And Integration Points
The file depends on RX debug configuration, `rx_globals.h`, `rx_internal.h`, `rx_trace.h`, `rx_conn.h`, `rx_call.h`, and clock/atomic helpers. Server scheduling and call lifecycle code call `rxi_calltrace` through macros declared in `rx_trace.h`.

## Risks And Test Signals
Risks include binary trace format portability, permissive trace file mode, unsynchronized global buffer access in multi-threaded debug builds, silent write errors, and stale path activation semantics. Test signals include enabling trace with `RXTRACEON` or patched pathname, call arrival/start/end/drop records, flush behavior, and `DUMPTRACE` output.
