# sources/storage-engines/rocksdb/db/c.cc lines 1-7443

## Scope

This chunk is the first 7,443 lines of RocksDB's C API implementation. It begins at the file header and `#include "rocksdb/c.h"`, enters `extern "C"`, defines most opaque C handle structs, implements callback adapter classes, and exposes a large surface of DB, backup, checkpoint, column-family, read/write, iterator, write-batch, options, cache, environment, SST writer, ingestion, live-file, and metadata wrappers. The chunk ends inside the declaration of `rocksdb_sst_file_metadata_destroy`; the remaining SST metadata accessors and later APIs are outside this chunk.

## Purpose

The code translates the C ABI declared by `rocksdb/c.h` into calls on RocksDB's C++ API. It hides C++ objects behind small C structs containing raw pointers or value members, converts C buffers into `Slice`/`std::string`/vectors, converts `Status` to heap-allocated C error strings, and maps user-supplied C callbacks into C++ virtual interfaces such as `Comparator`, `CompactionFilter`, `MergeOperator`, `SliceTransform`, `Logger`, `EventListener`, and `CompactionService`.

## Important Types And Ownership

- `rocksdb_t`, `rocksdb_backup_engine_t`, `rocksdb_iterator_t`, `rocksdb_wal_iterator_t`, `rocksdb_sstfilewriter_t`, transaction-related wrappers, and checkpoint wrappers generally own raw C++ pointers and destroy them in matching `*_destroy`/`*_close` functions.
- Option wrappers such as `rocksdb_options_t`, `rocksdb_readoptions_t`, `rocksdb_writeoptions_t`, `rocksdb_compactoptions_t`, `rocksdb_block_based_table_options_t`, `rocksdb_cuckoo_table_options_t`, `rocksdb_flushoptions_t`, and compaction-option wrappers hold C++ option values by value.
- Shared-resource wrappers (`rocksdb_logger_t`, checksum/partitioner/table collector factories, cache, write buffer manager, SST file manager, rate limiter, memory allocator) hold `std::shared_ptr` so they can be installed into options without requiring immediate destruction of the underlying C++ object.
- `rocksdb_column_family_handle_t` tracks an `immortal` flag. The default column family handle returned by `rocksdb_get_default_column_family_handle` points into the DB and is not deleted; other handles are deleted by `rocksdb_column_family_handle_destroy`.
- `rocksdb_readoptions_t` stores `Slice` members for upper/lower iterator bounds, timestamp, and iterator start timestamp. These are backing storage for pointers inside `ReadOptions`; callers must keep the source buffers valid according to RocksDB expectations because the `Slice` only references external memory.
- Metadata wrappers at the end of the chunk store pointers into parent metadata containers: `rocksdb_level_metadata_t` points into `rocksdb_column_family_metadata_t::rep.levels`, and `rocksdb_sst_file_metadata_t` points into a level's `files`. Destroying the parent before children leaves dangling references.

## Callback Adapter APIs

- `rocksdb_compactionfilter_t` subclasses `CompactionFilter`; `Filter` calls a C callback and may assign a replacement value. Its destructor invokes the user destructor. It also exposes `IgnoreSnapshots`.
- `rocksdb_compactionfilterfactory_t` subclasses `CompactionFilterFactory` and creates per-compaction `rocksdb_compactionfilter_t` instances from a C factory callback.
- `rocksdb_comparator_t` subclasses `Comparator`, supports normal comparison plus optional timestamp comparison and timestamp-stripped comparison. Key shortening methods are no-ops in the C binding.
- `rocksdb_filterpolicy_t` is a base C-visible filter wrapper. Built-in bloom and ribbon constructors create local C++ wrapper subclasses that delegate to `NewBloomFilterPolicy` or `NewRibbonFilterPolicy`.
- `rocksdb_mergeoperator_t` bridges C full and partial merge callbacks. It builds operand pointer/length arrays, assigns the returned value into RocksDB output, then frees it through either the provided `delete_value_` callback or `free`.
- `rocksdb_slicetransform_t` bridges prefix transform callbacks. Built-in fixed-prefix and noop transforms are wrapped by `SliceTransformWrapper`.
- `rocksdb_callback_logger_t` subclasses `Logger`, formats `Logv` output into a stack buffer or heap buffer, and calls the C logging callback with level and bytes.
- `rocksdb_eventlistener_t` subclasses `EventListener` and forwards flush, compaction, subcompaction, external ingestion, background error, stall condition, and memtable sealed events. It creates short-lived stack `rocksdb_t` wrappers around `DB*` for event callbacks and reinterprets RocksDB event-info structs as C wrapper types.
- `rocksdb_compactionservice_t` subclasses `CompactionService`, forwards scheduling/wait/cancel/installation events to C callbacks, validates schedule responses, and installs itself into `Options::compaction_service` through a `shared_ptr`.

## Main DB Control Flow

- Opening APIs allocate C++ DB objects with `DB::Open`, `DBWithTTL::Open`, `DB::OpenForReadOnly`, and `DB::OpenAsSecondary`, then release the resulting `unique_ptr` into `rocksdb_t`.
- Column-family open variants build `std::vector<ColumnFamilyDescriptor>` from C arrays, return one `rocksdb_column_family_handle_t` per returned C++ handle, and wrap the DB pointer. TTL opens also build a `std::vector<int32_t>` of TTLs.
- `rocksdb_open_and_trim_history` wraps `DB::OpenAndTrimHistory` and returns handles for every opened column family.
- `rocksdb_close` deletes both the C++ `DB` and the C wrapper.
- `rocksdb_try_catch_up_with_primary` exposes secondary catch-up via `DB::TryCatchUpWithPrimary`.
- `rocksdb_destroy_db` and `rocksdb_repair_db` forward to `DestroyDB` and `RepairDB`.

## Read/Write APIs

- Point writes (`rocksdb_put`, `rocksdb_put_cf`, `rocksdb_put_with_ts`, `rocksdb_delete*`, `rocksdb_singledelete*`, `rocksdb_merge*`) wrap key/value/timestamp buffers in `Slice` and call the matching `DB` method.
- `rocksdb_write` writes a `WriteBatch`; `rocksdb_write_writebatch_wi` writes the underlying `WriteBatch` from a `WriteBatchWithIndex`.
- Gets use either `PinnableSlice` or `std::string`, set output lengths on success, return `nullptr` on not found without setting an error, and use `CopyString` to allocate returned data with `malloc`.
- Timestamped get and multiget variants return value and timestamp buffers separately.
- `rocksdb_multi_get*` builds arrays/vectors of `Slice`, column-family handles, `PinnableSlice`/`std::string`, and `Status`. Per-key errors are returned as `strdup` strings except not-found, which is reported as null value and null error.
- Batched multiget variants return `rocksdb_pinnableslice_t` objects to avoid copying values; the slice-based variant reinterprets `rocksdb_slice_t` as `Slice`, relying on identical memory layout.
- `rocksdb_key_may_exist*` optionally returns copied value data only when RocksDB reports the value was actually found.

## Iterators, WAL, Snapshots, And Properties

- Iterator wrappers expose construction for default and column-family iterators, multi-CF iterator creation, seek/next/prev, validity, status, refresh, and direct key/value/timestamp access. Direct accessors return pointers into the iterator's current state; caller must not retain them after iterator movement/destruction.
- `rocksdb_iter_key_slice`, `rocksdb_iter_value_slice`, and `rocksdb_iter_timestamp_slice` return a C `rocksdb_slice_t` view for lower overhead.
- WAL iteration uses `DB::GetUpdatesSince`, then exposes valid/next/status/destroy and `rocksdb_wal_iter_get_batch`, which moves the WAL batch into a newly created `rocksdb_writebatch_t`.
- Snapshot wrappers call `GetSnapshot`, `ReleaseSnapshot`, and `GetSequenceNumber`; snapshots are owned by the DB until released.
- Property APIs expose string and integer DB/column-family properties using `GetProperty` and `GetIntProperty`.
- Size and maintenance APIs include approximate sizes, approximate sizes with flags, live-file metadata, manual compaction, suggested compaction, flush, WAL flush, file deletion disable/enable, and delete-files-in-range.

## WriteBatch And WriteBatchWithIndex

- `rocksdb_writebatch_create*` constructs standard batches, including serialized-data and parameterized constructors.
- Mutation methods cover put, merge, delete, single delete, delete range, timestamped variants, column-family variants, and vectorized `SliceParts` variants.
- Iteration uses local `WriteBatch::Handler` subclasses (`H` and `HCF`) to call C callbacks for put/delete/merge and optional log data.
- Save-point functions expose `SetSavePoint`, `RollbackToSavePoint`, and `PopSavePoint`.
- Timestamp update functions call `WriteBatch::UpdateTimestamps` with a C callback that maps column-family id to timestamp size.
- `rocksdb_writebatch_wi_*` mirrors the mutation surface for `WriteBatchWithIndex`, adds indexed reads from batch or batch+DB, pinned reads, and iterators overlaying a base iterator. The overlay constructors delete the passed base iterator wrapper after transferring its `Iterator*` into the new iterator.

## Backup, Restore, Checkpoint, And External Files

- Backup engine wrappers open backup engines from DB options or explicit backup options, create backups, purge old backups, verify backups, restore latest/specific backups, expose backup info fields, stop backups, and close engines.
- Backup option setters/getters cover backup dir, environment, file sharing, sync, old-data destruction, WAL backup, rate limits/limiters, background operations, callback trigger interval, max backups to open, and checksum naming mode.
- Checkpoint wrappers create a checkpoint object, create a checkpoint directory, export a column family, and destroy the checkpoint.
- Export/import metadata appears in wrappers for checkpoint export and `rocksdb_create_column_family_with_import`; its ownership is represented by `rocksdb_export_import_files_metadata_t`, with destruction likely implemented outside this chunk.
- `SstFileWriter` wrappers create writers, open files, add/put/merge/delete/delete-range records, finish, get file size, and destroy.
- External file ingestion options expose move-files, snapshot consistency, global sequence number, blocking flush, ingest-behind, and bottommost-level checks; ingestion functions forward a C file-list array into a `std::vector<std::string>`.

## Options And Resource Configuration

- `rocksdb_options_t` creation, copy, destroy, preset optimizers, dynamic `SetOptions`, and `GetOptionsFromString` are exposed.
- Table-related configuration includes block-based table options, cuckoo table options, plain table factory, bloom/ribbon filter policies, block caches, metadata cache pinning tiers, checksum, block sizes, index/search types, filter caching, and block alignment.
- Core DB/CF options setters/getters cover create flags, paranoid checks, file opening, path vectors, env/loggers, write buffers/managers, SST file manager, max open files, WAL size/ttl/dir, file sizes, level sizing, compaction triggers, compression, bottommost compression options, prefix extractor, direct IO/mmap/fsync, stats periods, concurrency, background jobs, log retention, pending compaction limits, manifest size, table cache shards, memtable factory/options, identity/DBID/WAL tracking in manifest, merge limits, bloom locality, inplace update, compaction style/priority, universal/FIFO compaction, rate limiter, atomic/manual WAL flush, WAL compression, and compact-on-deletion collectors.
- Blob options in this chunk expose enabling blob files, min/blob file size, blob compression, garbage collection, read-triggered compaction threshold, compaction wakeup, blob compaction readahead, starting level, blob cache, and prepopulate mode.
- Statistics wrappers enable statistics, clamp/set/get stats level, stringify statistics, read ticker counts, and fill histogram data.
- `ReadOptions`, `WriteOptions`, `CompactRangeOptions`, and `FlushOptions` have create/destroy plus many direct setters/getters. Read options include checksum/cache/snapshot/bounds/read-tier/tailing/readahead/prefix/total-order/max-skippable/background-purge/range-deletion/deadline/io-timeout/async-io/multiget optimization/timestamp/iter-start-ts/auto-readahead. Write options include sync, WAL disable, missing CF ignore, no slowdown, low priority, and memtable insert hint. Compact options include bottommost compaction, exclusivity, level targeting, write stall permission, subcompactions, and full-history timestamp lower bound.

## Cache, Env, And Memory Utilities

- Cache wrappers create LRU and HyperClock caches, optionally with strict capacity or option structs; expose capacity, usage, pinned usage, table address count, occupancy count, disown-data, and capacity mutation.
- Memory allocator wrapper creates a jemalloc nodump allocator through `NewJemallocNodumpAllocator`.
- `WriteBufferManager` wrappers create managers with or without a cache, expose enabled/cost/memory metrics, buffer size mutation, and allow-stall mutation.
- `SstFileManager` wrappers create managers, set max space and compaction buffer, read space/deletion/trash metrics, and configure delete rate/trash ratio.
- Env wrappers create default and in-memory envs, control thread-pool sizes by priority, join threads, lower IO/CPU priority, create directories, and destroy non-default envs only.

## State And Persistence Behavior

- Persistent DB state is modified through writes, write batches, column-family create/drop/import, compaction, flush, WAL flush, file deletion, repair/destroy, external file ingestion, backup/restore, checkpoints, and SST writer output.
- Options objects are in-memory configuration until used to open a DB or installed into another option object. Some runtime options can be changed on an open DB through `rocksdb_set_options*`.
- Returned heap buffers use mixed allocation conventions: many data strings use `malloc` via `CopyString`, human-readable strings often use `strdup`, and C++ wrappers use `new`. Callers must use the corresponding C API free/destroy functions from the broader C binding.
- Several APIs return non-owning pointers into live C++ objects (`Iterator` key/value/timestamp slices, live-file strings, job-info strings, metadata child wrappers). Their lifetime is tied to the parent iterator/event info/livefiles/metadata object.
- Shared pointers transfer ownership for some callback-derived objects when installed in options (`merge_operator`, compaction filter factory, prefix extractor, event listener, compaction service). Destroying the original C wrapper after installing it can double-delete unless the API contract says ownership was transferred.

## Dependencies And Integration Points

- Primary dependencies are RocksDB C++ headers for DB core, options, env, listeners, backup/checkpoint utilities, transaction/write-batch utilities, memory/cache/rate-limit utilities, table factories, and statistics/perf context.
- The file is the implementation backing `rocksdb/c.h`, so ABI stability, symbol names, allocation conventions, and enum integer mappings are integration-critical for C, Go, Rust, Python, and other FFI consumers.
- It integrates with RocksDB's callback-based extension points by subclassing C++ abstract classes and forwarding to C function pointers.
- It integrates with persistence subsystems: WAL/log iteration, backup engine, checkpoint/export/import, SST file writer, external ingestion, live file metadata, and DB identity.
- It integrates with runtime observability through statistics, perf context, properties, event listeners, logger callbacks, compaction/flush/write-stall/memtable info accessors, and backup info.

## Risks And Edge Cases

- Many wrappers assume non-null input pointers and valid array lengths; only newer compaction-service/open-and-compact functions contain explicit argument checks.
- Callback destructor pointers are often called unconditionally in adapter destructors; null destructors can crash.
- `CopyString` calls `malloc(slice.size())` and then `memcpy`, which may return null for zero-length buffers depending on allocator behavior. Callers must rely on returned lengths rather than C-string termination; `CopyString` does not add a null terminator.
- Some string-returning APIs use `strdup` and are null-terminated, while binary-returning APIs use `malloc`; FFI bindings must not assume one convention.
- Reinterpret casts of RocksDB C++ event info or `rocksdb_slice_t` to wrapper/Slice types rely on exact layout assumptions.
- Metadata child wrappers and iterator slice returns are borrowed views; stale access after parent destruction or movement is unsafe.
- `rocksdb_slicetransform_t::Transform` returns a `Slice` pointing at a callback-returned `char*` without visible ownership/free logic in this chunk, so callback implementations must obey RocksDB expectations to avoid leaks or dangling pointers.
- `rocksdb_create_column_families_destroy` frees only the returned array, not the individual handles, so callers must destroy handles separately.
- `rocksdb_create_column_family_with_ttl` returns a handle even if `CreateColumnFamilyWithTtl` fails, unlike some other create paths that delete the handle on error.
- `rocksdb_compactionservice_t::Wait` casts callback status directly to `CompactionServiceJobStatus` without range validation, unlike scheduler response creation.
- Event listener callbacks are invoked without null checks for individual callback pointers; users must provide all callbacks or risk crashes when events fire.
- `rocksdb_level_metadata_t` and `rocksdb_sst_file_metadata_t` are allocated with `malloc`, not `new`, because they only store borrowed pointers. Destruction must use the matching free path; the chunk ends before the body of `rocksdb_sst_file_metadata_destroy`.

## Test Signals

- Existing C binding tests should exercise open/close, put/get/delete/merge, column families, multiget, iterators, snapshots, write batches, write-batch-with-index, options setters/getters, cache/env creation, backup/restore, checkpoint/export/import, SST writer, external ingestion, and metadata traversal.
- FFI tests should check binary keys/values with embedded null bytes, zero-length values, timestamped APIs, not-found behavior with null error pointers, per-key multiget errors, and consistent freeing of returned buffers.
- Callback tests should cover custom comparator, comparator-with-timestamp, merge operator, compaction filter/factory, prefix extractor, logger, event listener, and compaction service lifecycle/destructor behavior.
- Persistence tests should validate WAL iteration sequence numbers, flush/compaction effects, live-file and column-family metadata accuracy, backup option behavior, checkpoint export/import, and secondary catch-up.
- Stress tests should include invalid enum/status values, null optional bounds/timestamps, large multiget batches, pinned-slice lifetime, base iterator transfer in `WriteBatchWithIndex`, and parent/child metadata destruction order.
