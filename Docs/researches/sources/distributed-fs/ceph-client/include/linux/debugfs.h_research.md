# sources/distributed-fs/ceph-client/include/linux/debugfs.h

Purpose: Defines the debugfs public API for creating transient kernel debugging files, directories, attributes, simple value nodes, blobs, register dumps, arrays, automounts, and cancellation-aware file operations.

Important APIs, types, and functions: Types include `debugfs_blob_wrapper`, `debugfs_reg32`, `debugfs_regset32`, `debugfs_u32_array`, `debugfs_short_fops`, `debugfs_automount_t`, and `debugfs_cancellation`. Creation APIs cover full and short file operations via `_Generic` `debugfs_create_file()`, auxiliary data, unsafe files, file sizing, dirs, symlinks, automounts, scalar value files, strings, bools, blobs, regsets, u32 arrays, devm seqfiles, and xul helpers. Removal and lookup APIs include `debugfs_remove()`, `debugfs_lookup_and_remove()`, `debugfs_lookup()`, `debugfs_file_get/put()`, and `debugfs_change_name()`.

Control flow: Callers create a debugfs hierarchy and normally ignore `ERR_PTR()` failures because debugfs is optional. On open/read/write, helpers expose `inode->i_private`, auxiliary pointers, simple-attr parsing, or custom fops. Cancellation APIs allow file operations to register cleanup callbacks while userspace holds a file. Disabled builds return `ERR_PTR(-ENODEV)` or no-op stubs.

State and persistence: Debugfs entries are in-memory dentries/inodes under the debugfs mount and disappear on removal or module unload. They expose live kernel variables or callbacks, not stable ABI. Auxiliary data and value pointers must outlive the file unless protected by removal/cancellation.

Dependencies and integration points: Depends on VFS, seq_file, simple_attr, devices for devm seqfiles and runtime-PM register dumps, and architecture debugfs root directories. Integrates with drivers and subsystems for non-ABI diagnostics.

Risks and test signals: Risks include treating debugfs as stable userspace ABI, exposing writable unsafe state, stale pointers after module/device removal, failing to remove entries, and assuming debugfs exists. Test with `CONFIG_DEBUG_FS=y/n`, module unload while files are open, scalar read/write parsing, regset runtime PM behavior, recursive removal, and cancellation callbacks.
