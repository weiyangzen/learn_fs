# sources/distributed-fs/ceph-client/scripts/rustdoc_test_builder.rs

Purpose: `rustdoc_test_builder.rs` transforms a single rustdoc-generated doctest source from stdin into a saved test body under `rust/test/doctests/kernel/`. It works around rustdoc not exposing stable test metadata.

Important APIs, types, and functions: `main()` reads stdin into a `String`, extracts the inner doctest function name by searching for the generated `fn main() { ... fn NAME()` pattern, rewrites unqualified `Result` return signatures to `::core::result::Result`, rewrites generated `unwrap()` checks into kernel `assert!(is_ok())`, derives a compact name after `_rust_kernel_`, and writes the transformed body to `rust/test/doctests/kernel/{name}`.

Control flow: every step is direct and uses `unwrap()`/`expect()` for fail-fast behavior. The script assumes one rustdoc-generated inner function and a known naming convention.

State and persistence: it creates or replaces one file in `rust/test/doctests/kernel/` for each rustdoc test fed to it. It does not create the directory itself.

Dependencies and integration points: invoked by the Rust kernel doctest build flow after rustdoc generates test code. Its output is consumed by `rustdoc_test_gen.rs`.

Risks: rustdoc output format changes can break function-name extraction. String replacement is precise and may miss semantically equivalent generated code. Panics are acceptable in the build pipeline but produce abrupt errors.

Test signals: doctests with plain `()`, `Result`, multiple generated numbers, and names containing `_rust_kernel_`; verify output path, stable name generation, and assert rewrite.
