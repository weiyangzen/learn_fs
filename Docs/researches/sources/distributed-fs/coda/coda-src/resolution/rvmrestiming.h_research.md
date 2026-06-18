# sources/distributed-fs/coda/coda-src/resolution/rvmrestiming.h

Purpose: defines timing probe identifiers for RVM-backed resolution paths. It mirrors generic resolution probe ids and adds recoverable-directory-resolution phase probes.

Important APIs/types: it declares `extern int pathtiming`, `extern int probingon`, `MAXPROBES`, and the `PROBE(info, num)` macro that conditionally calls `timing_path::insert`. `RecovTimingBase` starts the RVM-specific range, covering coordinator and subordinate phase 1, phase 2, phase 3, compensation, perform operation, phase 3.5/34, and phase 4 begin/end points. It also repeats older generic directory/file resolution ids for shared instrumentation consumers.

Control flow and integration: included by coordinator and subordinate resolution phase files. Probe calls bracket RPC phases, compensation computation, semantic execution, and final install/handle-inconsistency work.

State/persistence: no persistent state; writes are to process-local timing objects such as `tpinfo`. Risks include duplicated constants with `timing.h`, macro multi-evaluation of `info`, and dependence on external synchronization because `timing_path` is not internally locked. Test signals are probe traces that show balanced begin/end ids for successful and failed resolution runs and no out-of-range ids under `MAXPROBES`.
