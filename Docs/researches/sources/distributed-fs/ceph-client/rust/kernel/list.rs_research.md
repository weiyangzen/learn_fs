# sources/distributed-fs/ceph-client/rust/kernel/list.rs

Purpose: implements a generic intrusive circular doubly-linked list for Rust kernel code. Elements are reference-counted through `ListArc`, and each list owns the unique `ListArc` permission to mutate an element's link fields.

Important APIs/types/functions: `List<T, ID>`, unsafe trait `ListItem<ID>`, `ListLinks<ID>`, `ListLinksSelfPtr<T, ID>`, `Iter`, `Cursor`, `CursorPeek`, `IntoIter`, and re-exported helper macros/types from `list/arc.rs`, `list/arc_field.rs`, and `list/impl_list_item_mod.rs`. Public operations include `new`, `is_empty`, `push_back`, `push_front`, `pop_back`, `pop_front`, unsafe `remove`, `push_all_back`, `cursor_front`, `cursor_back`, and `iter`.

Control flow: insertion consumes a `ListArc`, converts it to a raw pointer, calls `T::prepare_to_insert` to obtain exclusive link-field access, and links the node into the circular list. Removal updates neighboring links, nulls the removed node's links, calls `T::post_remove`, and reconstructs the `ListArc`. Iteration walks from `first` until it reaches the stop pointer again. Cursors hold a mutable borrow of the list and represent the gap before `next`; peek wrappers permit removal or temporary borrowing of adjacent elements.

State and persistence behavior: list state is an in-memory raw pointer to the first link node; empty lists use null. Each element's link fields are null when not in a list and cyclic when inserted. Drop drains the list by popping the front, thereby dropping owned `ListArc`s. No persistent storage exists.

Dependencies and integration points: depends on `ArcBorrow`, `ListArc`, `Opaque`, pin-init, raw pointer manipulation, and `container_of!` via implementations. It is intended as a building block for kernel subsystems that need intrusive lists without allocating wrapper nodes.

Risks: the unsafe `ListItem` contract is central. Incorrect `view_links`, `view_value`, `prepare_to_insert`, or `post_remove` can create aliasing, dangling pointers, or duplicate link ownership. `remove` is unsafe because the caller must ensure the item is not in another same-ID list. Trait-object support through `ListLinksSelfPtr` stores a self pointer and must preserve validity until removal. Pointer provenance comments indicate sensitivity to pointer-reference-pointer roundtrips.

Test signals: doctests cover basic list use, trait-object list items, cursor removal/insertion, merging, and owned iteration. Additional tests should stress remove of absent items, single/two/many-element edge cases, `push_all_back` from empty and non-empty lists, drop draining, `DoubleEndedIterator`, and multiple `ID` link sets on the same value.
