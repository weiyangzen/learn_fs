<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils_test.go -->
## sources/control-plane/ceph-csi/internal/util/log/log_utils_test.go

**Purpose:** Tests that `GzipLogFile` creates a compressed replacement file.

**Important APIs and functions:** `TestGzipLogFile` creates a temp `rbd-*.log`, calls `GzipLogFile`, computes the `.gz` path with the same replacement logic, and checks that it exists.

**Control flow, state, and persistence:** Uses a temp directory and filesystem state cleaned by the test framework. It does not write content into the log before compression.

**Dependencies and integration points:** Uses standard `os`, `strings`, `errors`, and testing. It validates basic log utility output creation.

**Risks and test signals:** Minimal signal: it does not assert original removal, gzip validity, content round-trip, write failure cleanup, or path replacement edge cases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log_utils_test.go -->
