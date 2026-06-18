# File Research: sources/block-storage/linux-dm/drivers/md/dm-snap-persistent.c

## Purpose

`dm-snap-persistent.c` implements the persistent snapshot exception store. It records origin-to-COW chunk mappings on the COW device so snapshots survive reboot, supports committing new exceptions, reading metadata during activation, invalidating snapshots, merging committed exceptions back, and reporting COW usage.

## On-Disk Format

Chunk 0 contains `disk_header` with magic `SNAP_MAGIC`, validity flag, disk version, and chunk size. Metadata areas follow after the header. Each metadata area is one chunk containing `disk_exception` entries, and metadata chunks are interleaved with exception data chunks. A `new_chunk` value of zero terminates the exception list because chunk zero is reserved for the header.

All on-disk values are little-endian. Disk version is fixed at `SNAPSHOT_DISK_VERSION`; incompatible versions are rejected rather than migrated.

## Runtime State

`struct pstore` stores the exception store, version/valid flags, exceptions per area, current metadata area buffer, zero buffer, separate header buffer, current area index, next free chunk, committed-entry index, pending exception count, commit callbacks, dm-io client, and metadata workqueue.

Metadata I/O uses `dm_io`. Header/metadata chunk I/O can be routed through `ksnaphd` to avoid recursive `submit_bio_noacct()` when synchronous metadata I/O is initiated from sensitive paths. Existing metadata is read with dm-bufio and prefetches up to `DM_PREFETCH_CHUNKS`.

## Activation And Allocation

`persistent_read_metadata()` reads or initializes the header, adjusts chunk size if on-disk metadata overrides the table value, allocates callback storage sized to one metadata area, writes a new header and zeroes area 0 for fresh snapshots, rejects unsupported disk versions, returns invalid-snapshot state if `valid` is false, and otherwise reads all exception areas into the snapshot core via callback.

`persistent_prepare_exception()` checks COW space, assigns `e->new_chunk` from `next_free`, advances over metadata chunks using `skip_metadata()`, and increments pending exception count.

## Commit And Merge

`persistent_commit_exception()` writes the exception into the in-memory current area, records the completion callback, and waits until either all pending exceptions drain or the metadata area fills. If the area fills it zeroes the next area first, then writes the current metadata area with preflush/FUA/sync. On any metadata failure or invalid exception, `ps->valid` becomes false and callbacks are invoked with failure. Full areas advance to the next zeroed in-memory area.

Merge support works backwards from the latest committed exception. `persistent_prepare_merge()` returns a run of consecutive old/new chunk mappings from the current area, loading the previous area if needed. `persistent_commit_merge()` clears merged entries, writes the metadata area with preflush/FUA, decrements `current_committed`, and updates `next_free` for usage reporting.

## Constructor And Status

The constructor allocates `pstore`, initializes defaults, creates the `ksnaphd` workqueue, and accepts option `O` for userspace overflow support. The type is registered as both `persistent` and compatibility alias `P`. Table status emits `P` or `PO` plus chunk size.

## Invariants And Risks

- A valid snapshot depends on successfully writing metadata areas with ordering flags; failures mark the snapshot invalid.
- Chunk zero is never an exception data chunk and doubles as the exception-list terminator.
- `next_free` skips metadata chunks and is exact for allocation before merge; after merge it is mainly a conservative usage-reporting value.
- Callback batching assumes commit manipulation is not concurrent.
- Header writes use a separate buffer because invalidation can occur concurrently with metadata-area writes.
- Existing COW metadata chunk size can override the table-supplied chunk size, requiring buffer reallocation.

## Test Focus

Test fresh snapshot initialization, invalid magic, invalid version, on-disk chunk-size override, chunk-size validation, exception-list termination, dm-bufio prefetch bounds, COW full detection, metadata chunk skipping, out-of-order pending commits, metadata write failure invalidation, zero-next-area failure, callback success/failure batching, merge run detection, merge writes, overflow option parsing, drop-snapshot invalidation, and status output.
