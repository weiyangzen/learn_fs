<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds_test.go -->
## sources/control-plane/ceph-csi/internal/util/cephcmds_test.go

**Purpose:** Unit-tests the timeout command runner for successful command output and process termination on timeout.

**Important APIs and functions:** `TestExecCommandWithTimeout` runs `echo hello` with a one-second timeout and `sleep 3` with a one-second timeout, then checks stdout, error presence, and `errors.Is(err, context.DeadlineExceeded)`.

**Control flow, state, and persistence:** The test is table-driven and parallelized. It executes real local programs but does not touch Ceph state or persistent files.

**Dependencies and integration points:** Depends on standard `context`, `errors`, `testing`, and `time`. It protects callers that rely on timeout errors being wrap-detectable and stdout being returned.

**Risks and test signals:** The test assumes POSIX `echo` and `sleep` are available. It does not cover stderr inclusion, command-not-found, logging suppression for `context.TODO`, caller context cancellation, or secret stripping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cephcmds_test.go -->
