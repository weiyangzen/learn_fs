<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/COMMIT3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/COMMIT3Response.java

## Purpose

COMMIT response with file WCC data and write verifier. The source was read as a complete 69-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class COMMIT3Response extends NFS3Response`, `public COMMIT3Response(int status)`, `public COMMIT3Response(int status, WccData fileWcc, long verf)`, `public WccData getFileWcc()`, `public long getVerf()`, `public static COMMIT3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always serializes WccData; verifier is serialized only on NFS3_OK.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3Constant`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Default verifier comes from Nfs3Constant.WRITE_COMMIT_VERF; server must keep verifier stable across write/commit semantics.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/COMMIT3Response.java -->
