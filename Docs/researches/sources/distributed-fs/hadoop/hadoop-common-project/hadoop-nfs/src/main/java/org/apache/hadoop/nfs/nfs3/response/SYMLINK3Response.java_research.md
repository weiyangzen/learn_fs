<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SYMLINK3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SYMLINK3Response.java

## Purpose

SYMLINK response with created symlink handle/attrs plus directory WCC. The source was read as a complete 87-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class SYMLINK3Response extends NFS3Response`, `public SYMLINK3Response(int status)`, `public SYMLINK3Response(int status, FileHandle handle,`, `public FileHandle getObjFileHandle()`, `public Nfs3FileAttributes getObjPostOpAttr()`, `public WccData getDirWcc()`, `public static SYMLINK3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK writes handle-present, handle, attr-present, attrs, then dirWcc; failures write only dirWcc.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

OK requires non-null handle/attrs; errors still need accurate dirWcc.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SYMLINK3Response.java -->
