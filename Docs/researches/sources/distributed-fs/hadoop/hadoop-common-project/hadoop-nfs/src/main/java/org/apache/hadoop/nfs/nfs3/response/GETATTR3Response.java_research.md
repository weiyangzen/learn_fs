<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/GETATTR3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/GETATTR3Response.java

## Purpose

GETATTR response carrying full post-operation attributes on success. The source was read as a complete 58-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class GETATTR3Response extends NFS3Response`, `public GETATTR3Response(int status)`, `public GETATTR3Response(int status, Nfs3FileAttributes attrs)`, `public void setPostOpAttr(Nfs3FileAttributes postOpAttr)`, `public static GETATTR3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize reads attributes only on NFS3_OK; serialize writes attributes only on OK after the RPC accepted header/status.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Failure responses carry no attributes; callers must not assume postOpAttr is populated after deserialize failures.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/GETATTR3Response.java -->
