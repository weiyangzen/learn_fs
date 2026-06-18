# File Research: sources/block-storage/stratisd/src/engine/strat_engine/ns.rs

## Purpose

`ns.rs` manages mount namespace isolation for stratisd private mounts. It can unshare the current thread from the root mount namespace and create a private tmpfs area under `/run/stratisd/ns_mounts`.

## Key Constants

- `INIT_MNT_NS_PATH = "/proc/1/ns/mnt"`
- `NS_TMPFS_LOCATION = "/run/stratisd/ns_mounts"`

## Public Functions

- `unshare_mount_namespace()`
  - Checks if the current thread is in the root mount namespace.
  - Calls `unshare(CLONE_NEWNS)` only when needed.
  - Asserts afterward that the thread is no longer in the root mount namespace.
- `is_in_root_mount_namespace()`
  - Compares device and inode of `/proc/1/ns/mnt` with `/proc/self/task/<tid>/ns/mnt`.

## Key Type

`MemoryFilesystem` represents a mounted tmpfs used for private namespace mounts.

`MemoryFilesystem::new()`:

- Ensures `NS_TMPFS_LOCATION` exists and is a directory.
- If a mount already exists there, attempts to unmount it.
- Mounts a 1 MiB tmpfs.
- Remounts it as recursive slave/private enough to keep nested mounts from propagating out.
- Returns a guard object.

`Drop` for `MemoryFilesystem` unmounts the tmpfs and logs warnings on failure.

## Dependencies and Interactions

- Uses `nix::sched::unshare`.
- Uses `nix::mount::{mount, umount}`.
- Uses `stat()` to detect namespace identity and existing mounts.
- Converts filesystem errors into `StratisError`.

## Notable Edge Cases

- The precondition notes container behavior: if running in a container, PID must not be 1 or the container must share host PID.
- Existing non-directory path at `NS_TMPFS_LOCATION` is an error.
- Existing mounted filesystem at the namespace mount path is best-effort unmounted before remounting.
