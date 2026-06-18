# sources/cloud-native/ostree/src/libostree/ostree-mutable-tree.h

## Purpose
This public header declares the `OstreeMutableTree` API used to build and edit commit trees before writing them to an `OstreeRepo`.

## Important APIs, State, and Integration
The header defines type macros, `OstreeMutableTreeClass`, and an iterator helper struct. Constructors include `ostree_mutable_tree_new()`, `new_from_commit()`, and `new_from_checksum()`. Checksum APIs get/set metadata and contents checksums. Mutation and traversal APIs include `replace_file()`, `remove()`, `ensure_dir()`, `lookup()`, `ensure_parent_dirs()`, `walk()`, `fill_empty_from_dirtree()`, `check_error()`, `get_subdirs()`, and `get_files()`.

## Dependencies, Risks, and Tests
It depends on `ostree-types.h` and exposes GLib containers by transfer-none getters, so callers must not free returned hash tables. Integration points include commit writers and import code. Risks include public access to mutable hash-table contents through getters and lazy-load errors surfaced only by `check_error()` after legacy getter calls. Tests should verify documented transfer semantics and error behavior.
