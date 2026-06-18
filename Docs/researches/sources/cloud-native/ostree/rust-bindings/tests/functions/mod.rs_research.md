# sources/cloud-native/ostree/rust-bindings/tests/functions/mod.rs

Purpose: This integration test module exercises safe wrapper functions for listing repository objects and checksumming loaded file content.

Important APIs, types, and functions: `list_repo_objects` calls `Repo::list_objects` with `ffi::OSTREE_REPO_LIST_OBJECTS_ALL`, iterates `ObjectName` keys, counts `DirTree`, `DirMeta`, `File`, and `Commit`, and validates the commit checksum. `should_checksum_file_from_input` traverses a commit, loads each file object via `Repo::load_file`, and calls `ostree::checksum_file_from_input`.

Control flow: Both tests create a temporary `TestRepo`, write a known commit, then inspect repository objects. The checksum test filters traversal output to file objects before recomputing each checksum from loaded stream, metadata, and xattrs.

State and persistence behavior: Temporary repository state includes one commit and its file/tree metadata objects. No state persists beyond test cleanup.

Dependencies and integration points: Uses `TestRepo`, `ObjectType`, `gio::Cancellable::NONE`, the `ffi` constant from raw bindings, and safe wrappers that depend on FFI declarations in `sys/src/lib.rs`.

Risks: Expected object counts are fixture-specific and can change if `tests/data/test.tar` changes. The checksum test skips non-file objects, so metadata checksum wrapper regressions would be covered elsewhere.

Test signals: Passing confirms object listing maps raw OSTree object types correctly and that file content checksum recomputation matches stored object checksums.
