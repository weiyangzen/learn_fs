# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountEntry.java

## Purpose
`MountEntry.java` is a small immutable value object representing one NFS mount table entry: client host plus mounted path.

## Important APIs, Types, and Functions
- Constructor `MountEntry(String host, String path)` stores final fields.
- `getHost()` and `getPath()` expose values.
- `equals()` returns true for another `MountEntry` with equal host and path.
- `hashCode()` combines host and path hashes.

## Control Flow and State
There is no mutable state after construction. The object is suitable for lists, sets, and mount response serialization.

## Dependencies and Integration Points
`MountResponse.writeMountList()` consumes `List<MountEntry>` to serialize mountd DUMP responses.

## Risks and Edge Cases
The constructor does not null-check host or path, so `equals()` and `hashCode()` can throw if null values are supplied.

## Test Signals
No direct test is in this subset, but mount response serialization depends on predictable equality and getters.
