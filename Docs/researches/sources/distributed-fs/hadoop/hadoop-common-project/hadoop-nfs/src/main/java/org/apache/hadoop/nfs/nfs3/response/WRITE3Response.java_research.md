<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WRITE3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WRITE3Response.java

## Purpose

WRITE response with file WCC, committed byte count, stability mode, and verifier. The source was read as a complete 88-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WRITE3Response extends NFS3Response`, `public WRITE3Response(int status)`, `public WRITE3Response(int status, WccData fileWcc, int count,`, `public int getCount()`, `public WriteStableHow getStableHow()`, `public long getVerifer()`, `public static WRITE3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes WCC; on OK writes count, stableHow value, and verifier.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3Constant`, `Nfs3Status`, `WriteStableHow`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Field/getter typo `verifer`/`getVerifer`; deserialize uses WriteStableHow.values()[how], so invalid wire enum can throw.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WRITE3Response.java -->
