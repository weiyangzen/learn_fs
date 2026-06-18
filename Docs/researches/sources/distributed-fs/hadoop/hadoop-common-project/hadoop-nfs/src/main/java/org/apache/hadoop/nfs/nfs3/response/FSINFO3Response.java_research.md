<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSINFO3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSINFO3Response.java

## Purpose

FSINFO response describing I/O sizes, max file size, timestamp granularity, and filesystem property flags. The source was read as a complete 164-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSINFO3Response extends NFS3Response`, `public FSINFO3Response(int status)`, `public FSINFO3Response(int status, Nfs3FileAttributes postOpAttr, int rtmax,`, `public static FSINFO3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes post-op attributes; on OK writes rtmax/rtpref/rtmult, wtmax/wtpref/wtmult, dtpref, maxFileSize, timeDelta, and properties.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `NfsTime`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

timeDelta must be non-null on OK; deserialize assumes post-op attrs follow after a boolean.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSINFO3Response.java -->
