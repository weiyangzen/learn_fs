<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.h

**Purpose:** Declares the `TempFileTk` namespace API for durable temporary-file replacement writes.

**Important APIs/types/functions:** Three overloads of `storeTmpAndMove`: raw pointer/size, `std::vector<char>`, and `std::string`.

**Control flow:** Header-only behavior is limited to declarations; implementation handles temp file creation, write, fsync, rename, and directory fsync.

**State and persistence behavior:** The API persists bytes to the requested filename via replacement. Return value is `FhgfsOpsErr`, allowing callers to map storage/config write failures.

**Dependencies and integration points:** Includes `StorageErrors`. Used by storage format and ID helpers where partial writes would corrupt startup state.

**Risks:** Callers must pass valid buffers for raw pointer calls and handle non-success return codes. The API does not expose file mode or fsync policy knobs.

**Test signals:** Tests should verify the overloads produce identical file contents and propagate errors from unwritable directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.h -->
