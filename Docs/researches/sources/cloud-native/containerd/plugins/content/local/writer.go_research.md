<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer.go -->
# sources/cloud-native/containerd/plugins/content/local/writer.go

## Purpose
Write transaction implementation for local content store ingests.

## Important APIs, Types, And Functions
writer fields and methods Status, Digest, Write, Commit, Close, Truncate, and Sync.

## Control Flow
Write appends to data file, updates digester and offset. Commit syncs/stat/closes, validates size/digest, optionally rehashes to expected algorithm, renames ingest data to blob path, syncs parent dir, enables fsverity, timestamps, cleans ingest, stores labels, and chmods readonly on non-Windows. Close leaves resumable state.

## State And Persistence
Persists ingest data while open/closed before commit; commit atomically promotes by rename into blobs tree and removes ingest dir. Uses file mtimes for committed info.

## Dependencies And Integration Points
Tightly coupled to store.go paths/locks and fsverity. Implements content.Writer.

## Risks And Edge Cases
Write increments offset by len(p) rather than n, which matters if a partial write returns n<len(p) with error. Commit after Close fails. Cross-device rename would fail if ingest/blob roots diverged, but they share root.

## Test Signals
store_test.go covers sha256/sha512 commits, duplicate content, fsverity, truncate recovery, and content testsuite behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer.go -->
