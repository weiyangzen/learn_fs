# sources/distributed-fs/ceph-client/tools/verification/rv/include/rv.h

Purpose: `rv.h` contains common runtime-verification tool definitions.

Important types and APIs: `MAX_DESCRIPTION` and `MAX_DA_NAME_LEN` bound monitor metadata. `struct monitor` stores a monitor name, description, enabled state, and nested flag. `should_stop()` lets monitor-running loops observe top-level signal-triggered shutdown.

Control flow and integration: `in_kernel.c` fills `struct monitor` records when listing tracefs monitors and calls `should_stop()` during monitor execution. `trace.c` also uses `should_stop()` to stop raw trace iteration.

State, dependencies, risks, and tests: state is implemented in `rv.c` as a static stop flag. Risks are truncation from fixed-size arrays and a process-global stop condition. Test signals are clean monitor listing with descriptions, and Ctrl-C/SIGTERM causing `rv mon` loops and trace collection to exit.
