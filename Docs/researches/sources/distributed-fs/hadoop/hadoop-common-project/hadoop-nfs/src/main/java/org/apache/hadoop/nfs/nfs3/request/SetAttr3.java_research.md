<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SetAttr3.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SetAttr3.java

## Purpose

Mutable holder for NFSv3 sattr3 optional settable fields. The source was read as a complete 177-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class SetAttr3`, `public enum SetAttrField`, `public SetAttr3()`, `public SetAttr3(int mode, int uid, int gid, long size, NfsTime atime,`, `public int getMode()`, `public int getUid()`, `public int getGid()`, `public void setGid(int gid)`, `public long getSize()`, `public NfsTime getAtime()`.

## Control Flow

serialize writes booleans for mode/uid/gid/size and timestamp data when updateFields contains ATIME/MTIME; deserialize reads booleans/time-set enums and records which fields should be updated.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `EnumSet`, `NfsTime`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Constructor accepts atime/mtime but does not assign them, so serialized client-time attrs can be null unless set elsewhere; server-time deserialize uses current wall clock.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SetAttr3.java -->
