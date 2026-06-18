# File Research: sources/block-storage/linux-dm/drivers/md/dm-clone-target.c

## Purpose
Implements the Device Mapper `clone` target, which presents a destination device as a gradually hydrated clone of a read-only source device. Reads from unhydrated regions go to the source; writes trigger immediate hydration or overwrite optimization; background work eventually hydrates all regions.

## Main Interfaces
- Target lifecycle: `clone_ctr()`, `clone_dtr()`, `clone_postsuspend()`, `clone_resume()`.
- I/O path: `clone_map()`, `clone_endio()`, `issue_bio()`, `process_discard_bio()`.
- Hydration: `hydrate_bio_region()`, `hydration_copy()`, `hydration_overwrite()`, `hydration_complete()`, `do_hydration()`.
- Metadata commit: `commit_metadata()`, `process_deferred_flush_bios()`, `process_deferred_discards()`.
- Reporting/control: `clone_status()`, `clone_message()`, `clone_io_hints()`, `clone_iterate_devices()`.

## Control Flow
`clone_map()` increments in-flight I/O, handles flushes first, offsets data bios to target-relative sectors, and special-cases discards. Hydrated-region I/O is sent to the destination. Reads from unhydrated regions are sent to the source. Writes to unhydrated regions are remapped to destination and attach to a region hydration descriptor.

Per-region hydration descriptors are stored in a hash table. If a region is already hydrating, additional bios are deferred on that descriptor. If a full-region write arrives, it can overwrite the destination directly without copying from source. Otherwise kcopyd copies the region from source to destination. Completion updates metadata, completes overwrite bios, and issues deferred bios.

Background hydration scans for unhydrated regions, avoids starting while foreground I/O is in flight, respects `hydration_threshold`, batches adjacent regions up to `hydration_batch_size`, and resumes from `hydration_offset`.

## State And Synchronization
`struct clone` owns metadata, source/destination devices, region geometry, commit mutex, hydration hash table, hydration mempool, deferred bio lists, workqueue, delayed waker, kcopyd client, mode, flags, and in-flight counters. Hash buckets each have IRQ-safe spinlocks. `commit_lock` serializes metadata commit and failure handling. `hydrations_in_flight` and `hydration_stopped` coordinate suspend with active hydration.

## Integration Points
Uses `dm-clone-metadata` for region state and commit semantics, `dm-kcopyd` for source-to-destination copies, Device Mapper target hooks for mapping/status/messages/queue limits, and block-layer flush/discard APIs. Queue-limit code inherits discard limits from the destination device when passdown is enabled.

## Notable Behaviors
- Features include `no_hydration` and `no_discard_passdown`.
- Core tunables include `hydration_threshold` and `hydration_batch_size`, adjustable by messages.
- Discards over unhydrated regions mark those regions hydrated without copying, then optionally pass discard to the destination.
- Metadata commits perform `pre_commit`, flush the destination block device, then commit metadata.
- FUA overwrite completions and PREFLUSH bios are deferred until after metadata commit.
- Suspend cancels the periodic waker, stops new background hydration, waits for active hydrations, flushes the workqueue, and commits metadata.

## Risks And Review Focus
- Suspend/hydration ordering depends on memory barriers around `hydrations_in_flight` and `DM_CLONE_HYDRATION_SUSPENDED`.
- Metadata failure handling aborts, switches to read-only, and reloads the bitmap; all later I/O paths must respect mode changes.
- Hash-table insertion/removal must avoid duplicate hydration descriptors for the same region.
- Deferred flush, FUA completion, discard, and normal bio lists have different completion/submit semantics and must not be merged incorrectly.
