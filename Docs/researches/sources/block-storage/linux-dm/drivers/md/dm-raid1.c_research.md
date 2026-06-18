# File Research: sources/block-storage/linux-dm/drivers/md/dm-raid1.c

## Purpose

`dm-raid1.c` implements the older Device Mapper `mirror` target. It mirrors writes to multiple legs, chooses readable mirrors for reads, uses a dirty-region log and region hash for synchronization state, performs resync through kcopyd, and optionally exposes leg/log errors to userspace for repair.

## Core Model

`struct mirror_set` owns mirror legs, queued reads/writes/failures/held bios, a `dm_region_hash`, kcopyd and dm-io clients, sync state, log and leg failure flags, suspend state, a default mirror index, a `kmirrord` workqueue, delayed wake timer, and table-event work. Each `struct mirror` stores its `dm_dev`, offset, error count, and error-type bitmap.

Features are `handle_errors` and `keep_log`; `keep_log` requires `handle_errors`. Without handled errors, the target may ignore some leg errors to preserve legacy behavior. With handled errors, failures trigger table events and failed writes may be held for userspace intervention.

## I/O Flow

Writes are always queued to `kmirrord`. The worker classifies writes by region state: clean/dirty regions are written to all mirrors, nosync regions go only to the default mirror, recovering regions are delayed, and remotely recovering regions are requeued with delayed wake. Before synchronized writes, pending counts are incremented and the dirty log is flushed.

Reads are direct-mapped when the region is in sync and an intact mirror is available. If the region is not known in sync, reads are queued to the worker unless they are readahead, which is killed. Failed reads are retried on an alternate mirror if possible after restoring the original bio details.

Flushes are issued to all mirrors via dm-io. Discards are issued to all mirrors but discard failures return `BLK_STS_NOTSUPP` without degrading the array.

## Recovery

Recovery copies a region from the default mirror to all other mirrors using kcopyd. `do_recovery()` asks the region hash to quiesce regions, starts copy work for quiesced regions, and marks the mirror set in sync once the dirty log sync count equals the number of regions.

`recovery_complete()` marks default read errors or destination write errors against the relevant mirrors, then ends the region-hash recovery with success or failure.

## Constructor And Lifecycle

Constructor syntax is:

`<log_type> <#log_params> <log_params...> <#mirrors> [<dev> <offset>]... [<#features> <features...>]`

It creates a dirty log, allocates the mirror set and region hash, opens mirror devices, sets max I/O length to the region size, advertises flush/discard support, allocates per-bio private data, starts the `kmirrord` workqueue, parses features, creates the kcopyd client, and wakes recovery.

Presuspend sets the suspend flag, drains held bios, stops recovery, waits for in-flight recovery, calls log presuspend, and flushes the worker. Resume clears suspend, resumes the log, and restarts recovery. Destruction drains timer/work, destroys kcopyd/workqueue, releases devices, destroys the region hash, and frees context.

## Invariants And Risks

- Dirty-log flush failure is sticky in `ms->log_failure` until userspace reload/intervention.
- Pending region counts are decremented in `mirror_end_io()`, not in the write callback.
- If the primary fails while out of sync and `keep_log` is disabled, reads may continue to target the same failing primary to avoid serving stale data.
- Held bios during handled-error paths are requeued on noflush suspend and failed otherwise.
- Read retry depends on successful `dm_bio_record()` before remapping.
- `kmirrord` is the serialization point for region-state updates, recovery scheduling, read fallback, writes, and failure handling.

## Test Focus

Test constructor parsing, feature validation, log creation failures, mirror device offsets, read balancing only for in-sync regions, read retry after leg failure, write classification by region state, log flush failure behavior, handled versus unhandled errors, `keep_log`, all-legs-dead behavior, discard failure semantics, recovery completion errors, suspend with held bios, noflush suspend requeue, status health characters, and table/IMA output.
