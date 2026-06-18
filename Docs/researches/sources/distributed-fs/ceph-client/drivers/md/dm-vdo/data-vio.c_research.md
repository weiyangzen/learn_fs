# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.c

## Purpose

`data-vio.c` implements the lifecycle of user data I/O requests in VDO. It manages a bounded pool of `data_vio` objects, turns incoming bios into block-sized logical operations, serializes operations by logical block, performs reads, partial write read-modify-write, discard splitting, allocation, dedupe, compression, physical writes, recovery-journal updates, reference-count changes, block-map updates, acknowledgement, cleanup, and pool recycling.

## Important APIs, Types, And Functions

- Pool API: `make_data_vio_pool`, `free_data_vio_pool`, `vdo_launch_bio`, `drain_data_vio_pool`, `resume_data_vio_pool`, `dump_data_vio_pool`, and active/max request getters.
- Compression status API: `get_data_vio_compression_status`, `advance_data_vio_compression_stage`, and `cancel_data_vio_compression`.
- Cleanup/error API: `complete_data_vio`, `handle_data_vio_error`, `get_data_vio_operation_name`, and cleanup stages.
- Allocation/write API: `data_vio_allocate_data_block`, `release_data_vio_allocation_lock`, `update_metadata_for_data_vio_write`, `write_data_vio`, `launch_compress_data_vio`, and `continue_data_vio_with_block_map_slot`.
- Read API: `read_block`, `complete_read`, `complete_zero_read`, `modify_for_partial_write`, and `uncompress_data_vio`.
- Metadata update flow: `journal_remapping`, `increment_reference_count`, `decrement_reference_count`, and `update_block_map`.

## Control Flow

`vdo_launch_bio` admits a bio into the pool. It may block the submitting thread if no data VIO is available or if discard permits are exhausted. Once assigned, `launch_bio` classifies the request as read, write, discard, partial, zero, and/or FUA, copies full-block write data into the VIO buffer, computes the LBN, and enqueues `attempt_logical_block_lock` on the logical-zone thread.

The logical lock path serializes operations on the same LBN through `logical_zone->lbn_operations`. Reads behind a writing lock holder can be served from the lock holder after allocation succeeds. Otherwise waiters queue on the lock holder, and compression may be cancelled to prevent indefinite packer blocking.

For reads, `continue_data_vio_with_block_map_slot` calls `vdo_get_mapped_block`, then `read_block` reads the mapped PBN, reads the compressed block if needed, or synthesizes zeros for unmapped/zero blocks. Partial reads and compressed reads copy data back to the user bio on a CPU queue. Partial writes first read the old block, modify the requested range, then return to the write path.

For writes, the code acquires a flush generation lock, allocates a new physical block unless the operation is a full zero write or full discard, and may acknowledge non-FUA writes after allocation and before dedupe/compression/physical write. The dedupe path hashes data and acquires a hash lock. Compression uses LZ4 on the CPU queue and may attempt packer insertion; if not compressed or packed, `write_data_vio` writes the full block to the allocated PBN.

After the new data location is known, `update_metadata_for_data_vio_write` reads the old mapping, writes a recovery-journal remapping entry, updates reference counts for old and new PBNs, and rendezvous in `update_block_map`. Once both reference operations complete, `vdo_put_mapped_block` updates the block map. Cleanup then releases hash locks, allocation locks, recovery locks, logical locks, and flush generation locks before either launching the next discard block or returning the VIO to the pool.

Pool release processing is batched. Completed VIOs go through a funnel queue, `process_release_callback` acknowledges any still-unacknowledged bio, transfers discard permits fairly, assigns returned VIOs to oldest waiting reads/writes or permitted discards, wakes blocked submitters, and reschedules if the funnel still has entries.

## State And Persistence Behavior

The durable ordering is recovery journal entry first, reference-count updates, and block-map update. `data_vio->recovery_sequence_number` carries the journal entry lock until `vdo_update_block_map_page` transfers it to the dirty block-map page. Reference updaters describe increment/decrement journal operations for the slab depot. Flush generation locks prevent flush completion from racing ahead of acknowledged writes.

In-memory state includes the pool's limiters, wait queues, funnel queue, per-VIO logical lock, tree lock, mapped/new/duplicate PBNs, allocation lock, hash lock, compression state, recovery journal point, user bio pointer, discard progress, and async operation name. `allocation_succeeded` is read across threads with `READ_ONCE` because readers waiting behind a write may copy data from the lock holder.

Acknowledgement can happen before all metadata is durable for non-FUA writes after allocation succeeds; FUA and multi-block discard constraints delay acknowledgement. Fatal errors often enter read-only mode, especially after user bio acknowledgement or when `VDO_READ_ONLY` is encountered.

## Dependencies And Integration Points

The file integrates with Linux bios and block status conversion, VDO work queues/completions, logical zones, physical zones and PBN locks, slab depot reference counts, block map lookup/update, recovery journal, dedupe hash zones, packer/compression, MurmurHash3, LZ4, admin state, funnel queues, stats, and dump/logging facilities.

## Risks And Edge Cases

- Pool admission intentionally blocks submitter threads. Waiter wakeups and limiter counters must remain balanced or I/O can hang.
- Discards can span many blocks and reuse the same VIO; cleanup must correctly relaunch the next LBN and preserve remaining discard state.
- Early acknowledgement means post-ack fatal metadata errors must transition VDO read-only because the user cannot be failed anymore.
- Reads served from an allocating write lock holder require `allocation_succeeded` ordering and must not expose data before a real allocation exists.
- Compression cancellation and packer blocking are concurrency-sensitive; lock waiters must not wait forever behind a VIO stuck in the packer.
- The reference-count rendezvous uses two completions and `first_reference_operation_complete`; a missed callback would block block-map updates.
- Partial writes depend on correct zero-fill, old-block read, and bio copy offsets.
- `bio->bi_private` is reused to store `jiffies` while waiting for permits, then later stores VIO context for submitted bios.

## Test Signals

Tests should cover pool exhaustion and wakeup fairness, discard permit limiting, drain/resume with waiters, full reads, zero reads, compressed reads, partial reads, partial writes, full zero writes, full and multi-block discards, FUA writes, no-space allocation fallback to dedupe, compression disabled/cancelled/packer paths, hash-lock contention, logical-lock transfer, post-ack metadata failure read-only transition, reference-count update rendezvous, and block-map update failure. Runtime signals include async operation names in error logs, `bios_acknowledged` stats, pool max-busy stats, VIO error stats, read-only notifier state, and dump output for busy VIOs.
