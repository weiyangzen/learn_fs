# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.h

## Purpose
`memory-alloc.h` exposes VDO's tracked allocation interface and type-safe allocation macros.

## Important APIs, Types, and Functions
Macros `vdo_allocate()` and `vdo_allocate_extended()` calculate byte sizes using `size_mul()` and `struct_size()`. `vdo_allocate_cache_aligned()` requests cacheline alignment. `vdo_forget()` atomically nulls a pointer variable and returns the old value for transfer/free patterns. Functions declare allocation, nowait allocation, reallocation, string duplication, free, memory lifecycle, allocating-thread registration, stats retrieval, and reporting.

## Control Flow
Callers normally use `vdo_allocate(count, what, &ptr)` or `vdo_allocate_extended(count, field, what, &ptr)`, then release with `vdo_free()` or transfer ownership with `vdo_forget()`.

## State and Persistence Behavior
The header declares runtime memory accounting functions but no persistent state. `vdo_forget()` changes caller-owned pointer state to prevent reuse after ownership transfer.

## Dependencies and Integration Points
It includes Linux cache, I/O page size, overflow helpers, VDO assertions, and thread-registry types. It is included throughout the VDO tree.

## Risks and Edge Cases
Macro type inference depends on passing an address of a pointer with the expected target type. `vdo_forget()` casts through `void **`; callers must not pass expressions with unexpected side effects. Allocation macros rely on overflow-aware helpers.

## Test Signals
Compile-time macro use across flexible-array allocations, cache-aligned allocation tests, `vdo_forget()` ownership transfer patterns, and memory stat queries validate the header.
