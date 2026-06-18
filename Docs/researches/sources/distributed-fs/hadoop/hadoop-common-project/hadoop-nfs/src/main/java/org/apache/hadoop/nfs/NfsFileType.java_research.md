# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsFileType.java

## Purpose
`NfsFileType.java` maps NFS file type names to the numeric values used on the NFS wire.

## Important APIs, Types, and Functions
- Enum constants: `NFSREG(1)`, `NFSDIR(2)`, `NFSBLK(3)`, `NFSCHR(4)`, `NFSLNK(5)`, `NFSSOCK(6)`, and `NFSFIFO(7)`.
- `toValue()` returns the numeric protocol value.

## Control Flow and State
There is no mutable state. Values are assigned at enum construction and returned directly.

## Dependencies and Integration Points
`Nfs3FileAttributes` uses `NfsFileType` to set the serialized `type` field in attributes.

## Risks and Edge Cases
Protocol numeric values must not change. There is no reverse lookup helper in this enum.

## Test Signals
Coverage is indirect through NFS attribute serialization/deserialization and protocol response tests.
