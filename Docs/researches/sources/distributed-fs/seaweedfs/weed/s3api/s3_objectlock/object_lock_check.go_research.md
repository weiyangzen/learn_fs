# sources/distributed-fs/seaweedfs/weed/s3api/s3_objectlock/object_lock_check.go

## Purpose
`object_lock_check.go` provides shared object-lock checks used before destructive bucket operations. It detects active legal holds and retention periods on current objects and versions by scanning filer entries.

## Important APIs, Types, and Functions
Public helpers are `EntryHasActiveLock`, `HasObjectsWithActiveLocks`, `IsObjectLockEnabled`, and `CheckBucketForLockedObjects`. Internal helpers are `paginateEntries`, `recursivelyCheckLocksWithClient`, and `checkVersionsForLocksWithClient`.

## Control Flow
`EntryHasActiveLock` checks `Entry.Extended` for a legal hold set to `ON` or for governance/compliance retention whose retain-until timestamp is in the future. Unparseable retention dates fail safe as locked. `HasObjectsWithActiveLocks` starts a recursive scan at a bucket path. `paginateEntries` streams directory entries with a 10,000 entry page limit, tracks the last name, skips invalid names that could cause path traversal, and allows callback-controlled early stop. Recursion skips multipart upload scratch folders, descends ordinary directories, and gives `.versions` folders to a version-specific scanner. `CheckBucketForLockedObjects` first looks up the bucket entry, returns early if object lock is disabled, then scans for active locks and returns an error if any exist.

## State and Persistence Behavior
The file reads bucket and object metadata from the filer but does not mutate it. It treats `Entry.Extended` object-lock fields as durable source of truth and uses current wall-clock time for retention comparisons.

## Dependencies and Integration Points
It integrates with `filer_pb.SeaweedFilerClient` listing and lookup RPCs, S3 object-lock constants, admin UI, shell commands, and S3 bucket deletion logic.

## Risks and Edge Cases
The retention date parser expects Unix seconds in metadata; any other format is treated as locked, which is safe but may block deletion after metadata corruption. Pagination relies on entries being returned in stable name order. The scan can be expensive on large buckets, though it exits as soon as a lock is found. Invalid entry names are skipped, preventing traversal but potentially hiding malformed locked entries.

## Test Signals
Tests should cover legal hold case/whitespace normalization, governance and compliance retention before/after current time, malformed retain-until values, version folder scanning, multipart folder skipping, invalid name skipping, object-lock-disabled buckets, and propagation of filer list/lookup errors.
