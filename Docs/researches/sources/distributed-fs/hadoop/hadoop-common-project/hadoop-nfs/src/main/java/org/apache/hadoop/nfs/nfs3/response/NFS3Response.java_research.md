<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/NFS3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/NFS3Response.java

## Purpose

Base class for NFSv3 responses, holding numeric NFS status. The source was read as a complete 57-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class NFS3Response`, `public NFS3Response(int status)`, `public int getStatus()`, `public void setStatus(int status)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

serialize creates an ONC RPC accepted reply with xid/verifier, writes reply header, then writes status.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `RpcAcceptedReply`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Subclasses must call super.serialize first or the wire reply lacks RPC framing/status.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/NFS3Response.java -->
