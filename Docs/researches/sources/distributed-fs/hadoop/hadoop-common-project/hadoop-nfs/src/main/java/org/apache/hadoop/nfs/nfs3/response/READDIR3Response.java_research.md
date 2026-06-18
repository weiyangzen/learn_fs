<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READDIR3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READDIR3Response.java

## Purpose

READDIR response with directory attrs, cookie verifier, entries, and EOF flag. The source was read as a complete 161-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READDIR3Response extends NFS3Response`, `public static class Entry3`, `public Entry3(long fileId, String name, long cookie)`, `public String getName()`, `public static class DirList3`, `public DirList3(Entry3[] entries, boolean eof)`, `public List<Entry3> getEntries()`, `public READDIR3Response(int status)`, `public READDIR3Response(int status, Nfs3FileAttributes postOpAttr)`, `public READDIR3Response(int status, Nfs3FileAttributes postOpAttr,`.

## Control Flow

Entry3 serializes fileId/name/cookie; DirList3 serializes entries as boolean-linked list ending false, then EOF.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `ArrayList`, `Arrays`, `Collections`, `List`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`, and others. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Method names contain deserialzie typo; malformed streams can loop until boolean false is encountered.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READDIR3Response.java -->
