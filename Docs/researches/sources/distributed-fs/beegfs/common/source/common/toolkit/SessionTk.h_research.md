<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SessionTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/SessionTk.h

**Purpose:** Provides static helpers for BeeGFS storage-session file handle IDs and conversion from BeeGFS access flags to POSIX open flags.

**Important APIs/types/functions:** `fileIDFromHandleID`, `ownerFDFromHandleID`, `generateFileHandleID`, and `sysOpenFlagsFromFhgfsAccessFlags`.

**Control flow:** Handle IDs are encoded as `<ownerFDHex>#<fileID>`. Parsing locates `#`; missing separators return the original handle as file ID or owner fd `0`. Access flag conversion starts with `O_LARGEFILE`, picks read/write mode from BeeGFS flags, and adds direct, sync, and nonblocking flags when requested.

**State and persistence behavior:** Stateless string/flag transformation. The handle ID string is part of session-level protocol/state elsewhere but not persisted here.

**Dependencies and integration points:** Uses `StorageDefinitions` access flag constants, `StringTk` hex conversion, and POSIX open flag constants. Comments note this is not for metadata servers, which should use `EntryInfo`.

**Risks:** Malformed handle IDs degrade silently. If multiple access mode bits are set, read-write wins over write-only. `O_DIRECT` imposes alignment constraints not handled here.

**Test signals:** Useful tests would cover malformed IDs, hex owner parsing, all access flag combinations, and compatibility with session backup/restore logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SessionTk.h -->
