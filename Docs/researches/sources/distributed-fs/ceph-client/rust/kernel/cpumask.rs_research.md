<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpumask.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cpumask.rs

## Purpose
This file wraps Linux `struct cpumask` and `cpumask_var_t` for Rust code.

## Important APIs, Types, and Functions
`Cpumask` is a transparent wrapper exposing unsafe `from_raw_mut`, unsafe `from_raw`, `as_raw`, non-atomic `set` and `clear`, `test`, `setall`, `empty`, `full`, `weight`, and `copy`. `CpumaskVar` owns either an offstack allocated cpumask or an inline `Cpumask`, depending on `CONFIG_CPUMASK_OFFSTACK`, and provides `new_zero`, unsafe uninitialized `new`, unsafe raw borrow constructors, `try_clone`, `Deref`, `DerefMut`, and `Drop`.

## Control Flow and State
Owned construction calls `zalloc_cpumask_var` or `alloc_cpumask_var` when offstack, or initializes inline `Opaque` storage otherwise. `try_clone` allocates a new mask and copies from the source. Methods delegate directly to C cpumask helpers with validated `CpuId` inputs.

## State and Persistence Behavior
`Cpumask` borrows existing C storage. `CpumaskVar` owns storage and frees it in `Drop` only for offstack configurations. Inline configurations store the C cpumask directly in the Rust object. `new` may return uninitialized storage, so callers must initialize before use.

## Dependencies and Integration Points
The module depends on `AllocError`, `Flags`, `CpuId`, `Opaque`, cpumask bindings, and Rust deref traits. It is used by cpufreq policies and other CPU-affinity code.

## Risks
`set`/`clear` are non-atomic despite C naming conventions, so concurrent cpumask mutation requires external synchronization or atomic C APIs not exposed here. Unsafe raw constructors rely on caller-managed lifetimes. Offstack allocation failures return `AllocError`. Using uninitialized masks from `new` before population is unsafe.

## Test Signals
No local tests. Doc examples demonstrate setting, testing, counting, and cloning masks. Useful runtime tests should cover both offstack and inline configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpumask.rs -->
