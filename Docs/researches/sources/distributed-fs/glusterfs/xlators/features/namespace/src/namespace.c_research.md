# sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.c

## Purpose

`namespace.c` implements a translator that tags each request's root with a namespace hash, derived from the top-level path component, so later translators can throttle, account, log, or otherwise group fops by namespace.

## Important APIs, Types, and Functions

Core helpers are `parse_path`, `ns_inode_ctx_put`, `ns_inode_ctx_get`, `set_ns_from_loc`, `set_ns_from_fd`, `get_path_resume_cbk`, and the `GET_ANCESTRY_PATH_WIND` macro. Nearly every Gluster fop has an `ns_*` wrapper in the `fops` table, including create, lookup, read/write, xattr, lock, directory, fallocate, discard, and zerofill operations. Lifecycle hooks are `init`, `fini`, `reconfigure`, and `ns_forget`.

## Control Flow

Each fop wrapper attempts to populate `frame->root->ns_info`. Loc-based operations call `set_ns_from_loc`; fd-based operations call `set_ns_from_fd`. These helpers reset the namespace info, honor the `tag-namespaces` option, try cached inode context first, then parse a loc path or an `inode_path` result. The parser hashes the first path component after leading slashes with `SuperFastHash`; root hashes `/`. If the path looks like a GFID pseudo-path beginning with `<`, the fop creates a separate privileged frame, builds a call stub for the original operation, winds `getxattr` for `GET_ANCESTRY_PATH_KEY`, parses the returned path in `get_path_resume_cbk`, caches it on the inode, destroys the temporary frame, and resumes the original fop.

After namespace tagging, the original fop is passed to `FIRST_CHILD(this)` with the default callback. `ns_getspec` is the only simple pass-through that does not set namespace information.

## State and Persistence Behavior

Runtime state is `ns_private_t` in `this->private`, holding the `tag_namespaces` boolean. Per-inode cached namespace state is a heap-allocated `ns_info_t` stored through inode context and freed by `ns_forget`. Per-fallback request state is `ns_local_t`, which owns a fake loc and resume stub until `get_path_resume_cbk` resumes the original fop. No disk state is written by this translator.

## Dependencies and Integration Points

The translator depends on `SuperFastHash`, Gluster frame `root->ns_info`, inode contexts, call stubs, default fop callbacks, and the ancestry xattr convention `GET_ANCESTRY_PATH_KEY` supplied by lower layers such as POSIX. It must have exactly one child.

## Risks and Edge Cases

There is a likely bug in `set_ns_from_loc`: after `inode_path` succeeds into local variable `path`, it calls `parse_path(info, loc->path)` instead of `parse_path(info, path)`, so GFID fallback may still parse the GFID-style loc path. `ns_inode_ctx_put` allocates a fresh cached object without checking/replacing an existing context, which could leak if called repeatedly for the same inode. The fallback macro has several `goto wind` paths after partially allocating frames or stubs, which can leak those allocations. Namespace tagging is best effort: disabled config, missing paths, missing inode, or failed ancestry lookup still pass the fop through untagged.

## Test Signals

Tests should cover hashing of root, single-component paths, nested paths, repeated slashes, GFID pseudo-paths, fd-based fops with cached and uncached inode contexts, ancestry lookup fallback, reconfigure toggling `tag-namespaces`, `ns_forget` cleanup, and all fop classes preserving original arguments while setting or clearing `frame->root->ns_info`.
