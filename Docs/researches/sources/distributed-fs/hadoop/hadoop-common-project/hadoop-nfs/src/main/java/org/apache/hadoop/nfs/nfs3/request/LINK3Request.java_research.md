<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/LINK3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/LINK3Request.java

## Purpose

LINK request DTO carrying target object handle and destination directory/name. The source was read as a complete 63-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class LINK3Request extends RequestWithHandle`, `public LINK3Request(FileHandle handle, FileHandle fromDirHandle,`, `public static LINK3Request deserialize(XDR xdr) throws IOException`, `public FileHandle getFromDirHandle()`, `public String getFromName()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads target handle, destination directory handle, and destination name; serialize writes both handles and UTF-8 name.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Uses String.length in serialization, which can diverge from UTF-8 byte length for non-ASCII names.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/LINK3Request.java -->
