<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file_test.go -->
## sources/control-plane/ceph-csi/internal/util/file/file_test.go

**Purpose:** Validates temp file content persistence and sparse file sizing behavior.

**Important APIs and functions:** `TestCreateTempFile_WithValidContent`, `_WithEmptyContent`, and `_WithLargeContent` read back created temp files. `TestCreateSparseFile` checks a 10 MiB sparse file and expects errors for zero and negative sizes.

**Control flow, state, and persistence:** Tests create temporary files and remove temp files explicitly where needed. Parallel subtests are used for independent cases.

**Dependencies and integration points:** Uses standard `os` and `testing`. It protects helper behavior used by cryptsetup passphrase file handling and sparse-device style tests.

**Risks and test signals:** It does not check file permissions, closed-file behavior, sync failures, or whether sparse allocation actually avoids disk blocks. It also leaves `CreateSparseFile` temp files to `t.TempDir` cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/file/file_test.go -->
