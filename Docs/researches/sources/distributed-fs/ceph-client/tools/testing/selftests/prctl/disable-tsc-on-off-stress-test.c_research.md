# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-on-off-stress-test.c

Purpose: x86 stress test repeatedly toggling a process between TSC-enabled and TSC-SIGSEGV modes.

Important APIs/types/functions: `rdtsc()`, global `should_segv`, `sigsegv_cb()`, and `task()`.

Control flow: main forks 100 worker children. Each worker loops reading TSC, setting `PR_TSC_SIGSEGV`, expecting the next `rdtsc()` to fault, handler re-enables TSC and reads it once.

State and persistence behavior: `should_segv` tracks expected handler mode per child; prctl state is per-thread/process execution state.

Dependencies and integration points: x86 timestamp counter instruction and prctl TSC controls.

Risks and test signals: fatal conditions also exit 0 after printing, so automated pass/fail relies on absence of error output more than exit status.
