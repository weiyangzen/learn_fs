<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READ3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READ3Response.java

## Purpose

READ response with post-op attrs, count, EOF flag, and data bytes. The source was read as a complete 99-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READ3Response extends NFS3Response`, `public READ3Response(int status)`, `public READ3Response(int status, Nfs3FileAttributes postOpAttr, int count,`, `public Nfs3FileAttributes getPostOpAttr()`, `public int getCount()`, `public boolean isEof()`, `public ByteBuffer getData()`, `public static READ3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes attrs; on OK writes count, eof, opaque length, and fixed opaque data from ByteBuffer.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `ByteBuffer`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Assumes data.array() and count agree; failure responses have zero data.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READ3Response.java -->
