<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.cpp

**Purpose:** Implements atomic-ish file replacement by writing content to a temporary file, fsyncing it, renaming it over the final path, and fsyncing the containing directory.

**Important APIs/types/functions:** `TempFileTk::storeTmpAndMove(const std::string&, const void*, size_t)` plus vector and string overloads.

**Control flow:** Builds `filename + ".tmp-XXXXXX"`, opens with `mkstemp`, registers a local cleanup object to unlink the temp file on error, writes until all bytes are written, fsyncs the temp file, renames it to the final filename, disables cleanup, then opens and fsyncs the directory. Directory fsync failure is logged as a warning but returns success.

**State and persistence behavior:** Persists caller-provided bytes to the target path using rename replacement. It avoids leaving partial final files and removes temp files on most error paths.

**Dependencies and integration points:** Used by `StorageTk` for format files and ID/token files. Depends on `FDHandle`, BeeGFS logging and error conversion, `mkstemp`, `write`, `fsync`, `rename`, `dirname`, and directory `open`.

**Risks:** Vector/string overloads use `&contents[0]`, which is undefined for empty vectors/strings in older C++ assumptions even though size is zero. A zero-byte `write` result would spin because only `-1` is treated as failure. File permissions come from `mkstemp` defaults. Directory fsync warning is accepted to avoid rollback complexity.

**Test signals:** Indirectly covered by storage ID/format operations if present. Dedicated tests should cover empty content, rename failure, cleanup of temp files, and crash-consistency expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TempFileTk.cpp -->
