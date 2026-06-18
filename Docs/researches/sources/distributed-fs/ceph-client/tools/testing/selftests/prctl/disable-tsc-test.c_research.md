# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/disable-tsc-test.c

Purpose: basic x86 functional test for `PR_GET_TSC` and `PR_SET_TSC`.

Important APIs/types/functions: `rdtsc()`, `sigsegv_cb()`, and `tsc_names[]` provide read, fault handling, and diagnostics.

Control flow: the program reads TSC, gets current TSC mode, enables TSC, reads again, sets `PR_TSC_SIGSEGV`, then attempts `rdtsc()`. SIGSEGV handler confirms mode, re-enables TSC, and returns so the read can proceed.

State and persistence behavior: signal disposition and per-process TSC control state are mutated. No file state.

Dependencies and integration points: x86 inline assembly and Linux prctl constants, with local fallback definitions for older headers.

Risks and test signals: mostly diagnostic and exits success if the final flow completes; unexpected prctl errors are printed but do not always abort immediately.
