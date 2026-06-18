<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccAttr.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccAttr.java

## Purpose

Weak-cache-consistency pre-operation attribute tuple: size, mtime, ctime. The source was read as a complete 73-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WccAttr`, `public long getSize()`, `public NfsTime getMtime()`, `public NfsTime getCtime()`, `public WccAttr()`, `public WccAttr(long size, NfsTime mtime, NfsTime ctime)`, `public static WccAttr deserialize(XDR xdr)`, `public void serialize(XDR out)`.

## Control Flow

deserialize reads size hyper plus two NfsTime values; serialize writes zeros for null times.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `NfsTime`, `XDR`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

serialize mutates null mtime/ctime to zero timestamps, masking missing pre-op times.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccAttr.java -->
