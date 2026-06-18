# File Research: sources/block-storage/lvm2/lib/metadata/metadata.c

## Purpose

`metadata.c` is the central in-core VG/PV/LV metadata orchestration file for LVM2. It creates, reads, validates, writes, commits, reverts, and tears down volume-group metadata; manages PV membership and metadata areas; performs access-control checks for system IDs, clustered/shared locking, exported VGs, and missing devices; and provides lookup/helper APIs used by LV manipulation, pool, mirror, activation, and command code.

## Key Responsibilities

- PV setup and VG membership: computes default PV metadata size, PE alignment, alignment offsets, adds/removes PVs from VGs, moves PVs between VGs, initializes new PVs, writes PV labels, and handles orphan PV reads.
- VG lifecycle: validates VG create/rename parameters, creates VGs with format instances, checks VG removal, removes VG metadata areas, archives metadata before writes, and updates backups/notifications after commits/removal.
- Metadata-area management: copies, indexes, ignores/unignores, moves, writes, precommits, commits, reverts, repairs, and removes `metadata_area` instances attached to a `format_instance`.
- Read path: `vg_read()` locks the VG, resolves duplicate names/VGIDs, optionally rescans labels, imports the newest valid metadata copy from MDAs, reconciles lvmcache with full VG metadata, sets PV device pointers, detects missing/wrong/outdated PVs, validates segment graphs, and creates a committed copy for update operations.
- Write path: `vg_write()` handles historical LV cleanup, optional validation, partial/duplicate/unknown-segment rejection, MDA copy balancing, outdated PV wiping, archive creation, PV header rewrites, MDA writes, precommit, and lockd update. `vg_commit()` commits MDAs and advances the cached committed VG; `vg_revert()` rolls back precommitted metadata.
- Validation and graph traversal: verifies PV/LV list consistency, duplicate names/UUIDs, segment integrity, pvmove shape, historical LV chains, tags, shared-lock metadata, pool metadata spare uniqueness, and LV/PV reference membership.
- Access policy: enforces `system_id`, shared lock type/lvmlockd state, clustered/exported flags, write permissions, missing PV behavior, persistent reservation requirements, and legacy `LVM_WRITE_LOCKED` encoding.

## Main Data And APIs

- `struct volume_group`, `struct physical_volume`, `struct logical_volume`, `struct lv_segment`, `struct pv_list`, `struct lv_list`, and `struct metadata_area` are the main metadata graph objects.
- `struct format_instance` is the per-VG metadata-location object, holding active/ignored MDA lists plus optional MDA index state.
- Important public entry points include `vg_create()`, `vg_read()`, `vg_read_for_update()`, `vg_write()`, `vg_commit()`, `vg_revert()`, `vg_validate()`, `pv_create()`, `pv_write()`, `add_pv_to_vg()`, `vg_extend_each_pv()`, `vg_split_mdas()`, `vg_remove_direct()`, `find_lv()`, `find_pv*()`, `find_seg_by_le()`, `lv_calculate_readahead()`, `vg_mark_partial_lvs()`, `pv_change_metadataignore()`, `scan_text_mismatch()`, and MDA/FID helpers.
- Temporary radix trees in validation check uniqueness and membership for PV IDs, LV names, LV IDs, historical LV names/IDs, and lock args. Read-only committed VGs may cache `lv_uuids` for activation lookups.
- `POSTORDER_FLAG` and `POSTORDER_OPEN_FLAG` are temporary LV status bits used while walking LV dependency graphs.

## Control Flow Notes

- `_vg_read()` first decides whether cached scan results are stale by checking lvmcache mismatches and text MDA offset/checksum changes. It builds a format instance from lvmcache-discovered MDAs, reads each candidate MDA, chooses the highest seqno metadata copy, warns about inconsistent old copies, then updates lvmcache using the chosen VG.
- `vg_read()` wraps `_vg_read()` with locking, duplicate-name handling, missing-PV detection, partial-LV marking, segment validation, device-size checks, device-use mismatch checks, access policy checks, and optional committed-copy import for later rollback/activation decisions.
- `vg_write()` increments the VG seqno only after validation and MDA-copy adjustment. It writes any needed PV headers first, then writes every usable MDA, reverts already-written MDAs on failure, precommits successful writes, and leaves the caller responsible for `vg_commit()` or `vg_revert()`.
- `_vg_commit_mdas()` temporarily moves ignored MDAs so ignored copies commit before active copies, reducing the chance that interruption leaves the ignored copy as the newest active-looking metadata.
- LV dependency walks visit snapshot origin/COW, external LVs, mirror logs, pools, metadata LVs, writecache/integrity metadata, AREA_LV segment areas, and origin snapshot COWs.

## Dependencies

This file depends heavily on lvmcache label-scan state, format handlers, text metadata import/export, device-cache and block-size helpers, allocation/PV segment helpers, activation state, archiver/backup code, lvmlockd, persistent reservation checks, configuration lookup, radix trees, and device-mapper cache state. Several public functions are consumed by `lv_manip.c`, `mirror.c`, `pool_manip.c`, thin/cache/VDO/integrity code, and command front ends.

## Risks And Edge Cases

- PV label writes and VG metadata writes are not atomic together; comments explicitly note limited revert support around non-orphan PV writes.
- `pv_create()` has a FIXME for detaching from the orphan VG in the error path, so partial in-memory state can persist after failure.
- Metadata read chooses newest seqno among MDAs but only warns about older inconsistent copies; repair is separate.
- Some lookup indexes (`vg->lv_names`, `vg->pv_names`, `vg->lv_uuids`) are valid only in specific read-only/read contexts and are not universally maintained after mutations.
- Missing PV handling distinguishes absent devices from reappeared devices with `MISSING_PV`; allocated reappeared PVs remain treated as missing until explicit repair/reduce actions.
- Shared-lock validation intentionally skips some missing `lock_args` errors due known transient states during snapshot and thin-pool conversion.
- `vg_write()` may proceed with failed MDAs when the command handles missing PVs, so later commit health depends on at least one good MDA.
- Outdated PV wiping mutates headers/MDAs based on lvmcache's outdated-device lists and is only run when commanded.

## Summary

`metadata.c` is the transaction and consistency core for LVM2 metadata. It coordinates cached scan data, on-disk metadata copies, in-memory VG graphs, PV headers, locks, access policy, validation, and repair-adjacent cleanup so higher-level LV operations can mutate metadata through a common read/write/commit model.
