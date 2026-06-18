# sources/distributed-fs/ceph-client/rust/kernel/maple_tree.rs

Purpose: wraps Linux maple trees for Rust-owned values implementing `ForeignOwnable`, supporting non-overlapping range insertion, erasure, allocation-range insertion, locked lookup, and iteration through `ma_state`.

Important APIs/types/functions: `MapleTree<T>`, `MapleTreeAlloc<T>`, `to_maple_range`, `insert`, `insert_range`, `erase`, `lock`, `MapleGuard`, `MaState`, `find`, `alloc_range`, `InsertError<T>`, `InsertErrorKind`, `AllocError<T>`, and `AllocErrorKind`.

Control flow: constructors initialize a C `maple_tree` with normal or `MT_FLAGS_ALLOC_RANGE` flags. Insert operations convert Rust ownership to a foreign pointer, call C insertion APIs, and reclaim the value on error with a specific Rust error cause. `erase` removes the range containing an index and converts the returned pointer back into `T`. `lock` takes the tree spinlock and returns `MapleGuard`; lookups and `MaState` iteration borrow values while the guard/state proves access. Drop frees Rust entries if needed, then destroys the tree.

State and persistence behavior: state is in-memory C maple tree nodes containing foreign-owned Rust values. The invariant is that each stored range owns one `T`. Destruction may free all entries without first removing them because the tree is about to become unobservable. No durable persistence exists.

Dependencies and integration points: depends on `bindings` maple-tree APIs, `ForeignOwnable`, `Opaque`, RCU guard during raw destruction iteration, spinlocks, allocation flags, and kernel error conversion. It is useful for address/range maps in memory-management or driver code.

Risks: callers must not observe the tree during `free_all_entries`, which intentionally leaves C tree structure stale while freeing values. Borrowed results from `load` and `find` are only valid under the lock/state lifetime. Range conversion must reject empty or overflowing ranges; edge cases around `usize::MAX` are important. Error mapping treats unexpected non-ENOMEM/non-EEXIST returns as invalid requests.

Test signals: doctests cover point insertion, range insertion overlap, erasure by contained index, locked load with refcounted values, allocation tree placement, and iteration. Further tests should cover unbounded ranges, excluded bound overflow/underflow, drop of values with destructors, allocation-tree busy conditions, and lock-held mutation patterns.
