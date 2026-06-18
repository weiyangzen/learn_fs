# sources/cloud-native/overlayfs-tools/lib.c

Purpose: common fsck support library for prompting, xattr get/set/remove operations, and generic FTS directory scanning with callback hooks.

Important APIs/types/functions: `ask_question`, `get_xattr`, `set_xattr`, `remove_xattr`, `scan_entry_init`, `scan_check_entry`, and `scan_dir`.

Control flow: `ask_question` honors global repair-policy flags before falling back to interactive yes/no input. Xattr helpers open relative paths with `openat` and no symlink following, then perform fget/fset/fremove xattr operations. `scan_dir` uses `fts_open` with physical traversal, fills `scan_ctx`, counts files/directories, and invokes callbacks for whiteout, redirect, impurity, and impure checks on appropriate FTS events.

State and persistence: xattr helpers persist metadata mutations. `scan_dir` updates `scan_ctx.result` and transient `dirdata` stacks; prompt behavior reads global flags.

Dependencies/integration: used by `check.c` and `fsck.c`; depends on `path.c` for `basename2`, and on common allocation/printing helpers.

Risks: xattr helpers open directories read-only and no-follow, which is safer but may fail on unusual filesystem permissions. `set_xattr` tests `errno == EEXIST` after a call without first checking `ret`, so stale errno could be risky if not reset by libc behavior.

Test signals: unit fixtures for xattr existence/value, no-xattr filesystem, symlink handling, FTS callback ordering, and policy flags.
