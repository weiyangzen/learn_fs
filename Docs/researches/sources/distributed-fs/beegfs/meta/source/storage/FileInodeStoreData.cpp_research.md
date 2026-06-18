# sources/distributed-fs/beegfs/meta/source/storage/FileInodeStoreData.cpp

## Purpose

`FileInodeStoreData.cpp` implements the small non-inline parts of `FileInodeStoreData`: path-info extraction and equality. The file is the bridge between stored original-parent metadata and the `PathInfo` object used by chunk path calculation and fsck-style inspection.

## Important APIs and Types

`FileInodeStoreData::getPathInfo(PathInfo*)` converts `FileInodeOrigFeature` into `PATHINFO_FEATURE_ORIG`, no flag, or `PATHINFO_FEATURE_ORIG_UNKNOWN`. It then sets original parent UID and original parent entry ID on the output `PathInfo`. `operator==` compares inode feature flags, `StatData`, entry ID, stripe pattern equivalence, original-feature state, original UID, and original parent entry ID.

## Control Flow and State

`getPathInfo` uses a `switch` over `origFeature`. The unset/default case logs an error because callers expected the dentry version or stored metadata to identify whether original-parent fields are meaningful. Equality delegates stripe comparison to `stripePatternEquals`, so it expects both objects to own valid stripe-pattern pointers.

## Persistence and Dependencies

The implementation depends on `FileInodeStoreData.h`, `PathInfo`, and logging through `LogContext`. The path info reflects stored metadata fields that are later used to locate storage chunks, especially after UID or parent changes.

## Integration Points

`FileInode::getPathInfo` calls into this method under the inode lock. Fsck enumeration in `MetaStore` also depends on file inode path info when building `FsckFileInode` records. Equality is primarily useful for serialization tests and metadata comparisons.

## Risks and Test Signals

The important risk is losing original parent data or leaving `origFeature` unset, which would make chunk paths ambiguous. Equality can dereference stripe patterns and should be exercised with valid cloned patterns. Tests should include all three `FileInodeOrigFeature` cases and compare objects with different flags, stat data, and stripe patterns.
