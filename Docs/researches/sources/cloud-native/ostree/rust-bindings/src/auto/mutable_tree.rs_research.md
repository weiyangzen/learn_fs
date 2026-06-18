# sources/cloud-native/ostree/rust-bindings/src/auto/mutable_tree.rs

Purpose: Generated wrapper for `OstreeMutableTree`, a mutable in-memory representation of OSTree directory tree content.

Important APIs: `new`, feature-gated constructors `from_checksum` and `from_commit`, `check_error`, `ensure_dir`, `ensure_parent_dirs`, `fill_empty_from_dirtree`, checksum getters/setters, `lookup`, `remove`, `replace_file`, and `walk`. Hash-table accessors for files/subdirs are unimplemented.

Control flow and state: Methods mutate or inspect the underlying tree object. Directory creation and file replacement update in-memory tree state; loading from checksums/commits ties the tree to repository objects. Persistence requires later repo commit/write APIs outside this file.

Dependencies and integration points: Depends on `Repo` under relevant feature gates, GLib error handling, and checksum strings. It is used by commit construction and tree editing workflows.

Risks: Unimplemented files/subdirs accessors limit direct enumeration. Callers must validate checksum strings and understand that setters can create invalid state until `check_error` or downstream commit APIs reject it. Feature-gated repo constructors require matching libostree support.

Test signals: Tree edit tests should cover ensure/walk/lookup/replace/remove, invalid checksum handling, loading from commits, and committing the resulting tree through repo APIs.
