# sources/distributed-fs/ceph-client/lib/find_bit_benchmark_rust.rs

## Purpose
Rust benchmark module for measuring `BitmapVec` traversal methods analogous to C `find_next_bit` and `find_next_zero_bit` behavior. It is focused on Rust bitmap API performance.

## Important APIs, Types, and Functions
Defines module type `Benchmark`, constants `BITMAP_LEN` and `SPARSENESS`, helper functions `test_next_bit()`, `test_next_zero_bit()`, and `find_bit_test()`, and a `kernel::Module` implementation whose `init()` runs the benchmark then returns `Err(code::EINVAL)`.

## Control Flow
Initialization allocates a `BitmapVec`, fills it randomly, times `next_bit()` and `next_zero_bit()` loops using `Instant<Monotonic>`, prints results, then allocates a sparse bitmap, sets random bits through the kernel binding `__get_random_u32_below()`, repeats the traversal timings, and returns `EINVAL` so the module can be reloaded for repeated runs.

## State and Persistence
All state is stack/local Rust-owned bitmap allocation during init. Because init returns an error, no module instance persists.

## Dependencies and Integration Points
Depends on Rust-for-Linux kernel prelude, `BitmapVec`, allocation flags, monotonic time, printk macros, `ThisModule`, and a raw binding for random bounded integers. It benchmarks Rust API behavior relative to the C benchmark in the same directory.

## Risks
Allocation failure panics via `expect()`, appropriate for a benchmark but not production style. The unsafe random binding must receive a valid bound, which it does through `BITMAP_LEN.try_into().unwrap()`. Hardened bitmap bounds require explicit loop break when `i == BITMAP_LEN`. Like the C benchmark, timing varies with random data and system load.

## Test Signals
Build with Rust support, insert the module, and verify printed random/sparse timing lines and intentional `EINVAL` init failure. Compare iteration counts with expected bitmap density and watch for hardened-bounds warnings or allocation errors.
