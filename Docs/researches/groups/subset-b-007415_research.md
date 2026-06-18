# subset-b-007415 Research

Grouped source research for Hadoop NFSv3 request/response wire DTOs, NFS utility tests, and Hadoop Registry client API/implementation support files. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Status.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Status.java

## Purpose

Protocol constant table for NFSv3 success and error status values used throughout request handlers and response serializers. The source was read as a complete 162-line file for this research item.

## Important APIs, Types, and Functions

Defines NFSv3 numeric status constants including `NFS3_OK=0`, `NFS3ERR_PERM=1`, `NFS3ERR_NOENT=2`, `NFS3ERR_IO=5`, `NFS3ERR_NXIO=6`, `NFS3ERR_ACCES=13`, `NFS3ERR_EXIST=17`, `NFS3ERR_XDEV=18`, `NFS3ERR_NODEV=19`, `NFS3ERR_NOTDIR=20`, `NFS3ERR_ISDIR=21`, `NFS3ERR_INVAL=22`, and additional protocol errors.

## Control Flow

There is no runtime control flow; response code and server logic reference these static integer constants when mapping filesystem/auth/protocol failures to NFS wire status.

## State and Persistence Behavior

No state or persistence; constants are loaded with the class and used process-wide.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include every NFSv3 response class and server-side exception/status mapping.

## Risks and Edge Cases

`NFS3ERR_NOTDIR` is mutable (`static int`) while most constants are final; accidental reassignment would corrupt status mapping. Numeric values are wire ABI and must not drift from RFC/NFSv3 expectations.

## Test Signals

Compile-time use plus status-mapping tests from filesystem errors to NFS3ERR_* values; serialization tests should confirm integer values on the wire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Status.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/ACCESS3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/ACCESS3Request.java

## Purpose

ACCESS request DTO containing only the target file handle. The source was read as a complete 42-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class ACCESS3Request extends RequestWithHandle`, `public static ACCESS3Request deserialize(XDR xdr) throws IOException`, `public ACCESS3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle with NFS3Request.readHandle; serialize writes the same handle.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Risk is minimal; malformed/invalid handles surface as IOException from readHandle.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/ACCESS3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/COMMIT3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/COMMIT3Request.java

## Purpose

COMMIT request DTO for flushing a byte range of a file. The source was read as a complete 59-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class COMMIT3Request extends RequestWithHandle`, `public static COMMIT3Request deserialize(XDR xdr) throws IOException`, `public COMMIT3Request(FileHandle handle, long offset, int count)`, `public long getOffset()`, `public int getCount()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, 64-bit offset, and 32-bit count; serialize writes those fields in NFS order.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local guard against negative offsets/counts or int overflow in downstream filesystem code.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/COMMIT3Request.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSINFO3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSINFO3Request.java

## Purpose

FSINFO request DTO containing only the queried filesystem handle. The source was read as a complete 42-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSINFO3Request extends RequestWithHandle`, `public static FSINFO3Request deserialize(XDR xdr) throws IOException`, `public FSINFO3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle; serialize writes it unchanged.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local validation of whether the handle is a filesystem root or file.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSINFO3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSSTAT3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSSTAT3Request.java

## Purpose

FSSTAT request DTO containing only the queried filesystem handle. The source was read as a complete 42-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSSTAT3Request extends RequestWithHandle`, `public static FSSTAT3Request deserialize(XDR xdr) throws IOException`, `public FSSTAT3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle; serialize writes it unchanged.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Semantics depend entirely on the server implementation receiving the handle.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSSTAT3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/GETATTR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/GETATTR3Request.java

## Purpose

GETATTR request DTO containing only the target handle. The source was read as a complete 42-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class GETATTR3Request extends RequestWithHandle`, `public static GETATTR3Request deserialize(XDR xdr) throws IOException`, `public GETATTR3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle; serialize writes it unchanged.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Handle decode is the only local failure path.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/GETATTR3Request.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKDIR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKDIR3Request.java

## Purpose

MKDIR request DTO carrying parent directory handle, new name, and settable attributes. The source was read as a complete 62-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class MKDIR3Request extends RequestWithHandle`, `public static MKDIR3Request deserialize(XDR xdr) throws IOException`, `public MKDIR3Request(FileHandle handle, String name, SetAttr3 objAttr)`, `public String getName()`, `public SetAttr3 getObjAttr()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, name, and SetAttr3; serialize writes handle, UTF-8 name, and attributes.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local validation of empty names, slash characters, or attribute consistency.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKDIR3Request.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/NFS3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/NFS3Request.java

## Purpose

Abstract base for NFSv3 request argument objects. The source was read as a complete 46-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public abstract class NFS3Request`, `public abstract void serialize(XDR xdr);`.

## Control Flow

Shared static readHandle constructs FileHandle and throws IOException if FileHandle.deserialize returns false; subclasses implement serialize(XDR).

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Subclasses rely on this method for handle validation, but all other argument validation is left to operation-specific code or server handlers.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/NFS3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/PATHCONF3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/PATHCONF3Request.java

## Purpose

PATHCONF request DTO containing only the target handle. The source was read as a complete 42-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class PATHCONF3Request extends RequestWithHandle`, `public static PATHCONF3Request deserialize(XDR xdr) throws IOException`, `public PATHCONF3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle; serialize writes it unchanged.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No pathconf-specific state is represented locally.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/PATHCONF3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READ3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READ3Request.java

## Purpose

READ request DTO for a byte range. The source was read as a complete 62-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READ3Request extends RequestWithHandle`, `public static READ3Request deserialize(XDR xdr) throws IOException`, `public READ3Request(FileHandle handle, long offset, int count)`, `public long getOffset()`, `public int getCount()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, 64-bit offset, and 32-bit count; serialize writes the same.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`, `VisibleForTesting`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Request limits and negative values are not enforced here, so server handlers must bound counts.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READ3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIR3Request.java

## Purpose

READDIR request DTO for listing directory entries. The source was read as a complete 68-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READDIR3Request extends RequestWithHandle`, `public static READDIR3Request deserialize(XDR xdr) throws IOException`, `public READDIR3Request(FileHandle handle, long cookie, long cookieVerf,`, `public long getCookie()`, `public long getCookieVerf()`, `public long getCount()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, cookie, cookie verifier, and count; serialize writes them in that order.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Cookie validity and count limits are deferred to server logic.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIR3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIRPLUS3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIRPLUS3Request.java

## Purpose

READDIRPLUS request DTO for entries plus attributes/handles. The source was read as a complete 77-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READDIRPLUS3Request extends RequestWithHandle`, `public static READDIRPLUS3Request deserialize(XDR xdr) throws IOException`, `public READDIRPLUS3Request(FileHandle handle, long cookie, long cookieVerf,`, `public long getCookie()`, `public long getCookieVerf()`, `public int getDirCount()`, `public int getMaxCount()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, cookie, cookie verifier, dirCount, and maxCount; serialize mirrors them.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

dirCount/maxCount bounds and stale cookies are not checked locally.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIRPLUS3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READLINK3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READLINK3Request.java

## Purpose

READLINK request DTO containing only the symlink handle. The source was read as a complete 43-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READLINK3Request extends RequestWithHandle`, `public static READLINK3Request deserialize(XDR xdr) throws IOException`, `public READLINK3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle; serialize writes it unchanged.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

The server must later reject non-symlink handles; this class does not type-check.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READLINK3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/REMOVE3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/REMOVE3Request.java

## Purpose

REMOVE request DTO carrying parent directory handle and filename. The source was read as a complete 53-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class REMOVE3Request extends RequestWithHandle`, `public static REMOVE3Request deserialize(XDR xdr) throws IOException`, `public REMOVE3Request(FileHandle handle, String name)`, `public String getName()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle plus XDR string; serialize writes handle and UTF-8 bytes.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local filename validation; server must reject invalid names or directory targets.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/REMOVE3Request.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RMDIR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RMDIR3Request.java

## Purpose

RMDIR request DTO carrying parent directory handle and directory name. The source was read as a complete 53-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RMDIR3Request extends RequestWithHandle`, `public static RMDIR3Request deserialize(XDR xdr) throws IOException`, `public RMDIR3Request(FileHandle handle, String name)`, `public String getName()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle plus XDR string; serialize writes handle and UTF-8 bytes.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local check for dot/dotdot or empty directory semantics.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RMDIR3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RequestWithHandle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RequestWithHandle.java

## Purpose

Abstract base for requests whose first/primary argument is a FileHandle. The source was read as a complete 35-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public abstract class RequestWithHandle extends NFS3Request`, `public FileHandle getHandle()`.

## Control Flow

Stores a protected final handle and exposes getHandle; subclasses call super(handle) and serialize the handle in their operation-specific order.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Constructor is package-private and does not null-check handle; null handles fail later during serialization.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RequestWithHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SETATTR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SETATTR3Request.java

## Purpose

SETATTR request DTO carrying target handle, SetAttr3, and optional ctime guard. The source was read as a complete 85-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class SETATTR3Request extends RequestWithHandle`, `public static SETATTR3Request deserialize(XDR xdr) throws IOException`, `public SETATTR3Request(FileHandle handle, SetAttr3 attr, boolean check,`, `public SetAttr3 getAttr()`, `public boolean isCheck()`, `public NfsTime getCtime()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, SetAttr3, guard boolean, and ctime when guarded; serialize mirrors it.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `NfsTime`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

If check=true with null ctime, serialize will fail; guard mismatch handling lives in server code.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SETATTR3Request.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/WRITE3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/WRITE3Request.java

## Purpose

WRITE request DTO carrying file handle, offset, count, stable-how policy, and payload ByteBuffer. The source was read as a complete 93-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WRITE3Request extends RequestWithHandle`, `public static WRITE3Request deserialize(XDR xdr) throws IOException`, `public WRITE3Request(FileHandle handle, final long offset, final int count,`, `public long getOffset()`, `public void setOffset(long offset)`, `public int getCount()`, `public void setCount(int count)`, `public WriteStableHow getStableHow()`, `public ByteBuffer getData()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, offset, count, stableHow enum value, then opaque byte payload length; serialize writes count twice per NFS WRITE args and writes data.array().

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `ByteBuffer`, `FileHandle`, `WriteStableHow`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Assumes ByteBuffer has an accessible backing array and that count matches payload length; invalid stableHow values may map to null/throw depending enum helper.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/WRITE3Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/ACCESS3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/ACCESS3Response.java

## Purpose

ACCESS response with post-operation attributes and access bitmask. The source was read as a complete 70-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class ACCESS3Response extends NFS3Response`, `public ACCESS3Response(int status)`, `public ACCESS3Response(int status, Nfs3FileAttributes postOpAttr, int access)`, `public static ACCESS3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK deserialize reads attributes and access; serialize emits a postOpAttr-present boolean and access only on OK.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Failure serialization emits false for attributes, so callers expecting weak cache data on failures must tolerate absence.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/ACCESS3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/COMMIT3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/COMMIT3Response.java

## Purpose

COMMIT response with file WCC data and write verifier. The source was read as a complete 69-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class COMMIT3Response extends NFS3Response`, `public COMMIT3Response(int status)`, `public COMMIT3Response(int status, WccData fileWcc, long verf)`, `public WccData getFileWcc()`, `public long getVerf()`, `public static COMMIT3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always serializes WccData; verifier is serialized only on NFS3_OK.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3Constant`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Default verifier comes from Nfs3Constant.WRITE_COMMIT_VERF; server must keep verifier stable across write/commit semantics.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/COMMIT3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/CREATE3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/CREATE3Response.java

## Purpose

CREATE response with optional object handle, object attributes, and directory WCC. The source was read as a complete 90-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class CREATE3Response extends NFS3Response`, `public CREATE3Response(int status)`, `public CREATE3Response(int status, FileHandle handle,`, `public FileHandle getObjHandle()`, `public Nfs3FileAttributes getPostOpObjAttr()`, `public WccData getDirWcc()`, `public static CREATE3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK it emits handle-present, handle, attr-present, attr, then directory WCC; failures emit directory WCC only.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Mutates null dirWcc to empty WccData during serialize; OK responses require non-null handle/attrs.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/CREATE3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSINFO3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSINFO3Response.java

## Purpose

FSINFO response describing I/O sizes, max file size, timestamp granularity, and filesystem property flags. The source was read as a complete 164-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSINFO3Response extends NFS3Response`, `public FSINFO3Response(int status)`, `public FSINFO3Response(int status, Nfs3FileAttributes postOpAttr, int rtmax,`, `public static FSINFO3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes post-op attributes; on OK writes rtmax/rtpref/rtmult, wtmax/wtpref/wtmult, dtpref, maxFileSize, timeDelta, and properties.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `NfsTime`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

timeDelta must be non-null on OK; deserialize assumes post-op attrs follow after a boolean.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSINFO3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSSTAT3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSSTAT3Response.java

## Purpose

FSSTAT response describing filesystem byte/file-slot capacity and volatility hint. The source was read as a complete 139-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSSTAT3Response extends NFS3Response`, `public FSSTAT3Response(int status)`, `public FSSTAT3Response(int status, Nfs3FileAttributes postOpAttr,`, `public static FSSTAT3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes post-op attributes; on OK writes tbytes/fbytes/abytes/tfiles/ffiles/afiles/invarsec.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Null postOpAttr is normalized to empty attributes during serialization, which can hide missing server metadata.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/FSSTAT3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/GETATTR3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/GETATTR3Response.java

## Purpose

GETATTR response carrying full post-operation attributes on success. The source was read as a complete 58-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class GETATTR3Response extends NFS3Response`, `public GETATTR3Response(int status)`, `public GETATTR3Response(int status, Nfs3FileAttributes attrs)`, `public void setPostOpAttr(Nfs3FileAttributes postOpAttr)`, `public static GETATTR3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize reads attributes only on NFS3_OK; serialize writes attributes only on OK after the RPC accepted header/status.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Failure responses carry no attributes; callers must not assume postOpAttr is populated after deserialize failures.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/GETATTR3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LINK3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LINK3Response.java

## Purpose

LINK response carrying WCC data for source and link directories. The source was read as a complete 62-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class LINK3Response extends NFS3Response`, `public LINK3Response(int status)`, `public LINK3Response(int status, WccData fromDirWcc,`, `public WccData getFromDirWcc()`, `public WccData getLinkDirWcc()`, `public static LINK3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize reads status, fromDirWcc, and linkDirWcc; serialize writes both WCC blocks for all statuses.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Default constructor leaves both WCC blocks empty; server accuracy depends on supplying real pre/post attrs.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LINK3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LOOKUP3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LOOKUP3Response.java

## Purpose

LOOKUP response with resolved file handle, object post-op attrs, and parent directory attrs. The source was read as a complete 77-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class LOOKUP3Response extends NFS3Response`, `public LOOKUP3Response(int status)`, `public LOOKUP3Response(int status, FileHandle fileHandle,`, `public LOOKUP3Response(XDR xdr) throws IOException`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Constructor-from-XDR reads status, optional handle/object attrs on OK, and optional directory attrs; serialize writes corresponding presence booleans.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

serialize emits attr-present booleans based on nullness; OK with null handle/attrs is unsafe.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/LOOKUP3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/MKDIR3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/MKDIR3Response.java

## Purpose

MKDIR response with created directory handle/attrs plus parent directory WCC. The source was read as a complete 86-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class MKDIR3Response extends NFS3Response`, `public MKDIR3Response(int status)`, `public MKDIR3Response(int status, FileHandle handle, Nfs3FileAttributes attr,`, `public FileHandle getObjFileHandle()`, `public Nfs3FileAttributes getObjAttr()`, `public WccData getDirWcc()`, `public static MKDIR3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK it serializes handle-present, handle, attr-present, attrs, then WCC; deserialize mirrors.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

OK response requires non-null created handle and attrs; failure still carries WCC.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/MKDIR3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/MKNOD3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/MKNOD3Response.java

## Purpose

MKNOD response with created object handle/attrs plus parent directory WCC. The source was read as a complete 84-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class MKNOD3Response extends NFS3Response`, `public MKNOD3Response(int status)`, `public MKNOD3Response(int status, FileHandle handle,`, `public FileHandle getObjFileHandle()`, `public Nfs3FileAttributes getObjPostOpAttr()`, `public WccData getDirWcc()`, `public static MKNOD3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK it serializes handle/attrs presence and values; always serializes dirWcc.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Same null-safety concerns as MKDIR/SYMLINK OK responses.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/MKNOD3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/NFS3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/NFS3Response.java

## Purpose

Base class for NFSv3 responses, holding numeric NFS status. The source was read as a complete 57-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class NFS3Response`, `public NFS3Response(int status)`, `public int getStatus()`, `public void setStatus(int status)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

serialize creates an ONC RPC accepted reply with xid/verifier, writes reply header, then writes status.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `RpcAcceptedReply`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Subclasses must call super.serialize first or the wire reply lacks RPC framing/status.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/NFS3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/PATHCONF3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/PATHCONF3Response.java

## Purpose

PATHCONF response with path configuration limits and case/link/chown booleans. The source was read as a complete 119-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class PATHCONF3Response extends NFS3Response`, `public PATHCONF3Response(int status)`, `public PATHCONF3Response(int status, Nfs3FileAttributes postOpAttr,`, `public static PATHCONF3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes post-op attrs; on OK writes linkMax, nameMax, noTrunc, chownRestricted, caseInsensitive, casePreserving.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Deserialize reads a boolean and attrs before status-specific fields, assuming the attribute block is present.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/PATHCONF3Response.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READLINK3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READLINK3Response.java

## Purpose

READLINK response with symlink attrs and target path opaque bytes. The source was read as a complete 67-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READLINK3Response extends NFS3Response`, `public READLINK3Response(int status)`, `public READLINK3Response(int status, Nfs3FileAttributes postOpAttr,`, `public static READLINK3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes symlink post-op attrs; on OK writes variable opaque path bytes.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Constructor defensively copies path, but null path input would fail.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/READLINK3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/REMOVE3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/REMOVE3Response.java

## Purpose

REMOVE response carrying parent directory WCC. The source was read as a complete 53-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class REMOVE3Response extends NFS3Response`, `public REMOVE3Response(int status)`, `public REMOVE3Response(int status, WccData dirWcc)`, `public static REMOVE3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize reads status then WccData; serialize normalizes null WCC to empty and writes it.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Empty default WCC is protocol-shaped but may reduce client cache consistency if real attrs are unavailable.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/REMOVE3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RENAME3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RENAME3Response.java

## Purpose

RENAME response carrying source and destination directory WCC. The source was read as a complete 62-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RENAME3Response extends NFS3Response`, `public RENAME3Response(int status)`, `public RENAME3Response(int status, WccData fromWccData, WccData toWccData)`, `public WccData getFromDirWcc()`, `public WccData getToDirWcc()`, `public static RENAME3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize/serialize status plus fromDirWcc and toDirWcc for all outcomes.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Both WCC blocks should reflect pre/post states, especially same-directory renames.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RENAME3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RMDIR3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RMDIR3Response.java

## Purpose

RMDIR response carrying parent directory WCC. The source was read as a complete 54-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RMDIR3Response extends NFS3Response`, `public RMDIR3Response(int status)`, `public RMDIR3Response(int status, WccData wccData)`, `public WccData getDirWcc()`, `public static RMDIR3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize reads status then WccData; serialize writes status and WCC.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Default empty WCC reduces cache invalidation precision.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/RMDIR3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SETATTR3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SETATTR3Response.java

## Purpose

SETATTR response carrying target WCC. The source was read as a complete 54-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class SETATTR3Response extends NFS3Response`, `public SETATTR3Response(int status)`, `public SETATTR3Response(int status, WccData wccData)`, `public WccData getWccData()`, `public static SETATTR3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

deserialize reads status then WccData; serialize writes WCC after base status.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Server must populate WCC on both success and guarded failure for client cache correctness.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SETATTR3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SYMLINK3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SYMLINK3Response.java

## Purpose

SYMLINK response with created symlink handle/attrs plus directory WCC. The source was read as a complete 87-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class SYMLINK3Response extends NFS3Response`, `public SYMLINK3Response(int status)`, `public SYMLINK3Response(int status, FileHandle handle,`, `public FileHandle getObjFileHandle()`, `public Nfs3FileAttributes getObjPostOpAttr()`, `public WccData getDirWcc()`, `public static SYMLINK3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

On OK writes handle-present, handle, attr-present, attrs, then dirWcc; failures write only dirWcc.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`, `Nfs3FileAttributes`, `Nfs3Status`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

OK requires non-null handle/attrs; errors still need accurate dirWcc.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/SYMLINK3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WRITE3Response.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WRITE3Response.java

## Purpose

WRITE response with file WCC, committed byte count, stability mode, and verifier. The source was read as a complete 88-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WRITE3Response extends NFS3Response`, `public WRITE3Response(int status)`, `public WRITE3Response(int status, WccData fileWcc, int count,`, `public int getCount()`, `public WriteStableHow getStableHow()`, `public long getVerifer()`, `public static WRITE3Response deserialize(XDR xdr)`, `public XDR serialize(XDR out, int xid, Verifier verifier)`.

## Control Flow

Always writes WCC; on OK writes count, stableHow value, and verifier.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3Constant`, `Nfs3Status`, `WriteStableHow`, `XDR`, `Verifier`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Field/getter typo `verifer`/`getVerifer`; deserialize uses WriteStableHow.values()[how], so invalid wire enum can throw.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WRITE3Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccAttr.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccAttr.java

## Purpose

Weak-cache-consistency pre-operation attribute tuple: size, mtime, ctime. The source was read as a complete 73-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WccAttr`, `public long getSize()`, `public NfsTime getMtime()`, `public NfsTime getCtime()`, `public WccAttr()`, `public WccAttr(long size, NfsTime mtime, NfsTime ctime)`, `public static WccAttr deserialize(XDR xdr)`, `public void serialize(XDR out)`.

## Control Flow

deserialize reads size hyper plus two NfsTime values; serialize writes zeros for null times.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `NfsTime`, `XDR`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

serialize mutates null mtime/ctime to zero timestamps, masking missing pre-op times.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccAttr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccData.java

## Purpose

Weak-cache-consistency container pairing pre-op WccAttr and post-op Nfs3FileAttributes. The source was read as a complete 66-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WccData`, `public WccAttr getPreOpAttr()`, `public void setPreOpAttr(WccAttr preOpAttr)`, `public Nfs3FileAttributes getPostOpAttr()`, `public void setPostOpAttr(Nfs3FileAttributes postOpAttr)`, `public WccData(WccAttr preOpAttr, Nfs3FileAttributes postOpAttr)`, `public static WccData deserialize(XDR xdr)`, `public void serialize(XDR out)`.

## Control Flow

Constructor normalizes nulls to empty objects; serialize always writes both presence booleans as true and both attribute blocks.

## State and Persistence Behavior

Instances are in-memory RPC result holders. Persistent effects are represented indirectly through returned attributes, WCC data, verifiers, and opaque payloads produced by the server/filesystem layer.

## Dependencies and Integration Points

Direct dependencies include `Nfs3FileAttributes`, `XDR`. Integration points are `NFS3Response` RPC framing, `XDR`, `Verifier`, NFS status constants, file attributes, file handles, and weak cache consistency helpers.

## Risks and Edge Cases

Protocol cannot represent absent WCC via this class once constructed; clients may see default attrs instead of no attrs.

## Test Signals

Useful tests are success/failure XDR round-trips, null/default attribute behavior, WCC presence checks, invalid enum/boolean stream handling, and integration tests against NFSv3 client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/response/WccData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsExports.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsExports.java

## Purpose

JUnit 5 tests for `NfsExports` host/address matcher parsing, privilege selection, and cache expiry. The source was read as a complete 222-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class TestNfsExports`, `public void testWildcardRW()`, `public void testWildcardRO()`, `public void testExactAddressRW()`, `public void testExactAddressRO()`, `public void testExactHostRW()`, `public void testExactHostRO()`, `public void testCidrShortRW()`, `public void testCidrShortRO()`, `public void testCidrLongRW()`.

## Control Flow

Each test constructs `NfsExports` with wildcard, exact address/host, CIDR, regex, grouped regex, or multiple matcher strings and asserts `AccessPrivilege`; invalid syntax tests assert IllegalArgumentException.

## State and Persistence Behavior

Test-only state is local to each test method. No persistent files are created.

## Dependencies and Integration Points

Direct dependencies include `Nfs3Constant`, `Assertions`, `Test`. Integration points are JUnit 5, AssertJ where used, and the Hadoop NFS classes under test.

## Risks and Edge Cases

`testMultiMatchers` sleeps and polls around cache expiration, so it can be timing-sensitive on slow CI; hostname regex cache behavior is intentionally asserted.

## Test Signals

This file itself is a test signal; additional coverage should include negative/malformed XDR and more edge cases around cache expiry or file handle contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsExports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsTime.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsTime.java

## Purpose

JUnit 5 tests for `NfsTime` millisecond-to-second/nanosecond conversion and XDR round-trip equality. The source was read as a complete 46-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class TestNfsTime`, `public void testConstructor()`, `public void testSerializeDeserialize()`.

## Control Flow

Constructs `NfsTime(1001)`, checks seconds/nseconds, serializes to XDR, deserializes from read-only wrapper, and asserts equality.

## State and Persistence Behavior

Test-only state is local to each test method. No persistent files are created.

## Dependencies and Integration Points

Direct dependencies include `Assertions`, `XDR`, `Test`. Integration points are JUnit 5, AssertJ where used, and the Hadoop NFS classes under test.

## Risks and Edge Cases

Coverage is narrow but protects the time encoding consumed by NFS attrs and WCC structures.

## Test Signals

This file itself is a test signal; additional coverage should include negative/malformed XDR and more edge cases around cache expiry or file handle contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsTime.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/nfs3/TestFileHandle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/nfs3/TestFileHandle.java

## Purpose

JUnit test for `FileHandle` construction and XDR serialization/deserialization. The source was read as a complete 39-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class TestFileHandle`, `public void testConstructor()`.

## Control Flow

Creates a FileHandle with id 1024, serializes it, deserializes into a new handle, and asserts the file id remains 1024.

## State and Persistence Behavior

Test-only state is local to each test method. No persistent files are created.

## Dependencies and Integration Points

Direct dependencies include `XDR`, `Test`, `assertThat`. Integration points are JUnit 5, AssertJ where used, and the Hadoop NFS classes under test.

## Risks and Edge Cases

The final assertion checks the original handle id rather than handle2, so the intended round-trip assertion appears incomplete.

## Test Signals

This file itself is a test signal; additional coverage should include negative/malformed XDR and more edge cases around cache expiry or file handle contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/nfs3/TestFileHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/dev-support/findbugs-exclude.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/dev-support/findbugs-exclude.xml

## Purpose

SpotBugs/FindBugs exclusion filter for selected RegistryDNS methods. The source was read as a complete 33-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: No public callable members beyond constants/package documentation..

## Control Flow

Suppresses RV_RETURN_VALUE_IGNORED_BAD_PRACTICE for addNIOTCP, addNIOUDP, and serveNIOTCP.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Suppressions can hide real ignored-return bugs if methods evolve; keep class/method names synchronized.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/dev-support/findbugs-exclude.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/pom.xml

## Purpose

Maven module descriptor for hadoop-registry. The source was read as a complete 338-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: No public callable members beyond constants/package documentation..

## Control Flow

Declares dependencies on Hadoop common/auth, ZooKeeper/Curator, commons libs, Jackson, dnsjava, metrics, Snappy, JUnit; configures resources, SpotBugs exclusions, RAT, version-info, test-jar, Surefire env/system properties, and dist assembly profile.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Build/test behavior depends on inherited properties and test environment variables; SpotBugs filter and Surefire excludes are integration-sensitive.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/cli/RegistryCli.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/cli/RegistryCli.java

## Purpose

Command-line Tool for registry ls, resolve, bind, mknode, and rm operations. The source was read as a complete 496-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryCli extends Configured implements Tool, Closeable`, `public RegistryCli(PrintStream sysout, PrintStream syserr)`, `public RegistryCli(RegistryOperations reg,`, `public static void main(String[] args) throws Exception`, `public void close() throws IOException`, `public int run(String[] args) throws Exception`, `public int ls(String[] args)`, `public int resolve(String[] args)`, `public int bind(String[] args)`, `public int mknode(String[] args)`.

## Control Flow

Constructs/starts RegistryOperations, parses commons-cli options, builds ServiceRecord endpoints, validates absolute paths, invokes registry operations, and maps exceptions to user messages.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `*`, `Closeable`, `IOException`, `PrintStream`, `URI`, `URISyntaxException`, `List`, `Map`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Uses deprecated GnuParser; bind always overwrites; main terminates via ExitUtil; option parsing relies on exact arg positions.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/cli/RegistryCli.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/BindFlags.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/BindFlags.java

## Purpose

Public constants for registry bind semantics. The source was read as a complete 41-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public interface BindFlags`.

## Control Flow

Defines CREATE=0 and OVERWRITE=1 flags consumed by RegistryOperations.bind implementations.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Because CREATE is zero, missing flags and create-only are indistinguishable; overwrite must be explicitly ORed.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/BindFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperations.java

## Purpose

Service-lifecycle interface for DNS registration/removal based on registry ServiceRecord values. The source was read as a complete 60-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public interface DNSOperations extends Service`.

## Control Flow

register(path, record) and delete(path, record) are the primary operations and may throw IOException.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `ServiceRecord`, `Service`, `IOException`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Actual DNS persistence/lifecycle is implementation-defined; interface does not validate record content.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperationsFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperationsFactory.java

## Purpose

Factory for DNSOperations implementations. The source was read as a complete 78-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public final class DNSOperationsFactory implements RegistryConstants`, `public enum DNSImplementation`, `public static DNSOperations createInstance(Configuration conf)`, `public static DNSOperations createInstance(String name,`.

## Control Flow

createInstance validates non-null Configuration and currently instantiates RegistryDNS for DNSJAVA.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `Configuration`, `RegistryDNS`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

The operations.init(conf) call is commented out, so callers must know whether returned services need explicit init before start.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperationsFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryConstants.java

## Purpose

Central registry/DNS/ZooKeeper configuration key and default-value contract. The source was read as a complete 388-line file for this research item.

## Important APIs, Types, and Functions

Defines configuration/path constants such as `KEY_DNS_ENABLED`, `DEFAULT_DNS_ENABLED`, `KEY_DNS_DOMAIN`, `KEY_DNS_BIND_ADDRESS`, `KEY_DNS_PORT`, `DEFAULT_DNS_PORT`, `KEY_DNSSEC_ENABLED`, `KEY_DNSSEC_PUBLIC_KEY`, `KEY_DNSSEC_PRIVATE_KEY_FILE`, `DEFAULT_DNSSEC_PRIVATE_KEY_FILE`, `KEY_DNS_ZONE_SUBNET`, `KEY_DNS_ZONE_MASK`, `KEY_DNS_ZONE_IP_MIN`, `KEY_DNS_ZONE_IP_MAX`, and more.

## Control Flow

Includes prefixes, DNS bind/zone/DNSSEC keys, registry security/auth keys, ZK quorum/retry/session keys, ACL defaults, and canonical path fragments.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Key stability is high-risk because configs, tests, and deployed clusters depend on literal strings.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperations.java

## Purpose

Public registry service API for path creation, binding, resolving, stat/list/delete, existence, and write-accessor management. The source was read as a complete 182-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public interface RegistryOperations extends Service`, `public void clearWriteAccessors();`.

## Control Flow

Extends Hadoop Service; methods define checked exceptions for missing paths, invalid records, non-empty directories, and auth/write-accessor operations.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `FileAlreadyExistsException`, `PathIsNotEmptyDirectoryException`, `PathNotFoundException`, `Service`, `InvalidPathnameException`, `InvalidRecordException`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Implementations must preserve path and overwrite semantics or callers like RegistryCli and RegistryUtils will report misleading errors.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperationsFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperationsFactory.java

## Purpose

Factory for authenticated/anonymous/Kerberos registry clients. The source was read as a complete 160-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public final class RegistryOperationsFactory`, `public static RegistryOperations createInstance(Configuration conf)`, `public static RegistryOperations createInstance(String name, Configuration conf)`, `public static RegistryOperationsClient createClient(String name,`, `public static RegistryOperations createAnonymousInstance(Configuration conf)`, `public static RegistryOperations createKerberosInstance(Configuration conf,`, `public static RegistryOperations createKerberosInstance(Configuration conf,`, `public static RegistryOperations createAuthenticatedInstance(Configuration conf,`.

## Control Flow

Creates RegistryOperationsClient, sets auth-related Configuration keys, validates digest id/password, initializes clients, and converts ServiceStateException causes to RuntimeException.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `StringUtils`, `Configuration`, `ServiceStateException`, `RegistryOperationsClient`, `*`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

It mutates the caller-provided Configuration; missing digest credentials fail fast with IllegalArgumentException.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperationsFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/package-info.java

## Purpose

Package documentation for public registry client APIs. The source was read as a complete 35-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: No public callable members beyond constants/package documentation..

## Control Flow

No runtime control flow; JavaDoc groups RegistryOperations, DNS operations, factories, constants, and bind flags.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Risk is documentation drift with the evolving public API.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/JsonSerDeser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/JsonSerDeser.java

## Purpose

JSON byte marshaller/unmarshaller for registry records. The source was read as a complete 117-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class JsonSerDeser<T> extends JsonSerialization<T>`, `public JsonSerDeser(Class<T> classType)`, `public T fromBytes(String path, byte[] bytes) throws IOException`, `public T fromBytes(String path, byte[] bytes, String marker)`.

## Control Flow

Extends JsonSerialization<T>; fromBytes rejects null/empty payloads with NoRecordException, decodes UTF-8, parses JSON, and wraps JsonProcessingException as InvalidRecordException.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `JsonProcessingException`, `StringUtils`, `InterfaceAudience`, `InterfaceStability`, `InvalidRecordException`, `NoRecordException`, `JsonSerialization`, `EOFException`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

String marker parameter is unused beyond signature; invalid charset is not expected because StandardCharsets.UTF_8 is fixed.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/JsonSerDeser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryPathUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryPathUtils.java

## Purpose

Static helpers for validating, joining, splitting, encoding, and inspecting registry paths. The source was read as a complete 237-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryPathUtils`, `public static String validateZKPath(String path) throws`, `public static String validateElementsAsDNS(String path) throws`, `public static String createFullPath(String base, String path) throws`, `public static String join(String base, String path)`, `public static List<String> split(String path)`, `public static String lastPathEntry(String path)`, `public static String parentOf(String path) throws PathNotFoundException`, `public static String encodeForRegistry(String element)`, `public static String encodeYarnID(String yarnId)`.

## Control Flow

validateZKPath delegates to ZooKeeper PathUtils; validateElementsAsDNS checks each element with IDN conversion and DNS label regex; join normalizes slashes; parentOf rejects root/no-parent cases.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `InterfaceAudience`, `InterfaceStability`, `PathNotFoundException`, `InvalidPathnameException`, `RegistryInternalConstants`, `PathUtils`, `IDN`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Path conversion uses punycode and regex constraints; edge cases include root paths, trailing slashes, and non-ASCII usernames.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryPathUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryTypeUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryTypeUtils.java

## Purpose

Static helpers for building and validating ServiceRecord Endpoint objects. The source was read as a complete 291-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryTypeUtils`, `public static Endpoint urlEndpoint(String api,`, `public static Endpoint restEndpoint(String api,`, `public static Endpoint webEndpoint(String api,`, `public static Endpoint inetAddrEndpoint(String api,`, `public static Endpoint ipcEndpoint(String api, InetSocketAddress address)`, `public static Map<String, String> map(String key, String val)`, `public static Map<String, String> uri(String uri)`, `public static Map<String, String> hostnamePortPair(String hostname, int port)`, `public static Map<String, String> hostnamePortPair(InetSocketAddress address)`.

## Control Flow

Creates URL/REST/web/inet/ipc endpoints, address maps, URI lists, URL conversions, and validates ServiceRecord/Endpoint instances.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `InterfaceAudience`, `InterfaceStability`, `InvalidRecordException`, `Endpoint`, `ProtocolTypes`, `ServiceRecord`, `InetSocketAddress`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Validation catches endpoint shape but not service reachability; malformed URI/URL values surface when retrieval helpers parse them.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryTypeUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryUtils.java

## Purpose

Higher-level registry path/user and record extraction utilities. The source was read as a complete 398-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryUtils`, `public static String homePathForUser(String username)`, `public static String convertUsername(String username)`, `public static String serviceclassPath(String user,`, `public static String servicePath(String user,`, `public static String componentListPath(String user,`, `public static String componentPath(String user,`, `public static Map<String, ServiceRecord> listServiceRecords(`, `public static Map<String, RegistryPathStatus> statChildren(`, `public static String homePathForCurrentUser()`.

## Control Flow

Builds user/service/component paths, converts Kerberos/user names, honors HADOOP_USER_NAME in insecure mode, stats child paths, resolves service records, and skips EOF/invalid/no-record children.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `VisibleForTesting`, `Preconditions`, `StringUtils`, `InterfaceAudience`, `InterfaceStability`, `PathNotFoundException`, `UserGroupInformation`, `RegistryConstants`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

List/extract operations are non-atomic and tolerate deleted/invalid children; username conversion affects DNS-safe service discovery names.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/package-info.java

## Purpose

Package documentation for registry binding utilities. The source was read as a complete 22-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: No public callable members beyond constants/package documentation..

## Control Flow

No runtime control flow; marks the namespace for path, type, JSON, and higher-level utility helpers.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Risk is documentation drift only.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/AuthenticationFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/AuthenticationFailedException.java

## Purpose

RegistryIOException subtype for invalid or incomplete credentials. The source was read as a complete 39-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class AuthenticationFailedException extends RegistryIOException`, `public AuthenticationFailedException(String path, Throwable cause)`, `public AuthenticationFailedException(String path, String error)`, `public AuthenticationFailedException(String path,`.

## Control Flow

Provides path/cause, path/error, and path/error/cause constructors.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Mostly used for precise CLI/user diagnostics rather than unique behavior.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/AuthenticationFailedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidPathnameException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidPathnameException.java

## Purpose

RegistryIOException subtype for invalid registry path strings. The source was read as a complete 40-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class InvalidPathnameException extends RegistryIOException`, `public InvalidPathnameException(String path, String message)`, `public InvalidPathnameException(String path,`.

## Control Flow

Constructors preserve the failing path plus message/cause.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Should be thrown after path validation helpers rather than generic IllegalArgumentException for user-facing operations.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidPathnameException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidRecordException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidRecordException.java

## Purpose

RegistryIOException subtype for malformed service record data. The source was read as a complete 41-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class InvalidRecordException extends RegistryIOException`, `public InvalidRecordException(String path, String error)`, `public InvalidRecordException(String path,`.

## Control Flow

Constructors preserve path plus parse/validation detail.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Used by JSON and endpoint validators; broad catches may hide corrupt registry data if only logged.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidRecordException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoChildrenForEphemeralsException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoChildrenForEphemeralsException.java

## Purpose

RegistryIOException subtype exposing ZooKeeper ephemeral-node child restrictions. The source was read as a complete 48-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class NoChildrenForEphemeralsException extends RegistryIOException`, `public NoChildrenForEphemeralsException(String path, Throwable cause)`, `public NoChildrenForEphemeralsException(String path, String error)`, `public NoChildrenForEphemeralsException(String path,`.

## Control Flow

Constructors mirror other registry exceptions.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Can appear if external ZK manipulation creates a shape the registry API normally avoids.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoChildrenForEphemeralsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoPathPermissionsException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoPathPermissionsException.java

## Purpose

RegistryIOException subtype for path permission failures. The source was read as a complete 45-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class NoPathPermissionsException extends RegistryIOException`, `public NoPathPermissionsException(String path, Throwable cause)`, `public NoPathPermissionsException(String path, String error)`, `public NoPathPermissionsException(String path, String error, Throwable cause)`, `public NoPathPermissionsException(String message,`.

## Control Flow

Supports path/cause, path/error, path/error/cause, and wrapping PathIOException while preserving path.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `PathIOException`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Class comment is incomplete; behavior relies on PathIOException formatting.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoPathPermissionsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoRecordException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoRecordException.java

## Purpose

RegistryIOException subtype for paths without a valid ServiceRecord payload. The source was read as a complete 45-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class NoRecordException extends RegistryIOException`, `public NoRecordException(String path, String error)`, `public NoRecordException(String path,`.

## Control Flow

Constructors preserve path and error/cause.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `ServiceRecord`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

A path may exist and still raise this if data is too short or not a ServiceRecord.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoRecordException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/RegistryIOException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/RegistryIOException.java

## Purpose

Base checked exception for registry I/O failures with path context. The source was read as a complete 58-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryIOException extends PathIOException`, `public RegistryIOException(String message, PathIOException cause)`, `public RegistryIOException(String path, Throwable cause)`, `public RegistryIOException(String path, String error)`, `public RegistryIOException(String path, String error, Throwable cause)`.

## Control Flow

Extends PathIOException and can wrap another PathIOException while propagating its path.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `PathIOException`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Correct path propagation is important for CLI diagnostics and automated cleanup.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/RegistryIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/package-info.java

## Purpose

Package documentation for registry-specific exceptions. The source was read as a complete 33-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: No public callable members beyond constants/package documentation..

## Control Flow

No runtime control flow; documents that exceptions derive from RegistryIOException and may be accompanied by other IO/runtime exceptions.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Risk is documentation drift with the exception hierarchy.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/FSRegistryOperationsService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/FSRegistryOperationsService.java

## Purpose

Filesystem-backed RegistryOperations implementation using `_record` files under directories. The source was read as a complete 248-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSRegistryOperationsService extends CompositeService`, `public FSRegistryOperationsService()`, `public FileSystem getFs()`, `protected void serviceInit(Configuration conf)`, `public boolean mknode(String path, boolean createParents)`, `public void bind(String path, ServiceRecord record, int flags)`, `public ServiceRecord resolve(String path) throws PathNotFoundException,`, `public RegistryPathStatus stat(String path)`, `public boolean exists(String path) throws IOException`, `public List<String> list(String path)`.

## Control Flow

serviceInit obtains FileSystem; mknode creates directories; bind writes marshalled ServiceRecord to path/_record with overwrite semantics; resolve reads/parses/validates; stat/list/delete map registry paths to FS operations.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `File`, `FileNotFoundException`, `IOException`, `ArrayList`, `List`, `NotImplementedException`, `Configuration`, `FSDataInputStream`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

No registry-specific ACL support; addWriteAccessor/clearWriteAccessors throw NotImplementedException; stat requires `_record`, so empty nodes may not stat like ZK nodes.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/FSRegistryOperationsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/RegistryOperationsClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/RegistryOperationsClient.java

## Purpose

ZooKeeper-backed registry client service facade. The source was read as a complete 55-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryOperationsClient extends RegistryOperationsService`, `public RegistryOperationsClient(String name)`, `public RegistryOperationsClient(String name,`.

## Control Flow

Constructors delegate to RegistryOperationsService with optional RegistryBindingSource.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `RegistryBindingSource`, `RegistryOperationsService`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Behavior is inherited; risks are in external ZK auth/session configuration rather than this wrapper.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/RegistryOperationsClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/package-info.java

## Purpose

Package documentation for registry client service implementations. The source was read as a complete 26-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: No public callable members beyond constants/package documentation..

## Control Flow

No runtime control flow; identifies implementations as Hadoop/YARN lifecycle services implementing RegistryOperations.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Risk is documentation drift with implementation classes.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/BindingInformation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/BindingInformation.java

## Purpose

Mutable data holder returned by RegistryBindingSource for ZooKeeper binding diagnostics. The source was read as a complete 41-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class BindingInformation`.

## Control Flow

Public fields hold Curator EnsembleProvider and a description string.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `EnsembleProvider`, `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

No validation or immutability; callers must populate both fields consistently.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/BindingInformation.java -->
