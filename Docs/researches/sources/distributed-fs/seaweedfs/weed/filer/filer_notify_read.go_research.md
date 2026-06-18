<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_read.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify_read.go

## Purpose
Lists and reads persisted metadata log files in timestamp order across multiple filers, with chunk-level caching and streaming fallback.

## Important APIs and Types
`LogFileEntry`, `collectPersistedLogBuffer`, `CollectLogFileRefs`, `HasPersistedLogFiles`, `LogEntryItemPriorityQueue`, `OrderedLogVisitor`, `LogFileEntryCollector`, `LogFileQueueIterator`, and `LogFileIterator` are the core pieces.

## Control Flow and State
Collection lists day directories from `SystemLogDir`, then hour-minute log files. `OrderedLogVisitor` maintains one iterator per filer and a min-heap of next log entries by timestamp. `LogFileEntryCollector` incrementally enqueues more day/hour files. `LogFileQueueIterator` advances across files and skips unreadable deleted chunks. `LogFileIterator` first decodes immutable chunks through a shared cache; if a chunk is incomplete because records cross chunk boundaries, it falls back to streaming the whole file.

## Persistence Behavior
Reads persisted filer entries and their chunks; does not modify state. `CollectLogFileRefs` exposes chunk references without reading volume data for clients that can fetch directly.

## Dependencies and Integration Points
Uses filer directory listing, `NewChunkStreamReaderFromFiler`, persisted-log cache, protobuf log entry decoding, master client chunk reads, system log naming conventions, and `log_buffer.MessagePosition`.

## Risks
Ordering is per-entry timestamp with per-filer iterators; clock skew can still affect global semantics. Directory listing uses `context.Background` in collector paths, so caller cancellation is not consistently propagated. Chunk cache correctness depends on immutable log chunks. Invalid file names are skipped.

## Test Signals
No dedicated tests in the listed subset. `filer_notify.go` replay path depends on this code, and `isChunkNotFoundError` handles operational deletion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_read.go -->
