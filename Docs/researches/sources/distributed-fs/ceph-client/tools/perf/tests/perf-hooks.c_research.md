<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-hooks.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-hooks.c

## Purpose

This selftest exercises perf's hook framework recovery path when an installed hook crashes. It ensures a bad hook is invoked, recovery runs after SIGSEGV, and the hook is removed.

## Research

`the_hook` receives a pointer to an integer flag, writes `1234`, then raises `SIGSEGV`. `sigsegv_handler` logs recovery, calls `perf_hooks__recover`, restores the default handler, raises SIGSEGV again, and exits if control unexpectedly returns. `test__perf_hooks` installs the handler, registers `the_hook` under hook name `test`, invokes `perf_hooks__invoke_test`, checks the flag, then verifies `perf_hooks__get_hook("test")` is null. State is the hook registry in `perf-hooks.h` and one stack `hook_flags` variable. Dependencies are process signal handling and perf's hook API. Integration is suite-level coverage for hook isolation in developer/testing builds. Risks include platform signal semantics, brittle behavior if recovery longjmps differently, and accidental masking of real crashes. Passing signals are flag mutation and automatic hook removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-hooks.c -->
