<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/httpserver.go -->
## sources/control-plane/ceph-csi/internal/util/httpserver.go

**Purpose:** Provides metrics HTTP server startup and pprof handler registration for Ceph-CSI processes.

**Important APIs and functions:** `ValidateURL` parses `Config.MetricsPath`. `StartMetricsServer` registers the Prometheus handler at the configured path and calls `http.ListenAndServe`. `EnableProfiling` registers runtime pprof profiles plus static cmdline/profile/symbol/trace handlers through `addPath`.

**Control flow, state, and persistence:** This mutates the global `http.DefaultServeMux`. `StartMetricsServer` is blocking and calls fatal logging on listen failure. Profiling handlers are registered by profile name, not with an explicit `/debug/pprof/` prefix in the code shown.

**Dependencies and integration points:** Depends on Prometheus `promhttp`, net/http, pprof, runtime/pprof, net/url, and internal logging. It integrates with process metrics and optional profiling configuration.

**Risks and test signals:** Global mux registration can conflict if called multiple times or if paths are not prefixed consistently. `ValidateURL` only parses, it does not ensure sane path semantics. Server lacks read/write timeouts. There are no tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/httpserver.go -->
