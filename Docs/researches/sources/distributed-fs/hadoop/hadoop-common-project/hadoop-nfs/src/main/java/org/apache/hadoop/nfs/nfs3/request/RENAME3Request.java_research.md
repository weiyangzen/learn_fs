<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RENAME3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RENAME3Request.java

## Purpose

RENAME request DTO carrying source directory/name and destination directory/name. The source was read as a complete 76-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RENAME3Request extends NFS3Request`, `public static RENAME3Request deserialize(XDR xdr) throws IOException`, `public RENAME3Request(FileHandle fromDirHandle, String fromName,`, `public FileHandle getFromDirHandle()`, `public String getFromName()`, `public FileHandle getToDirHandle()`, `public String getToName()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads source handle/name then destination handle/name; serialize mirrors that order.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Does not extend RequestWithHandle because two handles are first-class; name validation is external.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RENAME3Request.java -->
