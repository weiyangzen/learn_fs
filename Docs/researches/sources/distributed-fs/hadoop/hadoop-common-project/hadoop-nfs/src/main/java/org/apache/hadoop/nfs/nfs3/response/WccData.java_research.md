<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccData.java

## Purpose

Weak-cache-consistency container pairing pre-op WccAttr and post-op Nfs3FileAttributes. The source was read as a complete 66-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WccData`, `public WccAttr getPreOpAttr()`, `public void setPreOpAttr(WccAttr preOpAttr)`, `public Nfs3FileAttributes getPostOpAttr()`, `public void setPostOpAttr(Nfs3FileAttributes postOpAttr)`, `public WccData(WccAttr preOpAttr, Nfs3FileAttributes postOpAttr)`, `public static WccData deserialize(XDR xdr)`, `public void serialize(XDR out)`.

## Control Flow

Constructor normalizes nulls to empty objects; serialize always writes both presence booleans as true and both attribute blocks.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `XDR`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Protocol cannot represent absent WCC via this class once constructed; clients may see default attrs instead of no attrs.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccData.java -->
