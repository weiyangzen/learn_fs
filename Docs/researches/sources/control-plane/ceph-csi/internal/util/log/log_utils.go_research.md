<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils.go -->
## sources/control-plane/ceph-csi/internal/util/log/log_utils.go

**Purpose:** Provides a helper to gzip-compress a log file and replace the `.log` file with a `.gz` file.

**Important APIs and functions:** `GzipLogFile(pathToFile)` reads the full file, replaces all `.log` substrings in the path with `.gz`, writes gzip content to a created/truncated file, and removes the original on success.

**Control flow, state, and persistence:** The function mutates filesystem state by creating/truncating the compressed file and deleting the original. If gzip writing fails, it removes the new file and leaves the original. Deferred close errors are ignored.

**Dependencies and integration points:** Depends on `compress/gzip`, `os`, and `strings`. It integrates with log rotation or cleanup paths.

**Risks and test signals:** It reads the whole log into memory and uses `strings.ReplaceAll`, so directory names containing `.log` also change. It does not explicitly close the gzip writer before deleting the original except via defer after return path starts, but deferred close happens before function returns. Tests cover existence of the `.gz` output only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils.go -->
