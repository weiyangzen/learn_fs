<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_rename.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_rename.go

## Purpose
Validates whether a rename or move is allowed with respect to self-subdirectory moves and bucket boundaries.

## Important APIs and Functions
`CanRename(ctx, source, target, oldName) error` checks a candidate rename. `DetectBucket(source util.FullPath) string` extracts the bucket name from a path below `DirBucketsPath`.

## Control Flow and State
`CanRename` builds the full source path, rejects moving a directory under itself, loads the source entry, rejects renaming a bucket directory itself, detects source and target buckets, and rejects cross-bucket moves.

## Persistence Behavior
No writes. It reads source metadata through `FindEntry`.

## Dependencies and Integration Points
Uses bucket detection, `FindEntry`, and `util.FullPath.Child`. It protects S3 collection boundaries and directory move safety before actual rename logic elsewhere.

## Risks
The self-subdirectory check uses string prefix, which can overmatch paths such as `/foo` and `/foobar` unless path formatting prevents it. It requires `FindEntry` before bucket check, so lazy remote fetch or TTL side effects can occur.

## Test Signals
No direct tests in this subset. Bucket event tests cover related but not pre-rename validation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_rename.go -->
