# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountResponse.java

## Purpose
`MountResponse.java` serializes XDR responses for NFS mount protocol operations.

## Important APIs, Types, and Functions
- `MNT_OK` is the success status code.
- `writeMNTResponse(int status, XDR xdr, int xid, byte[] handle)` writes an accepted RPC reply, status, and on success the file handle plus supported auth flavor list containing `AUTH_SYS`.
- `writeMountList(XDR xdr, int xid, List<MountEntry> mounts)` writes accepted reply and a linked-list style sequence of mount entries followed by a false terminator.
- `writeExportList(XDR xdr, int xid, List<String> exports, List<NfsExports> hostMatcher)` writes export paths and their allowed host groups, with nested boolean list terminators.

## Control Flow and State
All methods are static and append to the provided `XDR`. RPC accepted headers are written first using `RpcAcceptedReply` and `VerifierNone`. Response lists use ONCRPC boolean "value follows" encoding.

## Dependencies and Integration Points
It integrates mount protocol code with ONCRPC reply types, `AuthFlavor.AUTH_SYS`, `MountEntry`, and `NfsExports.getHostGroupList()`. Mount daemon implementations call these helpers when serving MNT, DUMP, and EXPORT.

## Risks and Edge Cases
`writeExportList()` uses an `assert` for matching list sizes, which is disabled unless assertions are enabled; mismatched lists can still cause runtime index errors. Host groups are encoded as UTF-8 variable opaque values.

## Test Signals
No direct tests in this subset. Protocol correctness depends on byte-accurate XDR serialization and list termination.
