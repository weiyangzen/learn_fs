# sources/distributed-fs/ceph-client/drivers/greybus/debugfs.c

## Purpose

`debugfs.c` owns the top-level Greybus debugfs directory. It provides one shared root dentry, `greybus`, under which other Greybus components such as SVC power monitoring and ES2 APB logging create their diagnostic files.

## Important APIs, Types, and Functions

- `gb_debugfs_init()` creates the root directory with `debugfs_create_dir("greybus", NULL)`.
- `gb_debugfs_cleanup()` recursively removes the tree and clears the global root pointer.
- `gb_debugfs_get()` returns the current root dentry and is exported to other Greybus modules.
- `gb_debug_root` is the only persistent state in this file.

## Control Flow

The Greybus core calls `gb_debugfs_init()` before registering the bus. Subsystems call `gb_debugfs_get()` when they add diagnostic files. Module exit calls `gb_debugfs_cleanup()`, which removes all descendants even if individual users did not remove their own files first.

## State and Persistence Behavior

The debugfs root persists for the lifetime of the Greybus core. It is not reference counted. Callers must be prepared for debugfs to be unavailable or for file creation to fail, as standard debugfs helpers may return `NULL` or error-like dentries depending on configuration.

## Dependencies and Integration Points

The file integrates with Linux debugfs and is included through `linux/greybus.h` declarations. `svc.c` creates per-SVC and pwrmon directories below this root; `es2.c` creates APB log files below it.

## Risks and Edge Cases

- `gb_debugfs_get()` can return `NULL` before initialization or after cleanup.
- Debugfs has no ABI guarantees; these files should remain diagnostics only.
- Because cleanup is recursive, double-removal by consumers is normally harmless, but dangling private data in open debugfs files can still be a lifecycle concern in users.

## Test Signals

Check that `/sys/kernel/debug/greybus` appears after Greybus core init, disappears after unload, accepts nested SVC/ES2 debugfs files, and that cleanup behaves correctly when consumers create no files or when debugfs is disabled.
