# sources/distributed-fs/juicefs/pkg/vfs/writer.go

## Purpose
This file implements JuiceFS buffered asynchronous writes. It exposes `FileWriter` and `DataWriter` interfaces and implements them with `dataWriter`, `fileWriter`, `chunkWriter`, and `sliceWriter`. The writer accepts byte ranges from VFS handles, groups them into chunk slices, uploads slice data to the chunk store, commits slice metadata in order, invalidates read cache ranges, and flushes pending writes on demand or in the background.

## Important APIs, Types, and Functions
`FileWriter` defines `Write`, `Flush`, `Close`, `GetLength`, and `Truncate`. `DataWriter` defines inode-scoped `Open`, `Flush`, `GetLength`, `Truncate`, `UpdateMtime`, and `FlushAll`. `sliceWriter.prepareID`, `write`, `flushData`, and `markDone` manage slice object IDs and upload completion. `chunkWriter.findWritableSlice` and `commitThread` choose writable slices and commit finished slices to metadata. `fileWriter.Write`, `writeChunk`, `flush`, `Flush`, `Close`, `Truncate`, and `updateMtime` manage file-level buffering. `dataWriter.flushAll`, `Open`, `free`, and `FlushAll` manage global writer lifetime and background flushing.

## Control Flow and State
A write enters `fileWriter.Write`, throttles when too many slices or too much buffer memory exists, waits for active flushes, splits data across metadata chunks, and calls `writeChunk`. A chunk either reuses a non-frozen slice or creates a new `sliceWriter` backed by `ChunkStore.NewWriter`. New slice IDs are allocated asynchronously with `Meta.NewSlice`; full or aged slices freeze and upload via `flushData`. Each `chunkWriter` has a `commitThread` that waits for slices to finish, waits for dependency slices when growing file length across chunks, writes slice metadata with `Meta.Write`, invalidates reader cache, records errors, and frees chunks.

Volatile state includes per-file length, error state, pending chunk/slice maps, wait counters, reference counts, and conditions. Persistent state is the uploaded chunk object plus the metadata slice committed by `Meta.Write`. `Flush` freezes all pending slices and waits until chunks drain, honoring cancellation after put-timeout windows and enforcing a computed deadline. `FlushAll` walks all open writers and returns the first nonzero errno as an error.

## Dependencies and Integration Points
The writer depends on `meta.Meta` for slice IDs and metadata commits, `chunk.ChunkStore` for object writers and memory accounting, `DataReader` for invalidation, and `utils.Cond` for wait/notify. `vfs.go` calls it from open/create/write/read/truncate/fallocate/copy/release/fsync/flush paths.

## Risks and Edge Cases
Ordering is subtle: growing slices can depend on prior chunk slices so metadata length does not advance out of order. Overlapping writes that cannot fit the latest writable slice create new slices or may return nil from `findWritableSlice`, relying on metadata overlay semantics. `Truncate` only adjusts buffered length and has a TODO to truncate buffered data when shrinking. Background goroutines and reference counting must stay balanced to avoid leaked file writers. Flush timeouts dump goroutine stacks and return `EIO`; long object-store stalls can surface as write failures. Memory throttling uses process allocation minus store memory, which may be noisy.

## Test Signals
`TestVFSIO` stresses this writer through sparse writes, fallocate, fsync, copy-file-range, sequential 128 KiB writes, many small overlapping writes, background flush waiting, read-after-write, and invalid fd paths. The writer itself has no direct tests in this target set, so most coverage is integration-level through VFS I/O.
