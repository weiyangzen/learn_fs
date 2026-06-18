# sources/distributed-fs/ceph-client/fs/binfmt_misc.c

## Purpose
Implements `binfmt_misc`, a pseudo-filesystem and binary-format handler that lets users register interpreter rules matched by filename extension or file magic. It supports per-user-namespace handler instances, global fallback to ancestor namespaces, handler enable/disable/delete operations, and flags controlling argv preservation, opened binary fd passing, credential behavior, and interpreter-file pinning.

## Important APIs, Types, And Functions
The central type is `Node`, representing one registered handler. It stores list linkage, flags, magic or extension data, mask, interpreter path, entry name, dentry, optional pinned interpreter file, and a refcount protecting concurrent exec against removal.

Exec integration is through `misc_format.load_binary = load_misc_binary`. Handler lookup uses `load_binfmt_misc()`, `get_binfmt_handler()`, and `search_binfmt_handler()`. Registration and control are exposed through the `binfmt_misc` filesystem: `/register` via `bm_register_write()`, `/status` via `bm_status_read()`/`bm_status_write()`, and per-entry files via `bm_entry_read()`/`bm_entry_write()`. Parsing helpers include `create_entry()`, `scanarg()`, `check_special_flags()`, and `parse_command()`. Filesystem lifecycle is implemented by `bm_fill_super()`, `bm_get_tree()`, `bm_init_fs_context()`, `bm_evict_inode()`, and `bm_put_super()`.

## Control Flow
At initialization, `init_misc_binfmt()` registers the `binfmt_misc` filesystem and inserts the binfmt handler. Mounting the filesystem lazily allocates `struct binfmt_misc` for the current user namespace, initializes its entries list and lock, publishes it with release semantics to `user_ns->binfmt_misc`, resets `enabled`, and creates `status` and `register` files.

Writing to `/register` passes a delimited string of the form `:name:type:offset:magic:mask:interpreter:flags` to `create_entry()`. Magic rules parse a decimal offset, escaped magic, optional escaped mask, decode hex escapes in place, and validate the match range against `BINPRM_BUF_SIZE`. Extension rules validate the extension field. Flags `P`, `O`, `C`, and `F` set preserve-argv0, open-binary, credentials, and pinned-interpreter behavior. `F` opens the interpreter at registration time using the register file's credentials. `add_entry()` creates a persistent dentry and adds the node to the namespace handler list.

During exec, `load_misc_binary()` finds the applicable namespace instance by walking from current user namespace to ancestors. If enabled, it refcounts the first matching enabled handler under `entries_lock`. It rejects path-inaccessible binaries, optionally removes the original argv0, sets `have_execfd` for open-binary mode, pushes the original binary path and interpreter as arguments, changes `bprm->interp`, opens or clones the interpreter file, sets `bprm->interpreter`, optionally marks `execfd_creds`, and drops the handler reference.

Writes of `0`, `1`, and `-1` disable, enable, or delete entries/global state. Deletion removes list entries under the root inode lock and `entries_lock`, then uses recursive dentry removal. Inode eviction finally drops the node reference and closes pinned interpreter files when the last exec user releases it.

## State And Persistence
Handler state lives in memory under each user namespace's `binfmt_misc` object and is represented as pseudo-files in the mounted filesystem. It is not persisted across reboot or namespace teardown. Per-entry `Enabled` bits and global `misc->enabled` affect future execs. `MISC_FMT_OPEN_FILE` pins an interpreter `struct file`, so registration captures a specific opened executable until the handler is deleted and all users finish.

## Dependencies And Integration Points
The code integrates with the exec subsystem, user namespaces, VFS simple filesystem helpers, dcache persistent dentries, file opening and write-denial APIs, memory barriers for namespace publication, and `string_unescape_inplace()`/`bin2hex()` for user-visible rule encoding. It also depends on `BINPRM_BUF_SIZE` because magic matching only sees the initial exec buffer.

## Risks
Rule parsing is exposed to userspace and must reject malformed delimiters, names, escapes, offsets, and masks without leaking memory. Concurrency between exec and handler deletion is subtle: list locking, inode locking, refcounts, and dentry eviction must cooperate so a handler is neither used after free nor leaked. The `F` flag changes semantics by pinning an interpreter opened under registration credentials; mistakes here can cause stale interpreter execution or unexpected credential boundaries. Namespace fallback means handlers in an ancestor namespace can affect descendants unless a child mounts its own instance.

## Test Signals
Useful tests include registering extension and magic handlers; matching with and without masks; invalid register strings; enable, disable, and delete commands on entries and global status; concurrent exec while deleting a handler; user-namespace mounts and ancestor fallback; `P`, `O`, `C`, and `F` flag combinations; path-inaccessible binaries; and verifying `/status` and per-entry reads emit the expected state.
