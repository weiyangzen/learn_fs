## sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils.go

Purpose: Linux helpers to create ID-mapped bind mounts using another process's user namespace and to spawn a helper user namespace process.

Important APIs/types/functions: `CreateIDMappedMount` and `CreateUsernsProcess`.

Control flow: `CreateIDMappedMount` opens `/proc/<pid>/ns/user`, clones the source mount with `open_tree`, sets `MOUNT_ATTR_IDMAP` with the user namespace fd, creates target directory, then moves the cloned mount to target. `CreateUsernsProcess` calls `clone(CLONE_NEWUSER|SIGCHLD)`, makes the child pause until killed, writes `uid_map` and `gid_map`, and returns pid plus cleanup function.

State and persistence: creates target directories, attaches mounts, spawns/kills a process, and writes `/proc/<pid>/{uid,gid}_map`.

Dependencies and integration points: works with `idtools.IDMap` and storage drivers needing idmapped mounts. Depends on modern Linux mount APIs and architecture-specific clone argument ordering for s390x.

Risks: requires kernel support and sufficient privileges; `gid_map` writes can require setgroups handling in some contexts; cleanup must be called to avoid lingering paused helper process. Partial failures call cleanup after map write errors.

Test signals: no selected tests directly cover idmapped mount creation.
