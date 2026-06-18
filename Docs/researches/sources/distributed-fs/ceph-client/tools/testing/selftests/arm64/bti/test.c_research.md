# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/test.c

Purpose: TAP-producing BTI behavior test that calls different landing-pad stubs through different indirect branch forms and verifies expected SIGILL behavior.

Important APIs/types/functions: output helpers `fdputs()`, `putstr()`, `putnum()`; `handler()` handles SIGILL, reports BTYPE, and clears PSTATE BTYPE to resume; `__do_test()` and `do_test` macro run trampoline/stub combinations; `start()` parses auxv, installs handler, runs 18 tests, prints summary, and exits.

Control flow: detects HWCAP/PACA and HWCAP2/BTI from initial stack auxv, reports whether binary was built for BTI, sets SIGILL handler, then tests six target stubs through three trampolines. Expected SIGILLs are disabled when hardware or binary BTI support is absent.

State and persistence: global counters and current-test strings; no file persistence beyond TAP output.

Dependencies/integration: freestanding runtime, signal wrappers, BTI assembly stubs/trampolines, arm64 auxv and signal context definitions.

Risks and test signals: exact expected matrix is architecture-sensitive. Handler must correctly skip/clear BTYPE; unexpected SIGILL exits with 128+signal after printing summary.
