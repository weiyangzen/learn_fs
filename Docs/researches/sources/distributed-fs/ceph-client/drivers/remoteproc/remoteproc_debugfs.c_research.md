# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_debugfs.c

## Purpose
Provides debugfs diagnostics and controls for remoteproc instances: processor name, recovery policy, artificial crash injection, resource-table display, carveout display, trace buffers, and coredump policy.

## Important APIs, Types, And Functions
Framework-facing functions are `rproc_init_debugfs()`, `rproc_exit_debugfs()`, `rproc_create_debug_dir()`, `rproc_delete_debug_dir()`, `rproc_create_trace_file()`, and `rproc_remove_trace_file()`. File operations back `name`, `recovery`, `crash`, `resource_table`, `carveout_memories`, `coredump`, and per-trace files. `rproc_rsc_table_show()` decodes standard resource entries; `rproc_carveouts_show()` lists live carveout entries.

## Control Flow
Module init creates a top-level debugfs directory when debugfs is available. `rproc_add()` creates per-device files; trace resources discovered during firmware parse create trace files; cleanup removes them. Writes to `recovery` toggle `recovery_disabled` or call `rproc_trigger_recovery()`. Writes to `crash` parse a crash type and call `rproc_report_crash()`. Writes to `coredump` select disabled, buffered, or inline dump policy unless the processor is already crashed.

## State And Persistence Behavior
Debugfs files mirror live kernel objects and disappear on rproc deletion or module exit. Trace reads directly access remote memory through `rproc_da_to_va()` and may become unavailable after cleanup. Recovery and coredump writes mutate `rproc->recovery_disabled` and `rproc->dump_conf`; no state is persistent across reboot.

## Dependencies And Integration Points
Depends on debugfs, seq_file show helpers, user-copy helpers, resource-table ABI definitions, and core crash/recovery/address-translation APIs. Trace debugfs entries are created by `remoteproc_core.c` when handling `RSC_TRACE`.

## Risks
The `crash` file intentionally disrupts running processors and exercises recovery. Resource-table output is presentation-only and trusts the current `table_ptr`. Trace reads use `strnlen()` on shared remote memory, so changing buffers can yield partial output. Command parsers need testing for newline, length, and invalid string behavior.

## Test Signals
Verify debugfs files appear/disappear with rproc add/del, `recovery` accepts enabled/disabled/recover, `coredump` accepts disabled/enabled/inline and rejects changes while crashed, `crash` triggers recovery, `resource_table` and `carveout_memories` reflect boot resources, and trace files show live content or a not-available fallback.
