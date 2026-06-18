<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/LOOKUP3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/LOOKUP3Request.java

## Purpose

LOOKUP request DTO for resolving a name under a directory handle. The source was read as a complete 60-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class LOOKUP3Request extends RequestWithHandle`, `public LOOKUP3Request(FileHandle handle, String name)`, `public static LOOKUP3Request deserialize(XDR xdr) throws IOException`, `public String getName()`, `public void setName(String name)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle and XDR string; serialize writes handle plus UTF-8 byte length and bytes.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`, `VisibleForTesting`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Has a VisibleForTesting setter; mutation after construction can affect reused request objects.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/LOOKUP3Request.java -->
