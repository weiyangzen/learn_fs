# sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.c

## Purpose
Provides the out-of-line target function used by kprobe tracing startup selftests. Keeping the target in a separate compilation unit ensures it can be built with the ftrace-friendly flags needed for reliable probing.

## APIs, Control Flow, and State
The file defines one function, `kprobe_trace_selftest_target(int a1, int a2, int a3, int a4, int a5, int a6)`, which returns the sum of its six arguments. It has no persistent state and no internal branching. `trace_kprobe.c` installs entry and return probes on this symbol during `CONFIG_FTRACE_STARTUP_TEST`, calls it with `1..6`, expects result `21`, and verifies both probes hit exactly once.

## Dependencies, Integration, Risks, and Tests
It depends only on `trace_kprobe_selftest.h`. Its integration point is the kprobe startup selftest, where it must remain visible and probeable. Risks are compiler optimization or build-flag changes eliminating, inlining, renaming, or making the function unsuitable for kprobe attachment. Test signals are the boot log line from `kprobe_trace_self_tests_init()` reporting `Testing kprobe tracing: OK`, plus failures in probe creation, hit counts, or return-value probing if this target stops behaving as expected.
