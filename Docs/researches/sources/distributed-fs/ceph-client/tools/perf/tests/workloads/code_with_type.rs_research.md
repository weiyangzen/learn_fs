# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.rs

## Purpose
This Rust companion workload creates a concrete `Buf` structure and mutates it in a loop so perf data type profiling can find Rust type and field information.

## Important APIs, Types, And Functions
The core type is private `struct Buf { data1: u64, data2: String, data3: u64 }`. The public ABI is `#[no_mangle] pub extern "C" fn test_rs(count: u32)`, which is called from `code_with_type.c`.

## Control Flow
`test_rs()` allocates a mutable `Buf` with `data2` set to `"data"`, then iterates from `1` to `count - 1`. Each iteration increments `data1`, adds an extra increment when `data1 == 123`, and accumulates `data1` into `data3`.

## State, Dependencies, And Integration
State is stack/local Rust data only; it is not persisted or shared. Integration depends on C-compatible symbol naming and the perf build path linking Rust into the workload. `data2` ensures the type includes a nontrivial standard-library field.

## Risks And Test Signals
The function has no observable return value, so aggressive optimization is a risk if debug/type information or side effects are insufficient for the target test. The expected test signal is the presence of `Buf` and its fields in perf's data type profiling output.
