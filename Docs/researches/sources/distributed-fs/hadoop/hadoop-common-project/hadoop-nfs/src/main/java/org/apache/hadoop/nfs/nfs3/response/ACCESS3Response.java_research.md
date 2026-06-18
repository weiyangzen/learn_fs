<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/ACCESS3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/ACCESS3Response.java

## Purpose

ACCESS response with post-operation attributes and access bitmask. The source was read as a complete 70-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class ACCESS3Response extends NFS3Response`, `public ACCESS3Response(int status)`, `public ACCESS3Response(int status, Nfs3FileAttributes postOpAttr, int access)`, `public static ACCESS3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK deserialize reads attributes and access; serialize emits a postOpAttr-present boolean and access only on OK.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Failure serialization emits false for attributes, so callers expecting weak cache data on failures must tolerate absence.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/ACCESS3Response.java -->
