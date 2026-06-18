# sources/distributed-fs/ceph-client/rust/macros/kunit.rs

## Purpose
`kunit.rs` converts an inline Rust test module annotated with `#[kunit_tests(name)]` into a Linux KUnit test suite. It preserves normal module items, wraps each `#[test]` function in an extern "C" KUnit case, and registers the suite only when `CONFIG_KUNIT="y"`.

## Important APIs, Types, And Functions
The central function is `kunit_tests(test_suite: Ident, module: ItemMod) -> Result<TokenStream>`. It emits per-test `kunit_rust_wrapper_<test>` functions, a static mutable `TEST_CASES` array terminated by `::pin_init::zeroed()`, and a `::kernel::kunit_unsafe_test_suite!` invocation. It also inserts local `assert!` and `assert_eq!` macro overrides that call `kernel::kunit_assert!` and `kernel::kunit_assert_eq!`.

## Control Flow
The helper validates that the suite name is no longer than 255 bytes and that the target module has inline contents. It gates the module with `#[cfg(CONFIG_KUNIT="y")]`, scans items, removes `#[test]` attributes from functions, and leaves non-test functions/items unchanged. For each test, it copies any `#[cfg]` attributes onto the wrapper call block, starts status as skipped, sets success before calling the Rust test, and asserts that the returned test result is OK.

## State And Persistence
Generated state is compile-time/static test registration data: wrappers and the mutable KUnit case array. Runtime state is KUnit's per-test status field and any state used by the test functions themselves.

## Dependencies And Integration Points
It depends on `syn`, `quote`, `CString`, `LitCStr`, `pin_init::zeroed`, `kernel::kunit` helpers, and `helpers::file()`. It integrates Rust unit-test syntax with Linux KUnit registration and status reporting.

## Risks And Edge Cases
Only inline modules are supported; `mod tests;` is rejected. Suite names over 255 bytes fail. The generated `static mut TEST_CASES` is required by KUnit registration and must not be accessed unsafely elsewhere. Local macro overrides are inserted before each test and may interact with user-defined macros in unusual scopes. Cfg-gated tests must have their cfgs propagated to avoid wrappers calling missing functions.

## Test Signals
Signals include macro expansion for modules with test and non-test items, cfg-gated tests, suite-name length rejection, KUnit-disabled builds, assertion macro behavior, generated C string names, and registration arrays terminated with a zeroed case.
