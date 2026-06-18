# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_module.h

Purpose: this header provides a compact framework for kernel-module selftests loaded by kselftest. It lets a module count test cases, report failures/skips, taint the kernel as tested, and expose module metadata.

Important APIs and macros: `KSTM_MODULE_GLOBALS()` declares `total_tests`, `failed_tests`, and `skipped_tests` as `__initdata`. `KSTM_CHECK_ZERO(x)` increments total tests and records a failure when `x` is nonzero. `kstm_report()` prints pass/skip/fail summaries and returns `-EINVAL` on failure. `KSTM_MODULE_LOADERS(__module)` emits module init/exit functions that call `selftest()`, add `TAINT_TEST`, report results, and register with `module_init()` / `module_exit()`. `MODULE_INFO(test, "Y")` marks the module as a test.

Control flow: a test module includes the header, defines `selftest()`, calls `KSTM_MODULE_GLOBALS()`, uses `KSTM_CHECK_ZERO()` in its checks, and uses `KSTM_MODULE_LOADERS(name)` to wire module load/unload. Loading the module runs tests synchronously from the init function and returns success or `-EINVAL`.

State and persistence: counters live only during module initialization because they are `__initdata`; no persistent state is stored. Loading the module taints the running kernel with `TAINT_TEST`, which is an intentional global diagnostic state.

Dependencies and integration points: depends on Linux kernel module APIs, `pr_info`, `pr_warn`, `add_taint`, `TAINT_TEST`, `LOCKDEP_STILL_OK`, and a module-provided `selftest()` symbol. It integrates with kselftest module loaders and kernel taint/reporting infrastructure.

Risks: the framework is intentionally minimal; skipped tests must be counted manually, failure checks only test zero/nonzero expressions, and returning failure from module init can unload the test immediately. Because it taints the kernel, it should be used only for test modules.

Test signals: kernel log output reports all-passed, skipped-plus-passed, or failed counts. Module load status is the machine-readable pass/fail signal.
