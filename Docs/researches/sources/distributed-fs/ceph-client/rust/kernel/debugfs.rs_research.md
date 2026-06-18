# sources/distributed-fs/ceph-client/rust/kernel/debugfs.rs

## Purpose
`debugfs.rs` is the top-level Rust abstraction for Linux debugfs. It gives drivers an owning `Dir`, `File<T>`, and `Scope<T>` API for creating debugfs directories and files whose backing data lifetimes are tied to Rust ownership instead of open-coded `debugfs_create_*` calls. When `CONFIG_DEBUG_FS` is disabled, the API compiles to inert handles so callers do not need conditional code.

## Important APIs, Types, and Functions
The main public types are `Dir`, `File<T>`, `Scope<T>`, and `ScopedDir<'data, 'dir>`. `Dir::new`, `Dir::subdir`, `Dir::read_only_file`, `Dir::read_binary_file`, `Dir::read_callback_file`, `Dir::read_write_file`, `Dir::read_write_binary_file`, `Dir::read_write_callback_file`, `Dir::write_only_file`, `Dir::write_binary_file`, `Dir::write_callback_file`, and `Dir::scope` cover owned debugfs entries. `Scope::dir` creates a root scoped tree. `ScopedDir` mirrors the file creation methods for borrowed data whose lifetime is proven by the enclosing `Scope`.

## Control Flow
Directory creation routes through private `Dir::create`, which either stores an `Arc<Entry<'static>>` to keep parent dentries alive or records `None` when allocation fails. File creation routes through `Dir::create_file`, which builds a pinned `Scope<T>` and then creates the debugfs `Entry` only after `data` is initialized. Scoped trees create a `ScopedDir`, run the caller's initializer to populate files, and finally move the underlying `Entry` into the owning `Scope`.

## State and Persistence
State is entirely in-memory and debugfs-backed. `Dir` keeps an optional refcounted `Entry`, `Scope<T>` stores the backing data and the tree entry, and `File<T>` wraps a scope. Drop order is load-bearing: the debugfs entry is removed before the backing data is dropped. `PhantomPinned` prevents moving backing data after file private pointers are published.

## Dependencies and Integration Points
This file integrates the local `entry`, `file_ops`, `traits`, and `callback_adapters` modules with kernel `PinInit`, `Arc`, `CStr`, `fmt`, and `UserSliceReader` infrastructure. It is the driver-facing entry point for exporting formatted or binary diagnostic state through debugfs.

## Risks
The main risks are lifetime and drop-order mistakes around file private data, especially because C debugfs stores raw pointers. Callback adapters require non-capturing, zero-sized closures. The private `scoped_dir` and `ScopedDir::new` APIs are intentionally not public because extracting entries incorrectly can leak directories. Disabled-debugfs behavior silently drops entries, so tests must cover both config paths.

## Test Signals
Useful signals include Rust doctests/build tests for each constructor, runtime creation and removal of nested debugfs trees, reads and writes through trait-backed and callback-backed files, module unload while files are open, allocation-failure paths that produce `Dir(None)`, and builds with `CONFIG_DEBUG_FS=n`.
