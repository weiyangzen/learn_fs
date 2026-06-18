# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-helpers.c

## Purpose

`fuse-helpers.c` implements common support routines for the FUSE bridge: request-state allocation/freeing, GlusterFS call frame creation, caller group collection and caching, inode/nodeid and loc conversion, stat and dirent conversion to FUSE wire structures, and FUSE xattr namespace/policy helpers. These functions are used by the main bridge and resolver code to keep operation handlers focused on protocol and FOP flow.

## Important APIs and Functions

- `free_fuse_state` releases a completed `fuse_state_t`, wipes locs and resolve state, unrefs dicts and fds, frees the input header and name, decrements active-subvolume wind count, and notifies a switched graph when its last in-flight request completes.
- `get_fuse_state` allocates request state, waits for graph migration to stop accepting paused requests, selects the active subvolume, increments its `winds` counter, stores the active inode table and pool, and initializes the state lock.
- `get_call_frame_for_req` creates a GlusterFS frame, copies UID/GID/PID and lock owner from the FUSE header, loads supplementary groups, applies configured client PID override, and marks the frame as a FOP.
- `frame_fill_groups` populates supplemental groups from `getgrouplist` or platform process credential sources. Linux can read `/proc/<pid>/status`; Solaris reads `/proc/<pid>/cred`; Darwin/BSD use `sysctl`; unsupported platforms set zero groups.
- `get_groups` wraps `frame_fill_groups` with `gid_cache` lookup and insertion, and supports `gid-timeout = -1` as a way to suppress supplemental groups.
- `fuse_ino_to_inode` converts FUSE nodeid `1` to the active root inode and non-root nodeids back to referenced `inode_t *` pointers.
- `inode_to_fuse_nodeid` maps root GFID to `1` and non-root inodes to pointer-valued nodeids.
- `fuse_loc_fill` builds a GlusterFS `loc_t` for either an entry under a parent/name or an inode, including parent/inode refs, GFIDs, path, and basename.
- `gf_fuse_stat2attr` converts GlusterFS `struct iatt` into `struct fuse_attr`, including optional 32-bit inode squashing and Darwin-specific fields.
- `gf_fuse_fill_dirent` converts `gf_dirent_t` fields into a FUSE dirent payload.
- `fuse_flip_xattr_ns`, `fuse_do_flip_xattr_ns`, and `fuse_xattr_alloc_default` selectively translate geo-replication xattrs from unprivileged `system.*` namespace to `trusted.*`.
- `fuse_ignore_xattr_set` enforces which non-user xattrs geo-replication (`GF_CLIENT_PID_GSYNCD`) may set.
- `fuse_check_selinux_cap_xattr` allows or denies `security.selinux` and `security.capability` according to mount options.

## Control Flow

`get_fuse_state` is the first helper used by most FUSE handlers. It allocates zeroed state, waits on `priv->migrate_cond` while `handle_graph_switch` is true, snapshots the current active subvolume, increments `active_subvol->winds` under `priv->sync_mutex`, records the active inode table and call pool, attaches the FUSE input header, and initializes the per-state lock. This makes the request count visible to graph-switch teardown logic.

`get_call_frame_for_req` is called by the `FUSE_FOP` macro and some interrupt handlers. It creates a frame, records the operation number for logging, copies request credentials from the FUSE header, stores the lock owner when present, then fills supplemental groups. If `client-pid` was configured, it overrides the frame root PID after group collection. This frame is then wound into lower translators.

Group lookup first checks `priv->gid_cache_timeout`. With no cache configured, `frame_fill_groups` runs directly. With timeout `-1`, groups are disabled. Otherwise, `gid_cache_lookup` can satisfy the request; misses call platform-specific collection and then add a new cache entry.

`fuse_loc_fill` handles two resolution shapes. For parent/name requests, it resolves or reuses the parent inode, searches the child with `inode_grep`, and builds the path with `inode_path(parent, name, &path)`. For inode requests, it resolves the inode by nodeid, finds a parent with `inode_parent`, and builds an inode path. It then sets `loc->name` from the last path component and rejects non-root locs without parents.

Xattr helpers are policy filters used before main FUSE handlers enter the GlusterFS stack. Geo-replication may request selected `system.glusterfs.*` keys and have them translated to `trusted.glusterfs.*`; disallowed xattr sets return `-1`; ACL/SELinux/capability helpers let the bridge return `EOPNOTSUPP`/`ENODATA` before lower translators see unsupported metadata.

## State and Persistence Behavior

This file manages in-memory request and credential state. `free_fuse_state` is the authoritative cleanup path for `fuse_state_t`. It releases `state->loc`, `state->loc2`, `state->xdata`, `state->xattr`, `state->name`, `state->fd`, `state->finh`, and both resolve structures. In debug builds it poisons the state before freeing.

Graph-switch persistence is represented by `active_subvol->winds` and `active_subvol->switched`. Every request created by `get_fuse_state` increments winds; `free_fuse_state` decrements it and sends `GF_EVENT_PARENT_DOWN` when a switched graph reaches zero active requests.

Supplemental group state lives on the call stack. Cached group lists live in `priv->gid_cache`, keyed by PID/UID/GID. The helper allocates and transfers group arrays through `call_stack_set_groups` or `call_stack_alloc_groups`.

Loc and inode conversion functions manipulate inode refs and paths. The path allocated by `inode_path` becomes owned by the loc and is later released by `loc_wipe`.

Xattr helper allocations return duplicated or newly built key strings through `nkey`; callers own and eventually free or transfer those strings into dict state.

## Dependencies and Integration Points

The file depends on `fuse-bridge.h`, GlusterFS inode, fd, loc, dict, gid cache, call-stack, UUID, logging, and memory helpers. Platform integration includes Linux `/proc`, `getpwuid_r`, `gf_getgrouplist`, Solaris procfs credentials, BSD/Darwin `sysctl`, and standard password/group APIs.

It integrates with the main FUSE bridge through the declared helper prototypes in `fuse-bridge.h`, with resolver code through `fuse_resolve_t` cleanup, and with graph-switch logic through `priv->sync_mutex`, `priv->migrate_cond`, `active_subvol->winds`, and `active_subvol->switched`.

## Risks and Edge Cases

- `get_fuse_state` assumes an active subvolume exists and increments `active_subvol->winds` without a local null check. The broader graph setup must guarantee this before FUSE handlers run.
- `free_fuse_state` assumes `state`, `state->this`, and `state->active_subvol` are valid. Shallow copies of `fuse_state_t`, such as interrupt helper copies, must not be passed through full cleanup unless ownership is correct.
- Group collection from `/proc/<pid>/status` is race-prone when the process exits or PID namespaces are involved. PID zero is treated as a container-oriented special case with group zero.
- The Linux group parser retries after resizing, but it caps at `GF_MAX_AUX_GROUPS`; callers should not assume all groups are always preserved.
- `gid_cache_add` ownership of `agl.gl_list` depends on return value; failure frees locally.
- `fuse_loc_fill` is designed to resist repeated invocation leaks, but callers must still avoid reusing a partially filled loc incorrectly.
- `fuse_ino_to_inode` pointer-casts non-root nodeids and immediately `inode_ref`s them; invalid/stale kernel nodeids would be dangerous if lookup accounting failed elsewhere.
- `gf_fuse_fill_dirent` copies `d_len` bytes without appending NUL, which is correct for FUSE dirent format but important for consumers expecting strings.
- Xattr namespace flipping assumes the original key contains `.` and asserts in `fuse_do_flip_xattr_ns`; callers should only pass expected namespace-style keys.
- `fuse_ignore_xattr_set` intentionally allows `user.*` regardless of geo-replication restrictions and has a tightly curated allowlist for non-user namespaces.

## Test Signals

Targeted tests should cover request allocation during graph migration, wind count decrement and parent-down notification, cleanup of every owned `fuse_state_t` field on success and failure, group collection with cache hit/miss/disabled modes, PID zero fallback, missing `/proc` entries, `client-pid` override behavior, root and non-root nodeid conversion, `fuse_loc_fill` for parent/name and inode-only cases, inode path failure behavior, 32-bit inode squashing in `gf_fuse_stat2attr` and `gf_fuse_fill_dirent`, geo-rep xattr namespace flipping, xattr allow/deny matrices, ACL disabled behavior, and SELinux/capability option combinations.
