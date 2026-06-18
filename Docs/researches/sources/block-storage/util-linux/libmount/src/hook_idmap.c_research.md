# File Research: sources/block-storage/util-linux/libmount/src/hook_idmap.c

This conditional Linux hook implements `X-mount.idmap=` for idmapped mounts using the mount fd API and `mount_setattr(MOUNT_ATTR_IDMAP)`.

Key components:

- `struct id_map` stores uid/gid/both mappings as namespace ID, host ID, and range triples.
- `struct hook_data` owns the user namespace FD and the parsed mapping list.
- `hook_prepare_options()` parses `X-mount.idmap=` and registers a post-mount hook.
- `hook_mount_post()` clones or reuses a detached mount tree, applies the ID mapping, and attaches it to the target.
- `hookset_deinit()` removes hooks and closes/free parsed state.

Important behavior:

- Values beginning with `/` are treated as paths to an existing user namespace and opened with validation through `NS_GET_OWNER_UID` when available.
- Otherwise the option is parsed as entries of `[b|u|g:]id-mount:id-host:id-range`, separated by spaces. `b:` or no prefix applies to both uid and gid maps.
- For explicit mappings, `get_userns_fd_from_idmap()` forks a child, unshares a user namespace, waits for the parent to write `/proc/<pid>/{u,g}id_map`, then opens `/proc/<pid>/ns/user`.
- Non-root gid mapping writes first write `deny\n` to `/proc/<pid>/setgroups` when available.
- Post-mount handling uses `open_tree(... OPEN_TREE_CLONE ...)`, `mount_setattr(... MOUNT_ATTR_IDMAP ...)`, detaches the old target if using a private clone, then `move_mount()`s the idmapped tree to the final target.
- `cxt->force_clone = 1` forces clone-based mount behavior so the mount can be idmapped before final attachment.

Dependencies and interactions:

- Active only with `HAVE_MOUNTFD_API` and `HAVE_LINUX_MOUNT_H`.
- Coordinates with `hook_mount.c` through `mnt_context_get_sysapi()` and `force_clone`.
- Uses namespace, socketpair, fork/wait, and `/proc` uid/gid map mechanics.

Risk notes:

- The map buffer is fixed at 4096 bytes because kernel uid/gid map writes are limited; overflow is detected through `snprintf()` return handling but very large mapping sets will fail.
- Failure after cloning but before move can leave the original target detached only after `umount2()` is reached; current code detaches after successful `mount_setattr()`.
- This feature depends heavily on kernel/user namespace permissions and will fail in restricted environments.
