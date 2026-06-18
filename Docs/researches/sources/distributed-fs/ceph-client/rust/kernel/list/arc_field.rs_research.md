# sources/distributed-fs/ceph-client/rust/kernel/list/arc_field.rs

Purpose: provides `ListArcField`, a field wrapper whose contents are accessible only through ownership of the corresponding `ListArc`. This supports per-list-permission interior mutability without exposing general shared mutation.

Important APIs/types/functions: `ListArcField<T, ID>`, `new`, `get_mut`, unsafe `assert_ref`, unsafe `assert_mut`, and `define_list_arc_field_getter!`.

Control flow: `ListArcField` stores `T` in `UnsafeCell`. Code with exclusive construction access can call `get_mut`. Code that has a shared or mutable `ListArc<Self, ID>` uses generated getters; the macro obtains the field from `self`, then calls `assert_ref` or `assert_mut` under the safety argument that `ListArc` ownership grants access to that field.

State and persistence behavior: state is the wrapped in-memory value. There is no persistence or independent synchronization. The type's `Send` and `Sync` implementations require `T: Send + Sync` because access may cross threads through a `ListArc`.

Dependencies and integration points: depends on `UnsafeCell` and `ListArc`. It integrates with list item structs that need a field owned by the unique list reference, often to pair intrusive-list membership with mutable metadata.

Risks: `assert_mut` returns `&mut T` from `&self`; soundness relies entirely on the caller really having mutable access to the unique `ListArc`. Manually calling the unsafe methods without the required `ListArc` access would violate aliasing. The macro is safer than hand calls but still assumes the field belongs to the same `Self` and `ID`.

Test signals: tests should verify generated shared and mutable getters, interaction with `UniqueArc` construction through `get_mut`, and compile-time rejection of mismatched field types/IDs. Miri-style aliasing checks would be useful if available for a user-space model.
