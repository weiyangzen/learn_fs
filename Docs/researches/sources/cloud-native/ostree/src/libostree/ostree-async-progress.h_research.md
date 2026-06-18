# sources/cloud-native/ostree/src/libostree/ostree-async-progress.h

Purpose: This public header declares the `OstreeAsyncProgress` GObject type, its class signal slot, and the progress key/value API implemented in `ostree-async-progress.c`.

Important APIs, types, and functions: It defines GObject type-check/cast macros, forward declares `OstreeAsyncProgress` and `OstreeAsyncProgressClass`, and defines the class struct with `GObjectClass parent_class` and `void (*changed)(OstreeAsyncProgress *, gpointer)`. Public declarations include constructors, status getters/setters, varargs `get`/`set`, typed uint/uint64 accessors, variant accessors, `finish`, and `copy_state`.

Control flow: Header-only flow is limited to macro expansion and C linkage via `G_BEGIN_DECLS`/`G_END_DECLS`. Runtime behavior is in the C implementation.

State and persistence behavior: The header exposes an opaque instance type, preventing callers from depending on internal fields. It defines an in-memory progress object API and no persistence contract.

Dependencies and integration points: Includes `ostree-types.h` for GLib type dependencies and `_OSTREE_PUBLIC`. Consumed by libostree users, GIR generation, and Rust FFI generation in `sys/src/lib.rs`.

Risks: ABI stability of the class struct matters because the raw Rust binding mirrors `OstreeAsyncProgressClass`. Adding virtual slots changes layout and must be reflected in generated bindings/tests. Varargs declarations must remain annotated as NULL-terminated for compiler diagnostics and introspection expectations.

Test signals: `sys/tests/layout.c` and `abi.rs` compare `OstreeAsyncProgressClass` size/alignment with Rust. Behavioral signal depends on async progress tests outside this subset.
