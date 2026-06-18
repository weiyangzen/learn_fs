<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync_types.h

## Purpose

`xe_sync_types.h` defines the per-sync-entry state used while translating userspace sync objects into dma-fence operations.

## Important APIs, Types, and Functions

`struct xe_sync_entry` stores an optional DRM syncobj, input fence, timeline chain fence, user-fence chain fence, internal user-fence syncobj, `xe_user_fence`, user address, timeline values, type, and flags.

## Control Flow

Parsing fills the fields according to sync type and signal direction. Later dependency, wait, signal, and cleanup helpers consume the populated fields.

## State and Persistence Behavior

Entries are transient per ioctl/job submission. Reference fields must be released by `xe_sync_entry_cleanup()`.

## Dependencies and Integration Points

The header forward declares DRM syncobj, dma-fence, chain, uABI sync, and user fence types. It is consumed by the sync implementation and ioctl paths.

## Risks and Test Signals

Partially initialized entries on parse failure are a cleanup risk. Tests should exercise parse failure after each allocation point and confirm cleanup handles NULL fields safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync_types.h -->
