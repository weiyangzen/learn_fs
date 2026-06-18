<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/CREATE3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/CREATE3Response.java

## Purpose

CREATE response with optional object handle, object attributes, and directory WCC. The source was read as a complete 90-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class CREATE3Response extends NFS3Response`, `public CREATE3Response(int status)`, `public CREATE3Response(int status, FileHandle handle,`, `public FileHandle getObjHandle()`, `public Nfs3FileAttributes getPostOpObjAttr()`, `public WccData getDirWcc()`, `public static CREATE3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK it emits handle-present, handle, attr-present, attr, then directory WCC; failures emit directory WCC only.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Mutates null dirWcc to empty WccData during serialize; OK responses require non-null handle/attrs.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/CREATE3Response.java -->
