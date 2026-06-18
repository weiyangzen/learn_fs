# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-common.c

## Purpose
`posix-common.c` owns the lifecycle and option surface of the `storage/posix` translator. It validates the brick export directory, initializes persistent POSIX translator state, creates the hidden GFID handle hierarchy, starts background janitor/fsync/health/disk-space services, handles runtime reconfiguration, exposes statedump data, and tears the translator down.

## Important APIs, Types, And Functions
- `posix_priv(xlator_t *this)` writes statedump fields from `struct posix_private`, notably `base_path`, `base_path_length`, and atomic read/write maxima.
- `posix_notify()` forwards `GF_EVENT_PARENT_UP` as `GF_EVENT_CHILD_UP` and handles parent-down cleanup when graph shutdown starts.
- `mem_acct_init()` initializes translator memory accounting with `gf_posix_mt_end`.
- `posix_reconfigure()` applies settable volume options to an existing `struct posix_private`.
- `posix_init()` is the main constructor for `storage/posix`.
- `posix_fini()` is the destructor.
- `posix_options[]` declares the translator's volume options and defaults.

## Control Flow
Initialization rejects subvolumes, requires a `directory` option, verifies the export path, allocates `struct posix_private`, verifies xattr support, enforces `trusted.glusterfs.volume-id`, verifies or creates the root `trusted.gfid`, probes ACLs, initializes locks and atomics, opens the brick and `.glusterfs` directory fds, calls `posix_handle_init()`, sets up trash and unlink directories, enables optional AIO/io_uring, and starts disk-space, health, janitor, context-janitor, and fsyncer services.

Reconfiguration re-reads settable options for ownership, fsync batching, gfid2path, node pathinfo, pgfid link-count tracking, AIO/io_uring, disk reserve, health checking, landfill purge, create masks, hardlink limits, FIPS checksum mode, and ctime. Shutdown cancels or joins background services, closes directory fds and `mount_lock`, destroys locks/conds, and frees private state.

## State And Persistence Behavior
Persistent brick state includes `trusted.glusterfs.volume-id`, root `trusted.gfid`, `.glusterfs`, `.glusterfs/landfill`, and `.glusterfs/unlink`. Runtime state includes the base path, fd cache `arrdfd[256]`, locks, conditions, thread handles, reserve thresholds, create masks, hardlink limits, ctime mode, and gfid2path/pgfid options.

## Dependencies And Integration Points
The file integrates with `posix-handle.c`, AIO/io_uring support, disk-space and health-check workers, Gluster events/statedump, and xlator option parsing. It depends on Gluster syscall wrappers, dict helpers, thread/timer APIs, and memory accounting.

## Risks And Edge Cases
Partial initialization has a broad cleanup surface; disk-reserve reconfiguration touches shared diskxl state; missing xattr support is fatal unless explicitly allowed; hidden handle directory creation is a hard dependency; and startup deletion of `.glusterfs/unlink` must align with open-fd recovery semantics.

## Test Signals
Cover first initialization, volume-id mismatch, root GFID creation/mismatch, no-xattr backends, `.glusterfs` fd setup, option reconfigure toggles, disk reserve thread changes, hidden directory protection through entry ops, partial-init cleanup, and shutdown under live background activity.
