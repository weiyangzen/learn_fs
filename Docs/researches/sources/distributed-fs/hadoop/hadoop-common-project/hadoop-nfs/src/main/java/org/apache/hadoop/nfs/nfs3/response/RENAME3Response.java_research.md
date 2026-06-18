<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RENAME3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RENAME3Response.java

## Purpose

RENAME response carrying source and destination directory WCC. The source was read as a complete 62-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RENAME3Response extends NFS3Response`, `public RENAME3Response(int status)`, `public RENAME3Response(int status, WccData fromWccData, WccData toWccData)`, `public WccData getFromDirWcc()`, `public WccData getToDirWcc()`, `public static RENAME3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize/serialize status plus fromDirWcc and toDirWcc for all outcomes.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Both WCC blocks should reflect pre/post states, especially same-directory renames.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RENAME3Response.java -->
