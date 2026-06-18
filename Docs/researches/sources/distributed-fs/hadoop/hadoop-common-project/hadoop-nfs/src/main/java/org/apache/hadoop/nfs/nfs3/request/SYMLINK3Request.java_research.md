<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SYMLINK3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SYMLINK3Request.java

## Purpose

SYMLINK request DTO carrying parent handle, link name, symlink attributes, and target path bytes as a string. The source was read as a complete 72-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class SYMLINK3Request extends RequestWithHandle`, `public static SYMLINK3Request deserialize(XDR xdr) throws IOException`, `public SYMLINK3Request(FileHandle handle, String name, SetAttr3 symAttr,`, `public String getName()`, `public SetAttr3 getSymAttr()`, `public String getSymData()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, name, SetAttr3, and symlink data; serialize writes name/attrs/target in XDR order.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local validation of symlink target length or name encoding beyond UTF-8 byte conversion.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SYMLINK3Request.java -->
