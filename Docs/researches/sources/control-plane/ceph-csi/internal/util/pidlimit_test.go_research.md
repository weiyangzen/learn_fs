<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit_test.go -->
## sources/control-plane/ceph-csi/internal/util/pidlimit_test.go

**Purpose:** Provides an opt-in test for PID limit reading and privileged write behavior.

**Important APIs and functions:** `TestGetPIDLimit` checks `CEPH_CSI_RUN_ALL_TESTS`, calls `GetPIDLimit`, asserts nonzero, attempts `SetPIDLimit(4096)`, and restores the previous value if setting succeeds.

**Control flow, state, and persistence:** The test is skipped by default because it needs root permissions and cgroup support. When enabled, it mutates the process cgroup PID limit and tries to restore it.

**Dependencies and integration points:** Uses `os.Getenv` and standard testing. It validates host/container integration rather than pure unit behavior.

**Risks and test signals:** Useful but intentionally limited. If restoration fails after a successful set, the test only logs. It does not test cgroup path parsing with fixtures or v1/v2 variants deterministically.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit_test.go -->
