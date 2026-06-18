# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.c

## Purpose
Provides low-level block-device I/O helpers for the indexer. It wraps dm-bufio clients in an `io_factory`, plus bounded sequential buffered readers and writers for contiguous index regions.

## Important APIs, Types, And Functions
Private types are `io_factory`, `buffered_reader`, and `buffered_writer`. Public functions include `uds_make_io_factory()`, `uds_replace_storage()`, `uds_put_io_factory()`, `uds_get_writable_size()`, `uds_make_bufio()`, `uds_make_buffered_reader()`, `uds_free_buffered_reader()`, `uds_read_from_buffered_reader()`, `uds_verify_buffered_data()`, `uds_make_buffered_writer()`, `uds_free_buffered_writer()`, `uds_write_to_buffered_writer()`, and `uds_flush_buffered_writer()`.

## Control Flow
The factory stores a block device and reference count. Readers create a dm-bufio client with a sector offset, prefetch up to four blocks, and sequentially copy bytes from 4 KiB buffers, refusing reads beyond their block limit. Writers create new dm-bufio buffers, append data or zero-fill when data is NULL, mark full buffers dirty, release them, and write dirty buffers when freed.

## State And Persistence
I/O state is bounded by `(offset, block_count)` region windows. Writers zero-fill unwritten bytes in the current block before marking it dirty, which keeps serialized regions deterministic and avoids leaving stale data in partial blocks. `uds_replace_storage()` swaps the backing block device pointer for future clients.

## Dependencies And Integration Points
Depends on Linux block-device and dm-bufio APIs, atomic reference counting, allocation, logging, and numeric constants. It is used by layout, volume, page-map, open-chapter, and volume-index persistence code.

## Risks
The factory does not own an opened reference to the block device in this file; callers must manage block-device lifetime. Existing reader/writer clients keep their dm-bufio clients, so storage replacement should happen only when no old clients are active. `uds_verify_buffered_data()` restores reader position on mismatch and depends on valid `end/start` state; misuse before any positioning could be fragile.

## Test Signals
Tests should cover boundary reads/writes, out-of-range errors, partial block zero-fill, verify success and failure with position restoration, dirty-buffer sync failures, prefetch behavior across sequential blocks, and storage replacement followed by new reader/writer creation.
