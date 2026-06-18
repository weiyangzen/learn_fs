# sources/distributed-fs/ceph-client/rust/kernel/mm/mmput_async.rs

Purpose: provides an `MmWithUser` reference-count wrapper whose `ARef` destructor uses `mmput_async`, making it suitable for contexts where synchronous `mmput` could sleep.

Important APIs/types/functions: `MmWithUserAsync`, its `AlwaysRefCounted` implementation, `Deref<Target = MmWithUser>`, and `MmWithUser::into_mmput_async`.

Control flow: `inc_ref` still uses `mmget`, preserving `mm_users`. `dec_ref` calls `mmput_async`. `into_mmput_async` consumes an `ARef<MmWithUser>`, reinterprets the raw pointer as `MmWithUserAsync`, and returns an `ARef` with the alternate drop behavior.

State and persistence behavior: no independent state; it shares the same `mm_struct` and reference count as `MmWithUser`. The only behavioral difference is asynchronous release.

Dependencies and integration points: compiled only with `CONFIG_MMU`. Depends on `bindings::mmput_async`, `ARef`, `AlwaysRefCounted`, and `MmWithUser`. It is re-exported from `mm.rs` under `CONFIG_MMU`.

Risks: layout compatibility with `MmWithUser` is essential for the raw cast. Callers must choose this wrapper when destruction context matters; using regular `MmWithUser` in atomic context can be invalid because `mmput` may sleep. Conversely, async release may defer cleanup timing.

Test signals: build tests under `CONFIG_MMU`, refcount lifecycle tests converting from `MmWithUser`, and context tests dropping `ARef<MmWithUserAsync>` from atomic-like paths are the key signals.
