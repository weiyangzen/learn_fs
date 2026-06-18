<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READDIRPLUS3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READDIRPLUS3Response.java

## Purpose

READDIRPLUS response with directory attrs plus entries carrying attrs and file handles. The source was read as a complete 163-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READDIRPLUS3Response extends NFS3Response`, `public static class EntryPlus3`, `public EntryPlus3(long fileId, String name, long cookie,`, `public String getName()`, `public static class DirListPlus3`, `public DirListPlus3(EntryPlus3[] entries, boolean eof)`, `public List<EntryPlus3> getEntries()`, `public DirListPlus3 getDirListPlus()`, `public READDIRPLUS3Response(int status)`, `public READDIRPLUS3Response(int status, Nfs3FileAttributes postOpDirAttr,`.

## Control Flow

EntryPlus3 serializes fileId/name/cookie, attr-present+attrs, handle-present+handle; list is boolean-linked and ends with EOF.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `ArrayList`, `Arrays`, `Collections`, `List`, `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, and others. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Deserialize assumes attr and handle presence booleans are true and consumes values; null entry attrs/handles are unsafe on OK.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READDIRPLUS3Response.java -->
