# sources/distributed-fs/ceph-client/rust/kernel/debugfs/entry.rs

## Purpose
`entry.rs` is the raw debugfs dentry owner for the Rust debugfs abstraction. It wraps C `struct dentry *` values returned by debugfs creation functions and removes them on drop, while encoding parent and borrowed-data lifetimes.

## Important APIs, Types, and Functions
`Entry<'a>` stores the raw dentry pointer, an optional owning parent `Arc<Entry<'static>>`, and a lifetime marker. `Entry::dynamic_dir` and unsafe `Entry::dynamic_file` create entries whose parent is refcounted. `Entry::dir` and `Entry::file` create entries tied to borrowed parent/data lifetimes for scoped trees. `Entry::empty` creates a null placeholder, `Entry::as_ptr` exposes the raw pointer, and `Drop` calls `debugfs_remove`.

## Control Flow
Owned directory creation passes a parent pointer or null into `debugfs_create_dir`. Owned file creation calls `debugfs_create_file_full` with the file mode, parent dentry, backing data pointer, and Rust-generated file operations. Scoped creation follows the same pattern but uses borrowed lifetimes instead of `Arc`. Empty entries are used as placeholders during pinned initialization and for disabled/failed debugfs paths.

## State and Persistence
The only persistent state is the debugfs dentry pointer plus an optional parent keepalive. The pointer invariant allows null and error pointers because `debugfs_remove` accepts them. Parent `Arc` ownership prevents a child dentry from outliving a dynamically owned parent.

## Dependencies and Integration Points
This module is private to `debugfs.rs` and uses kernel bindings for `debugfs_create_dir`, `debugfs_create_file_full`, and `debugfs_remove`. It also depends on `CStr`, `Arc`, and `FileOps<T>` to pass valid names, parents, backing data, and C vtables into debugfs.

## Risks
Safety depends on the caller ensuring backing data outlives any created file entry. The `Entry::dynamic_file` function is unsafe for that reason, and `Scope` is the higher-level mechanism that satisfies it. Another risk is forgetting a scoped `Entry` deliberately; that is correct only because the enclosing root `Entry` recursively removes the subtree.

## Test Signals
Test nested directory removal, parent-drop-before-child ordering, null/error pointer cleanup, files backed by scoped and owned data, and module unload with open debugfs files. KASAN and lockdep should stay quiet during create/remove churn.
