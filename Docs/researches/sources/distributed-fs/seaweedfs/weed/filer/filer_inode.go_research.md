<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_inode.go

## Purpose
Backfills stable inode values for filer entries so persisted metadata aligns with FUSE derivation and hard-link identity.

## Important APIs and Functions
`ensureEntryInode(entry *Entry)` is a `Filer` method that sets `entry.Attr.Inode` if it is zero.

## Control Flow and State
Nil entries and entries with an inode are left untouched. Missing creation time is set to `time.Now()`. Hard-linked entries hash the `HardLinkId`; ordinary entries use `FullPath.AsInode(crtime.Unix())`.

## Persistence Behavior
The computed inode is persisted when the caller later inserts or updates the entry. This avoids needing a separate reverse inode index.

## Dependencies and Integration Points
Called from `CreateEntry`, parent directory auto-creation, and `UpdateEntry` when legacy entries lack inodes. Uses `util.HashStringToLong` and `util.FullPath.AsInode`.

## Risks
For non-hard-linked entries, inode changes if the path and creation time combination changes before persistence. Missing crtime uses wall clock, so legacy backfill is deterministic only after first persistence. Hard-link IDs must remain stable.

## Test Signals
`filer_inode_test.go` verifies FUSE-equivalent derivation, shared hard-link inode, create-time inode assignment, parent directory assignment, update preservation, and legacy backfill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_inode.go -->
