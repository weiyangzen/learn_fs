# sources/distributed-fs/ceph-client/rust/kernel/mm.rs

Purpose: wraps `struct mm_struct` and related read-lock guards so Rust code can model address-space lifetime through `mmgrab`, `mmget`, mmap read locks, and per-VMA read locks.

Important APIs/types/functions: `Mm`, `MmWithUser`, `AlwaysRefCounted` impls, `Mm::from_raw`, `Mm::mmget_not_zero`, `MmWithUser::from_raw`, `lock_vma_under_rcu`, `mmap_read_lock`, `mmap_read_trylock`, `MmapReadGuard`, `VmaReadGuard`, and `VmaRef` integration from `virt`.

Control flow: `ARef<Mm>` increments/decrements `mm_count` via `mmgrab`/`mmdrop`. `ARef<MmWithUser>` increments/decrements `mm_users` via `mmget`/`mmput`. `mmget_not_zero` attempts to upgrade an `Mm` to an `MmWithUser`. With nonzero users, callers may take mmap read locks or try per-VMA RCU locks. Guards unlock in `Drop` and are marked `NotThreadSafe` so lock/unlock happen on the same thread.

State and persistence behavior: wraps live process address-space state owned by the kernel. Reference counts are kernel state; guard objects model temporary lock ownership. No new persistent data is introduced.

Dependencies and integration points: depends on `bindings` MM APIs, `ARef`, `AlwaysRefCounted`, `NotThreadSafe`, `Opaque`, and `virt::VmaRef`. It is the foundation for VMA lookup and miscdevice mmap handling.

Risks: using `Mm` methods that require nonzero `mm_users` without `MmWithUser` would be unsafe, so the type split must be preserved. `mmdrop`/`mmput` may sleep, influencing where `ARef` destructors can run. Per-VMA lock support is config-dependent and returns `None` when disabled. Raw constructors require callers to prove lifetime and user-count invariants.

Test signals: tests should cover `mmget_not_zero` success/failure, mmap read lock lookup, trylock failure handling, per-VMA-lock disabled builds, and guard drop on the same thread. Static analysis should check no `VmaRef` outlives its guard.
