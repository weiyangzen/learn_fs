# sources/distributed-fs/ceph-client/rust/kernel/list/arc.rs

Purpose: defines `ListArc`, a special `Arc` wrapper that is unique per element and list-link ID, giving its owner exclusive permission to mutate intrusive list fields while still allowing ordinary shared `Arc` references.

Important APIs/types/functions: `ListArcSafe<ID>`, unsafe `TryNewListArc<ID>`, `impl_list_arc_safe!`, `ListArc<T, ID>`, `AtomicTracker<ID>`, constructors `new`, `pin_init`, `init`, conversions from `UniqueArc`, `pair_from_unique`, `try_from_arc`, `try_from_arc_borrow`, `try_from_arc_or_drop`, raw conversions, `into_arc`, `clone_arc`, `as_arc`, `as_arc_borrow`, and `ptr_eq`.

Control flow: creating a `ListArc` from a `UniqueArc` pins or owns the unique allocation, calls `on_create_list_arc_from_unique`, converts to `Arc`, then rewraps without changing representation. Attempted creation from a shared `Arc` delegates to `TryNewListArc::try_new_list_arc`, typically an atomic compare-exchange. Dropping or converting into a regular `Arc` calls `on_drop_list_arc` so tracking no longer claims a live list permission. Raw conversions intentionally preserve the tracking state so list insertion/removal can round-trip ownership.

State and persistence behavior: no persistent state. Per-object list-permission state lives inside the target type via `ListArcSafe`, commonly through `AtomicTracker` storing an `AtomicFlag`. The invariant allows false positives in tracking but forbids false negatives, avoiding duplicate `ListArc` creation.

Dependencies and integration points: depends on kernel `Arc`, `ArcBorrow`, `UniqueArc`, atomic ordering, pinning, `AllocError`, and `build_assert!`. It is tightly coupled to `List` ownership transfer and to macros that implement tracking for user structs.

Risks: representation-preserving transmutes and raw pointer conversions are sound only if tracking invariants are exact. The `untracked` macro strategy intentionally prevents creation from shared `Arc`; using it where shared recreation is needed can cause functional failures, while incorrect tracked implementations can cause memory unsafety. `pair_from_pin_unique` relies on distinct const IDs enforced by `build_assert!`.

Test signals: tests should cover tracked and untracked strategies, `try_from_arc` contention, drop/recreate ordering with `AtomicTracker`, `into_arc` clearing tracking, pair creation with distinct IDs, and list insertion/removal round trips. Concurrency tests around `AtomicTracker::cmpxchg` would be valuable.
