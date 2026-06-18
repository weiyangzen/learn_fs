<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LOOKUP3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LOOKUP3Response.java

## Purpose

LOOKUP response with resolved file handle, object post-op attrs, and parent directory attrs. The source was read as a complete 77-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class LOOKUP3Response extends NFS3Response`, `public LOOKUP3Response(int status)`, `public LOOKUP3Response(int status, FileHandle fileHandle,`, `public LOOKUP3Response(XDR xdr) throws IOException`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Constructor-from-XDR reads status, optional handle/object attrs on OK, and optional directory attrs; serialize writes corresponding presence booleans.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

serialize emits attr-present booleans based on nullness; OK with null handle/attrs is unsafe.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LOOKUP3Response.java -->
