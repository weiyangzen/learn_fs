# sources/compression/xz/tests/test_hardware.c

Purpose: smoke tests for hardware-information APIs in `lzma/hardware.h`.

Important functions: `test_lzma_physmem()` calls `lzma_physmem()` and skips if the platform cannot determine memory. `test_lzma_cputhreads()` calls `lzma_cputhreads()` when threading is enabled and skips if CPU count is unavailable.

Control flow: `main()` starts the tuktest harness and runs the two tests. Results are intentionally tolerant because zero can mean unsupported platform introspection, not a library bug.

State and persistence: no state or files.

Dependencies and integration: depends on `tests.h`, `mythread.h`, and liblzma hardware APIs. Thread count testing is gated by `MYTHREAD_ENABLED`.

Risks: these tests are intentionally shallow and cannot assert specific values because results are hardware and OS dependent. They mainly catch crashes or impossible zero results on supported platforms.

Test signals: pass when nonzero values are returned, skip when the platform cannot report them, and fail only through harness/assertion errors.
