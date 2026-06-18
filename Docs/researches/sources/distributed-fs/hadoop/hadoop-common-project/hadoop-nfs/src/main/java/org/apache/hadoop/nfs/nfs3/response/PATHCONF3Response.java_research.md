<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/PATHCONF3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/PATHCONF3Response.java

## Purpose

PATHCONF response with path configuration limits and case/link/chown booleans. The source was read as a complete 119-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class PATHCONF3Response extends NFS3Response`, `public PATHCONF3Response(int status)`, `public PATHCONF3Response(int status, Nfs3FileAttributes postOpAttr,`, `public static PATHCONF3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes post-op attrs; on OK writes linkMax, nameMax, noTrunc, chownRestricted, caseInsensitive, casePreserving.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Deserialize reads a boolean and attrs before status-specific fields, assuming the attribute block is present.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/PATHCONF3Response.java -->
