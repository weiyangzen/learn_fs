## sources/distributed-fs/ceph-client/mm/kasan/kasan_test_rust.rs

Purpose: Rust helper for the KASAN KUnit suite. It provides a minimal unsafe Rust use-after-free trigger so the C test suite can verify that Rust code is sanitized.

Important APIs and functions: exposes `#[no_mangle] extern "C" fn kasan_test_rust_uaf() -> u8`, declared from `kasan.h` and called by `rust_uaf()` in the C KUnit tests.

Control flow: creates a `KVec<u8>`, pushes 4096 bytes using `GFP_KERNEL`, takes a raw mutable pointer to element 2048, drops the vector to free storage, then unsafely dereferences the stale pointer. The dereference is intentionally incorrect and should trigger KASAN.

State and persistence: all state is local to the helper. The vector allocation is released before the invalid access; there is no persistent state.

Dependencies and integration: depends on kernel Rust prelude, `KVec`, `GFP_KERNEL`, raw pointer operations, and C ABI linkage into the KASAN KUnit object when `CONFIG_RUST` is enabled.

Risks and test signals: the test panics on allocation failure through `unwrap()`, so it assumes test memory is available. The signal is a KASAN report observed by the C test harness when `CONFIG_RUST` and KASAN KUnit tests are enabled.
