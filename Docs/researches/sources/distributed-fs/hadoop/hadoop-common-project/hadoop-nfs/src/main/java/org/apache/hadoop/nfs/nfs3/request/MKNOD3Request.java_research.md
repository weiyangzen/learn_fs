<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKNOD3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKNOD3Request.java

## Purpose

MKNOD request DTO for special files, sockets, and FIFOs. The source was read as a complete 90-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class MKNOD3Request extends RequestWithHandle`, `public MKNOD3Request(FileHandle handle, String name, int type,`, `public static MKNOD3Request deserialize(XDR xdr) throws IOException`, `public String getName()`, `public int getType()`, `public SetAttr3 getObjAttr()`, `public Specdata3 getSpec()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads parent handle, name, type, then attributes/specdata depending on NfsFileType; serialize writes handle, name, attributes, and optional specdata.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `NfsFileType`, `FileHandle`, `Specdata3`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

serialize omits the type field even though deserialize expects it, a wire-format asymmetry to watch in round-trip tests.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKNOD3Request.java -->
