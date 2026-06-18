# Group Research: group_324_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer_hammer_io_c__2619335a72ff

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_io.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_io.c

## Purpose
Implements HAMMER’s low-level I/O primitives, buffer-cache association rules, dirty tracking, write ordering hooks, and direct data I/O paths.

## Key Elements
- Defines the modified-I/O red-black tree ordering for volume/buffer dirty lists.
- Initializes and classifies `hammer_io` objects by HAMMER zone.
- Manages passive association between kernel `struct buf` objects and HAMMER volume/buffer structures.
- Provides `hammer_io_read()`, `hammer_io_new()`, `hammer_io_release()`, and `hammer_io_flush()` for loading, creating, releasing, and explicitly flushing backing buffers.
- Tracks dirty metadata/data/undo/volume buffers through `volu_root`, `meta_root`, `undo_root`, `data_root`, and `lose_root`.
- Generates undo records before modifying volume or buffer on-disk bytes via `hammer_modify_volume()` and `hammer_modify_buffer()`.
- Installs `hammer_bioops` callbacks to control kernel writeback, completion, deallocation, and dependency checks.
- Implements direct frontend vnode read/write helpers for large data records, including CRC verification, indirect read mode, async direct-write completion, stale alias invalidation, and device flush commands.

## Dependencies
Uses DragonFlyBSD buffer/bio/vnode APIs from `<sys/buf2.h>` and HAMMER internals from `hammer.h`: blockmap lookup, volume lookup, buffer synchronization/deletion, undo generation, CRC helpers, inode scanning, and flusher/device flush state.

## Behavior/Risks
Metadata and volume buffers are not allowed to be written by ordinary kernel writeback; HAMMER’s flusher must explicitly write them. Data and undo buffers may be released to kernel writeback under controlled conditions. The file is concurrency-sensitive: correctness depends on `io_token`, reference/interlock state, `B_LOCKED`, `modify_refs`, and careful passive buffer disassociation. Direct I/O paths must invalidate or sync aliases so reblocking, mirroring, and frontend vnode buffers do not observe stale data.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.c

## Purpose
Implements the kernel-side HAMMER ioctl dispatcher and local handlers for history, sync TIDs, versioning, filesystem info, snapshots, cleanup config records, and raw data lookup.

## Key Elements
- `hammer_ioctl()` wraps each request in a HAMMER transaction and dispatches by `HAMMERIOC_*` command.
- Mutating commands check read-only state and privilege status before invoking prune, reblock, rebalance, PFS, mirror-write, version-set, volume, snapshot, config-set, and dedup operations.
- Delegates major maintenance operations to other modules: prune, reblock, rebalance, PFS management, mirroring, volume add/delete/list, and dedup.
- `hammer_ioc_gethistory()` scans B-tree records for create/delete TIDs over inode or key-specific history ranges.
- `hammer_ioc_synctid()` triggers no-op, async, single-sync, or double-sync flusher behavior and reports a synchronization TID.
- `hammer_ioc_get_version()` reports supported HAMMER volume versions and descriptions; `hammer_ioc_set_version()` upgrades/downgrades permitted versions and updates the root volume header.
- Snapshot handlers add, delete, and enumerate per-PFS snapshot records under `snapshot_lock`.
- Config handlers read or replace the per-PFS cleanup configuration record.
- `hammer_ioc_get_data()` looks up a supplied B-tree key, extracts leaf/data, and copies bounded data to userland.

## Dependencies
Uses HAMMER transaction, cursor, B-tree, snapshot, flusher, PFS, volume, reblock/rebalance/prune, dedup, and volume-header APIs exposed through `hammer.h`.

## Behavior/Risks
Several ioctl handlers return `0` while placing operation status in `head.error`, matching ioctl continuation semantics. Snapshot/config updates retry on `EDEADLK`. Version changes are guarded but can trigger structural migration such as undo FIFO upgrade. History logic special-cases regular file data keys because HAMMER stores data record keys as `base + length`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.h

## Purpose
Defines the user/kernel HAMMER ioctl ABI, including command numbers, shared request structures, mirror stream record formats, and operation flags.

## Key Elements
- Common `hammer_ioc_head` carries flags, error, and reserved ABI space.
- Defines prune, rebalance, history, reblock, synctid, info, PFS, mirror, version, volume, snapshot, config, dedup, and get-data request structures.
- Documents iteration fields such as `key_beg`, `key_end`, `key_cur`, `nxt_tid`, `nxt_key`, `index`, and `count`.
- Defines mirror stream records: generic header, record payload, skip range, update, sync, PFS data, and union wrapper.
- Defines mirror record types and CRC/error/no-data flags, including byte-order signature constants.
- Provides ioctl command IDs `HAMMERIOC_PRUNE` through `HAMMERIOC_SCAN_PSEUDOFS`.

## Dependencies
Includes `<sys/param.h>`, `<sys/ioccom.h>`, and `hammer_disk.h`, making it usable from userland as well as kernel code.

## Behavior/Risks
This is a stable ABI surface. Structure sizes, reserved fields, aligned mirror records, and flag meanings are part of userland compatibility. The header explicitly notes that config records are not mirrored and that snapshot get results may require caller-side sorting due to signed B-tree key ordering.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mirror.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mirror.c

## Purpose
Implements HAMMER mirror read/write ioctls that serialize modified B-tree records to userland and apply mirror streams to a target PFS.

## Key Elements
- `hammer_ioc_mirror_read()` scans a PFS-localized B-tree range with mirror-TID filtering and emits aligned mirror records into a user buffer.
- Emits `REC`, `PASS`, and `SKIP` records. Internal B-tree mirror-filter hits become skip ranges; older records become pass records so the receiver can delete gaps.
- Optionally omits bulk data with `HAMMER_IOC_MIRROR_NODATA`.
- Handles data CRC-domain errors as non-fatal stream flags so userland can wash or report damaged data.
- `hammer_ioc_mirror_write()` validates stream records, checks space/flusher pressure, and applies skip, record, and pass records.
- Write helpers delete target records absent from the source, create missing records, and update existing records only by delete TID.
- Filters non-mirrored record types, currently excluding cleanup config records.

## Dependencies
Uses HAMMER cursor/B-tree APIs, mirror-filter cursor state, CRC helpers, copyin/copyout, PFS localization helpers, flusher pressure checks, space checks, and generic record create/delete helpers in `hammer_object.c`.

## Behavior/Risks
Mirror write always returns `0` to preserve updated continuation fields and records cumulative failures in `mirror->head`. The stream is sensitive to localization remapping and record ordering. Bad data CRC records may be ignored on write. Correct deletion depends on careful cursor progress through `key_cur`, `ATEDISK`, skip boundaries, and `tid_end`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mirror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mount.h

## Purpose
Defines the userland-to-kernel HAMMER mount argument structure and public mount flags.

## Key Elements
- `struct hammer_mount_info` carries volume device names, volume count, HAMMER-specific flags, mirror master ID, and `asof` mount TID.
- `master_id` supports no-mirror mode via `-1` or mirror master IDs `0-15`.
- Defines mount flags for no-history, explicit master ID, no mirror, and dirty undo state.
- `HMNT_USERFLAGS` limits user-settable mount flags to no-history, master ID, and no-mirror.

## Dependencies
Includes `<sys/types.h>` and `<sys/mount.h>` with include guards so it can be shared by mount tooling and kernel code.

## Behavior/Risks
This is a small ABI header. Reserved fields preserve structure layout compatibility, including space formerly used for export arguments.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_object.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_object.c

## Purpose
Manages HAMMER object records: in-memory frontend records, merged in-memory/on-disk lookup and iteration, backend record flushing, range deletion, generic media record creation, and B-tree record deletion.

## Key Elements
- Builds an inode-local red-black tree of pending memory records with comparison functions for exact lookup, range scan, overlap detection, and truncation.
- Allocates, references, waits on, releases, and destroys `hammer_record` objects, including target inode dependency handling and reservation cleanup.
- Implements frontend operations for directory entry add/delete, generic record add, bulk data reservation, bulk replacement, and frontend truncation.
- Uses flags such as `DELETED_FE`, `DELETED_BE`, `COMMITTED`, `INTERLOCK_BE`, and cursor delete visibility to distinguish frontend and backend views.
- `hammer_ip_sync_record_cursor()` flushes memory records to media, deletes overwritten ranges, allocates/copies data, inserts B-tree leaves, handles direct-write completion, and converts certain directory-add records into covering deletes.
- `hammer_ip_lookup()`, `hammer_ip_first()`, and `hammer_ip_next()` merge in-memory records with on-disk B-tree records while handling generation changes and duplicate/overwrite cases.
- `hammer_ip_resolve_data()` resolves data from either memory, direct-write-backed reserved media, or on-disk B-tree data.
- Backend deletion helpers delete ranges, auxiliary clean records, individual records, and generic records with restart handling for `EDEADLK`.
- `hammer_create_at_cursor()` writes generic records directly to media for mirroring/snapshot/config paths, verifying CRC for user mirror data or generating CRC for system data.
- `hammer_delete_at_cursor()` adjusts delete TIDs, optionally destroys B-tree elements/data, updates inode counts and `vol0_next_tid`, and propagates mirror TID changes.
- Directory-empty checking scans merged records; mirror localization fixes directory entry payload localization and recalculates CRC.

## Dependencies
Depends heavily on HAMMER cursor, B-tree, inode, flusher, blockmap allocation/reservation, CRC, direct I/O wait, volume accounting, and transaction/sync-lock APIs.

## Behavior/Risks
This file encodes core consistency rules between frontend-visible pending records and backend media state. It contains explicit unimplemented edge cases for unaligned range deletion and panics on left/right truncation edge cases. Correctness depends on cursor flags, record generation reseeks, direct-I/O waits before commit/destruction, and avoiding duplicate visibility between memory records and B-tree records.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_object.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ondisk.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ondisk.c

## Purpose
Provides the residency and access layer for HAMMER on-disk structures: volumes, translated filesystem buffers, B-tree nodes, allocation helpers, and filesystem sync queuing.

## Key Elements
- Maintains RB trees for installed volumes, cached buffers, and cached B-tree nodes.
- `hammer_install_volume()` opens a device, validates or formats the volume header, checks FSID/volume numbering, inserts the volume, and records the root volume.
- Provides volume reference/load/release/unload paths around embedded `hammer_io`.
- `hammer_get_buffer()` resolves zone offsets through blockmap or undo mappings, handles read-only raw-zone aliases, creates cached `hammer_buffer` structures, and loads/new-zeros backing buffers.
- `hammer_sync_buffers()` flushes dirty/running HAMMER buffers that could alias direct frontend reads.
- `hammer_del_buffers()` destroys or invalidates buffers over a range after block reuse or direct writes.
- Exposes `hammer_bread()`, `hammer_bread_ext()`, `hammer_bnew()`, and `hammer_bnew_ext()` for offset-based buffer access.
- `hammer_get_node()` and related node functions cache B-tree nodes separately from buffers, validate node CRCs, support passive node caches, and flush node references when buffers disappear.
- Allocation helpers create B-tree nodes and allocate data in metadata, small-data, or large-data zones according to record type and size.
- Sync helpers scan vnodes, call `VOP_FSYNC`, and trigger async or synchronous flusher passes.

## Dependencies
Uses DragonFlyBSD namei/vnode/buffer APIs, HAMMER I/O primitives, blockmap/undo translation, CRC validation, volume numbering, flusher APIs, vnode sync scanning, and B-tree node/buffer data structures from `hammer.h`.

## Behavior/Risks
The layer relies on 0-to-1 reference transitions to load on-disk state and on final release to hand buffers back to the I/O subsystem. Read-only mounts may see zone aliases from recovery and handle them specially. CRC-bad B-tree nodes return `EIO` or `EDOM` depending on transaction flags. Unmount paths deliberately avoid flushing dirty buffers that should already have been handled by the flusher.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ondisk.c -->