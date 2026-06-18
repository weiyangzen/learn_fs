# sources/cloud-native/ostree/rust-bindings/src/auto/diff_item.rs

Purpose: Generated shared wrapper for `OstreeDiffItem`, representing one modified item in directory/tree diffs.

Important APIs: The file only defines the shared boxed/reference-counted wrapper with `ostree_diff_item_ref`, `ostree_diff_item_unref`, and type lookup. It derives debug, equality, ordering, and hash traits.

Control flow and state: Instances are produced by diff functions and reference-counted through libostree. There are no accessors in this file, so detailed diff interpretation may require other APIs or formatted output.

Dependencies and integration points: Used by `functions::diff_dirs` and `diff_print` alongside added and removed `gio::File` arrays. Depends on libostree shared ref/unref semantics.

Risks: Derived ordering/hash on shared wrapper identity may not represent semantic file diff ordering. Lack of field accessors limits Rust-side inspection and may push callers toward print-based handling.

Test signals: Diff integration tests should produce modified items, pass them to `diff_print`, and ensure reference ownership is stable.
