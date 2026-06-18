<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file.go -->
## sources/control-plane/ceph-csi/internal/util/file/file.go

**Purpose:** Provides small filesystem helpers for cryptsetup tests and runtime key handling: synced temp file creation and sparse file sizing.

**Important APIs and functions:** `CreateTempFile(prefix, contents)` creates a temp file in the system temp directory, writes the full string, syncs, closes, and returns the file handle for its name. `CreateSparseFile(file, sizeMB)` seeks to `sizeMB*MiB - 1` and writes one zero byte.

**Control flow, state, and persistence:** Temp files persist until callers remove them. On write/sync error, `CreateTempFile` closes and removes the temp file. Sparse file creation mutates the provided open file and returns errors for invalid seek/write cases such as zero or negative sizes.

**Dependencies and integration points:** Depends on `os` and `fmt`. `cryptsetup.AddKey`, `RemoveKey`, and `VerifyKey` use temp files to pass passphrases to cryptsetup.

**Risks and test signals:** `CreateTempFile` returns a closed `*os.File`; callers should mainly use `Name`. The write-short error wraps `err`, which can be nil if the count mismatches without an error. Temp files may hold secrets and must be removed by callers. Tests cover valid/empty/large contents and sparse file sizing/error cases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file.go -->
