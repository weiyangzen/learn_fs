# sources/distributed-fs/ceph-client/rust/kernel/kunit.rs

Purpose: maps Rust unit-test assertions and generated test suites into the kernel KUnit framework. It provides hidden macros/functions used by generated Rust tests plus a public `in_kunit_test` helper.

Important APIs/types/functions: `err`, `info`, `kunit_assert!`, `kunit_assert_eq!`, private `TestResult`, `is_test_result_ok`, `kunit_case`, `kunit_unsafe_test_suite!`, and `in_kunit_test`. The local `tests` module demonstrates `#[kunit_tests]` integration.

Control flow: print helpers route formatted Rust `fmt::Arguments` to `_printk` when `CONFIG_PRINTK` is enabled. `kunit_assert!` first checks the Rust condition, then obtains the current KUnit test. Without a current KUnit test it logs KUnit-like failure text. With a test pointer, it builds static `kunit_loc` and `kunit_unary_assert` records, calls `__kunit_do_failed_assertion`, then aborts the KUnit test via `__kunit_abort`. `kunit_unsafe_test_suite!` builds a static `kunit_suite` and places a pointer into `.kunit_test_suites`.

State and persistence behavior: state is static test metadata and per-current-task KUnit context retrieved from C. Assertion metadata is static to satisfy C lifetime requirements. No persistent state is written.

Dependencies and integration points: depends on KUnit C bindings, `_printk`, Rust formatting, generated `#[kunit_tests]` infrastructure, `CStr`, and link-section behavior. It is a bridge between Rust doc/unit tests and KUnit's C execution model.

Risks: failing assertions abort without running Rust destructors, and comments explicitly note the foreign-unwind/stack implications. The hidden macros must be used only from generated tests or valid KUnit context. Suite and test case arrays must be static and null-terminated; misuse of `kunit_unsafe_test_suite!` can hand invalid metadata to KUnit. The suite-name buffer has a 255-byte limit enforced at const time.

Test signals: the embedded tests cover basic assertion routing and `in_kunit_test`. Additional signals are build/link tests verifying `.kunit_test_suites`, tests with `CONFIG_PRINTK` disabled, generated doctests returning both `()` and `Result`, and tests that intentionally fail to confirm KUnit receives the failure.
