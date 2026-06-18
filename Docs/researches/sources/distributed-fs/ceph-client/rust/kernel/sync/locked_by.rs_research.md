# Research: sources/distributed-fs/ceph-client/rust/kernel/sync/locked_by.rs

## sources/distributed-fs/ceph-client/rust/kernel/sync/locked_by.rs

Purpose: represents data protected by a lock that is not physically wrapping that data. Important APIs are `LockedBy<T, U>`, `new`, `access`, and `access_mut`.

Control flow: `new` records the address of the owner lock's protected data (`owner.data.get()`) and stores the payload in `UnsafeCell`. `access` and `access_mut` require references to the owner data, compare their address to the stored owner pointer, panic on mismatch, and then return shared or mutable access to the payload. State is the payload plus a raw, never-dereferenced owner identity pointer. Dependencies are `Lock`, backend trait, `build_assert`, `UnsafeCell`, pointer equality, and size checks forbidding zero-sized owners/locks where identity would be ambiguous. Integration points are aggregate structures where one lock protects fields in child objects, and `GlobalLockedBy` mirrors the same concept for global locks. Risks include owner memory reuse causing logical but memory-safe mistaken access, panics on mismatched owners, ZST misuse caught at build time, and readers assuming the owner pointer preserves lifetime. Test signals include correct-owner access, mismatched-owner panic, mutable exclusivity through guards, and compile-time failures for ZST owner cases.
