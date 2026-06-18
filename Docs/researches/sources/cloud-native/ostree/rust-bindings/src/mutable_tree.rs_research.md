# sources/cloud-native/ostree/rust-bindings/src/mutable_tree.rs

## sources/cloud-native/ostree/rust-bindings/src/mutable_tree.rs

Handwritten extensions for generated `MutableTree`. It exposes `copy_files` and `copy_subdirs`, intentionally copying libostree's internal hash tables into Rust `HashMap`s instead of exposing mutable borrowed table access.

Control flow obtains C hash tables via `ostree_mutable_tree_get_files` or `_get_subdirs`. `copy_files` uses GLib container conversion, while `copy_subdirs` manually iterates with `g_hash_table_foreach` and converts keys to `String` and values to `MutableTree`. State is a snapshot copy of the mutable-tree contents; repository persistence happens later when a mutable tree is written by repo APIs.

Dependencies include `glib`, `ffi`, and `HashMap`. Risks are conversion correctness and the fact that returned maps are copies, not live views. This design reduces use-after-free risk compared with exposing the original C tables. No local tests are present.
