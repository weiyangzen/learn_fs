# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-ctxt-sw-stress-test.c

Purpose: x86 stress test that PR_SET_TSC state is preserved correctly across context switches.

Important APIs/types/functions: `rdtsc()`, `sigsegv_expect()`, `segvtask()`, `sigsegv_fail()`, and `rdtsctask()` implement enabled/disabled TSC roles.

Control flow: main forks 100 children; even children enable TSC and spin reading it, odd children set `PR_TSC_SIGSEGV`, install a handler, and attempt `rdtsc()`. Any enabled SIGSEGV or disabled successful read prints fatal error.

State and persistence behavior: each child has independent prctl TSC mode and alarm timeout. Parent only waits for children.

Dependencies and integration points: x86 `rdtsc`, `PR_GET_TSC/PR_SET_TSC`, and signal delivery.

Risks and test signals: child failures call `exit(0)`, so parent status may not catch all printed fatal errors; this is a legacy stress pattern where stderr output is part of the signal.
