<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/CREATE3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/CREATE3Request.java

## Purpose

CREATE request DTO carrying directory handle, name, create mode, attributes, and exclusive verifier. The source was read as a complete 87-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class CREATE3Request extends RequestWithHandle`, `public CREATE3Request(FileHandle handle, String name, int mode,`, `public static CREATE3Request deserialize(XDR xdr) throws IOException`, `public String getName()`, `public int getMode()`, `public SetAttr3 getObjAttr()`, `public long getVerf()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize branches on CREATE_UNCHECKED/GUARDED to read SetAttr3 or CREATE_EXCLUSIVE to read verifier; invalid modes throw IOException.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `Nfs3Constant`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

serialize always writes objAttr and never writes the exclusive verifier branch, so CREATE_EXCLUSIVE round-trips need scrutiny.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/CREATE3Request.java -->
