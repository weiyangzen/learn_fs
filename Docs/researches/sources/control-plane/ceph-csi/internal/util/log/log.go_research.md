<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log.go -->
## sources/control-plane/ceph-csi/internal/util/log/log.go

**Purpose:** Provides Ceph-CSI logging helpers over `k8s.io/klog/v2`, adding request context prefixes and named verbosity levels.

**Important APIs and types:** Verbosity constants are `Default`, `Useful`, `Extended`, `Debug`, and `Trace`. Context keys are `CtxKey` and `ReqID`. Functions include `Log`, `FatalLogMsg`, `ErrorLogMsg`, `ErrorLog`, `WarningLogMsg`, `WarningLog`, `DefaultLog`, `UsefulLog`, `ExtendedLogMsg`, `ExtendedLog`, `DebugLogMsg`, `DebugLog`, `TraceLogMsg`, and `TraceLog`.

**Control flow, state, and persistence:** `Log` prepends `ID` and optional `Req-ID` from context values. Error/warning/fatal functions always format and emit. Verbosity helpers format first, then check `klog.V(level).Enabled()` before logging, so arguments are still evaluated by the caller and formatting cost is still paid.

**Dependencies and integration points:** Depends on `context`, `fmt`, and klog. Used throughout utilities for consistent request-aware logs.

**Risks and test signals:** Context keys are package-level variables of an unexported type, reducing collision risk. Format-before-enabled reduces performance benefits of klog level checks. Fatal exits the process. No direct tests in this subset cover prefix formatting or levels.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/log/log.go -->
