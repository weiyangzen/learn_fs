<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/REMOVE3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/REMOVE3Response.java

## Purpose

REMOVE response carrying parent directory WCC. The source was read as a complete 53-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class REMOVE3Response extends NFS3Response`, `public REMOVE3Response(int status)`, `public REMOVE3Response(int status, WccData dirWcc)`, `public static REMOVE3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize reads status then WccData; serialize normalizes null WCC to empty and writes it.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Empty default WCC is protocol-shaped but may reduce client cache consistency if real attrs are unavailable.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/REMOVE3Response.java -->
