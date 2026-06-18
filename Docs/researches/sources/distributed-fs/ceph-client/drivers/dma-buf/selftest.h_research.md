# sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.h

Purpose: shared declarations and helpers for dma-buf selftest modules.

Important APIs/types/functions: includes generated prototypes for every `selftest(name, func)` entry in `selftests.h`, defines `struct subtest`, declares `__subtests()`, and provides the `subtests()` and `SUBTEST()` helper macros.

Control flow: no direct runtime flow. Test files define static subtest arrays with `SUBTEST(fn)` and invoke `subtests(tests, data)`, which passes the caller function name for filtering/logging.

State and persistence behavior: none. It is compile-time glue.

Dependencies and integration points: included by `selftest.c` and all `st-*` dma-buf selftest files. It centralizes subtest invocation against the harness.

Risks and test signals: macro-generated prototypes must match the actual selftest function signatures. Test signals are clean builds when adding/removing entries in `selftests.h` and correct caller names in `st_filter`.
