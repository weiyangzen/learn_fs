<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify.go

## Purpose
Builds and logs metadata change events, sends optional notifications, triggers local empty-folder cleanup, flushes metadata logs to filer storage, and reads persisted log buffers.

## Important APIs and State
`NotifyUpdateEvent`, `notifyUpdateEvent`, `newMetadataEvent`, `logMetaEvent`, `triggerLocalEmptyFolderCleanup`, `logFlushFunc`, `isChunkNotFoundError`, and `ReadPersistedLogBuffer` are the main APIs. `persistedLogReplaySem` caps concurrent persisted log replays at 64.

## Control Flow and State
Notification skips suppressed contexts, nil events, and system log paths. It appends the local filer signature if absent, builds a `SubscribeMetadataResponse`, optionally sends to `notification.Queue`, adds serialized data to `LocalMetaLogBuffer`, records test/instrumentation sinks, and updates empty-folder cleanup. Flush writes buffered data to `/topics/...`-style system log files by appending chunks until success.

## Persistence Behavior
Metadata events persist through log buffer flushes to filer entries. `ReadPersistedLogBuffer` replays these logs using `collectPersistedLogBuffer`, a readahead goroutine, and visitor close cleanup. Missing chunks/volumes during persisted replay can be skipped by lower iterator code.

## Dependencies and Integration Points
Uses protobuf marshaling, `notification.Queue`, `log_buffer`, filer append/upload, system log constants, empty-folder cleanup, persisted log readers, HTTP not-found errors, and context metadata-event suppression/sinks.

## Risks
`logFlushFunc` retries forever with sleep, which can stall shutdown or hide persistent write failures. Signatures prevent loops but rely on correct propagation. Readahead goroutine must be stopped on all returns; code explicitly does this. System log path filtering suppresses events below `SystemLogDir`.

## Test Signals
`filer_notify_test.go` checks protobuf preservation of chunk `SourceFileId`. Persisted replay behavior likely has tests elsewhere; this subset provides limited direct coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify.go -->
