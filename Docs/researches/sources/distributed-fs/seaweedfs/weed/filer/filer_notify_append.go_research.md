<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_append.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify_append.go

## Purpose
Uploads flushed metadata log data as SeaweedFS file chunks and appends them to a system-log filer entry.

## Important APIs and Functions
`appendToFile(targetFile string, data []byte) error` assigns/uploads bytes and updates the target filer entry. `assignAndUpload` performs volume assignment and HTTP upload.

## Control Flow and State
Append first uploads data to a volume, then finds or creates the filer entry at `targetFile`, computes append offset from `TotalSize`, appends a protobuf file chunk from upload result, and calls `CreateEntry` to persist metadata. Assignment uses storage rules from `FilerConf`, overridden by `metaLogCollection` and `metaLogReplication`.

## Persistence Behavior
Data is persisted to a volume before metadata is updated. Metadata is stored as a filer entry under the system log path. If metadata update fails after upload, the uploaded chunk may become unreferenced until deletion/cleanup.

## Dependencies and Integration Points
Used by `logFlushFunc` in `filer_notify.go`. Integrates with master volume assignment, operation uploader, filer storage rules, chunk metadata conversion, and `CreateEntry`.

## Risks
Uses `context.Background`, so caller cancellation is ignored. Upload-before-metadata ordering can leak chunks on failure. Append offset relies on current chunk metadata and no concurrent append conflict; log buffer flushing likely serializes per file but this function itself has no lock.

## Test Signals
No direct test in this subset. Notification replay tests indirectly depend on successfully persisted log entries in integration scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_append.go -->
