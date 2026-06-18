<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READLINK3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READLINK3Response.java

## Purpose

READLINK response with symlink attrs and target path opaque bytes. The source was read as a complete 67-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READLINK3Response extends NFS3Response`, `public READLINK3Response(int status)`, `public READLINK3Response(int status, Nfs3FileAttributes postOpAttr,`, `public static READLINK3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes symlink post-op attrs; on OK writes variable opaque path bytes.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Constructor defensively copies path, but null path input would fail.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READLINK3Response.java -->
