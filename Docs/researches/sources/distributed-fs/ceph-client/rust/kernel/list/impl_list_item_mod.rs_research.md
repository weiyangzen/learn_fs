# sources/distributed-fs/ceph-client/rust/kernel/list/impl_list_item_mod.rs

Purpose: contains helper traits and macros that implement unsafe `ListItem` plumbing from declared link fields, reducing the amount of hand-written unsafe code needed by intrusive list users.

Important APIs/types/functions: unsafe `HasListLinks<ID>`, `impl_has_list_links!`, unsafe marker `HasSelfPtr<T, ID>`, `impl_has_list_links_self_ptr!`, and `impl_list_item!` for both `ListLinks` and `ListLinksSelfPtr` storage strategies.

Control flow: `impl_has_list_links!` uses `offset_of!` and `addr_of_mut!` to produce a raw pointer to a link field without dereferencing intermediate pointers. The `ListLinks` variant of `impl_list_item!` implements `view_links` as field access and `view_value`/`post_remove` via `container_of!`. The `ListLinksSelfPtr` variant writes the full self pointer into the `ListLinksSelfPtr` container during insertion and reads it back for trait-object-compatible value recovery.

State and persistence behavior: no module-owned persistent state. The macros define how per-object link state is accessed and, for self-pointer lists, where the object pointer is cached during list membership.

Dependencies and integration points: depends on `ListItem`, `ListLinks`, `ListLinksSelfPtr`, `Opaque`, and `container_of!`. It is the recommended integration path for user structs implementing intrusive list support.

Risks: macro-generated implementations are only as sound as the field declaration. The `ListLinksSelfPtr` variant has TODO safety comments and writes/reads raw self pointers, so misuse could invalidate trait object recovery. Nested field paths must not traverse pointers; the macro includes a static `offset_of!` check to catch that. Manual `HasListLinks` implementations bypass this protection.

Test signals: doctests cover simple and nested field implementations for both link storage styles. Additional compile-fail tests should cover wrong field types, pointer-traversing field paths, duplicate `ListItem` IDs, and mismatched trait-object self pointer types.
