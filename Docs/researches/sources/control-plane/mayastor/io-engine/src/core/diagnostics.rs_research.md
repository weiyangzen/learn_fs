# sources/control-plane/mayastor/io-engine/src/core/diagnostics.rs

## Purpose
Implements reactor/process diagnostics, primarily stack dumping when reactor freeze detection decides a reactor has stopped responding.

## Important APIs, Types, and Functions
- `diagnose_reactor(&Reactor)` logs core, TID, and state, then spawns stack collection.
- `process_diagnostics_cli(&MayastorCliArgs)` handles the hidden `--diagnose-stack` CLI path and returns a trace result.
- `collect_process_stack(pid)` uses `rstack::TraceOptions` to print per-thread frames to stdout.
- `dump_self_stack()` re-executes the current io-engine binary with `--diagnose-stack <pid>` and logs stdout.

## Control Flow and State
Freeze detection calls `diagnose_reactor`; this logs the frozen reactor and launches a Tokio task. The task runs a separate process so stack collection can be isolated from the hung runtime path. When invoked in CLI diagnostic mode, the process traces the requested PID and prints thread names plus symbolized frames.

No persistent state is stored. Diagnostic output goes to logs or stdout depending on mode.

## Dependencies and Integration Points
Depends on `async_process`, `rstack`, `MayastorCliArgs`, and `Reactor`. It is called from `reactor_monitor_loop` in `reactor.rs` and from CLI bootstrap before normal environment startup.

## Risks and Test Signals
`String::from_utf8(output.stdout).unwrap()` can panic on invalid output, though diagnostic command output is expected UTF-8. Stack tracing may need privileges and symbols. Tests should cover CLI routing, invalid PID errors, and that freeze diagnostics do not block the monitor loop.
