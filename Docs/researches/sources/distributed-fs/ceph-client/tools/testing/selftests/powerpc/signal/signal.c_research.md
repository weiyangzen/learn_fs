# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.c

Purpose: stress-tests that sending `SIGUSR1` to the current process is reliably delivered, including through a raw assembly syscall helper.

Important APIs/types/functions: uses external `signal_self()`, `signal_handler()`, global `signaled/fail`, and `test_signal()`.

Control flow: installs handlers for `SIGUSR1` and `SIGALRM`, first forks 1000 children that signal the parent, then performs `MAX_ATTEMPT` direct self-signal attempts via the assembly helper. Each iteration arms an alarm and busy-waits until the signal flag is set.

State and persistence behavior: `sig_atomic_t` globals carry signal state between handler and loop. No filesystem or durable state is changed.

Dependencies and integration points: built with `signal.S`, the selftest harness, and Altivec flags even though this file itself does not use vector operations directly.

Risks and test signals: busy waits rely on signal delivery and alarm timeout. Failure prints iteration and return code; test timeout is extended to 300 seconds.
