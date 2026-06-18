# sources/distributed-fs/ceph-client/drivers/dma-buf/selftest.c

Purpose: provides the module harness for dma-buf selftests, including test selection, subtest filtering, ordering, and init-time execution.

Important APIs/types/functions: builds the `selftests[]` table from `selftests.h`, declares per-test module parameters, exposes `__sanitycheck__()`, `__subtests()`, and module parameter `st_filter`.

Control flow: module init calls `run_selftests()`. If no individual test parameter is enabled, all tests default to enabled. Tests run in declaration order. `__subtests()` applies optional comma-separated filters with optional `!` negation and `caller/subtest` syntax, prints each subtest, checks for pending signals, runs the function, and stops on non-`-EINTR` errors. `run_selftests()` warns if a test returns positive or `-ENOTTY`, because those conflict with selftest sentinel semantics.

State and persistence behavior: enabled flags are module parameters. `__st_filter` is module parameter string state. There is no persistent result storage beyond kernel logs and module load return code.

Dependencies and integration points: depends on `selftest.h`/`selftests.h`, module parameters, scheduler signal checks, and individual selftest source files. The module is built as `dmabuf_selftests` under `CONFIG_DMABUF_SELFTESTS`.

Risks and test signals: filter parsing assumes `kstrdup(__st_filter)` succeeds and that `__st_filter` is meaningful; null filter behavior should be validated in module-parameter handling. Long-running subtests can be interrupted by signals. Test signals are module load success/failure, per-test parameter selection, `st_filter` include/exclude behavior, and kernel log lines for each executed test/subtest.
