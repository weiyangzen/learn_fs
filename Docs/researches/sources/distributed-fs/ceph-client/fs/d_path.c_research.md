# sources/distributed-fs/ceph-client/fs/d_path.c

## Purpose
`d_path.c` implements kernel helpers and the `getcwd` syscall path for converting dentries and mounts into printable path strings. It builds paths backwards into caller buffers while tolerating concurrent renames and mount changes.

## Important APIs, Types, and Functions
- `struct prepend_buffer` and helpers `prepend_char()`, `prepend_copy()`, `prepend()`, `prepend_name()`, and `extract_string()` manage reverse buffer construction and overflow reporting.
- `__prepend_path()` walks dentries and mounts up to a root and reports normal, absolute-root, detached, or escaped states.
- `prepend_path()` wraps the path walk with RCU and sequence retry handling for `rename_lock` and `mount_lock`.
- Public helpers include `__d_path()`, `d_absolute_path()`, `d_path()`, `dynamic_dname()`, `simple_dname()`, `dentry_path_raw()`, and `dentry_path()`.
- `SYSCALL_DEFINE2(getcwd)` implements the kernel side of `getcwd(2)`.

## Control Flow
The core algorithm starts at the target dentry and prepends `/name` components until it reaches the supplied root or a mount boundary. At mount roots it crosses to the parent mountpoint unless the mount is global root or detached. The optimistic RCU walk uses sequence counters; if rename or mount sequence validation fails, it retries under the relevant lock mode. `d_path()` first handles synthetic `d_dname` dentries, then uses the caller's current root and adds `" (deleted)"` for unlinked dentries.

## State and Persistence
This file does not persist state. It reads dentry names, parent pointers, mount parent/mountpoint pointers, current task root/pwd, and dentry deleted state. Outputs are transient strings placed at an offset inside the caller buffer.

## Dependencies and Integration
It depends on VFS dentry/mount internals, `fs_struct` sequence counters, RCU, seqcount helpers, safe kernel nofault copying, user-copy helpers, and syscall allocation helpers. Its exported functions are used by procfs, audit/logging, filesystem diagnostics, and callers that need stable textual paths.

## Risks and Edge Cases
- Name pointer and length can be mismatched during rename; `prepend_copy()` fills faulted regions with placeholder bytes and relies on sequence retry to discard bad output.
- Return pointers usually point inside the supplied buffer, not necessarily at its beginning.
- Deleted path suffixes are ambiguous by design.
- `__d_path()` returns `NULL` when unreachable from the supplied root; `d_absolute_path()` returns `-EINVAL` for detached/unreachable paths beyond allowed root behavior.
- Buffer overflow is tracked by setting `len` negative and returning `-ENAMETOOLONG`.
- `getcwd()` prepends `"(unreachable)"` if cwd is outside the process root.

## Test Signals
Exercise path generation under concurrent rename/mount movement, deleted dentries, synthetic `d_dname` dentries, detached mounts, unreachable cwd, too-small buffers, root path handling, and user-copy failures in `getcwd`.
