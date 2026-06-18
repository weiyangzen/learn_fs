<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/main.go -->
# Research: sources/control-plane/csi-driver-smb/cmd/smbplugin/main.go

- Purpose: command entrypoint for `smbplugin`, the CSI SMB driver process used by controller and node manifests.
- Important APIs/types/functions: defines flags for CSI endpoint, node ID, driver name, version output, metrics address, kubeconfig, volume stats, Windows SMB mapping cleanup, working mount dir, stats cache expiration, Kerberos cache directory/prefix, default delete policy, archived-volume cleanup, and Windows HostProcess mode. `handle()` builds `smb.DriverOptions`, calls `smb.NewDriver`, and runs `driver.Run`; `exportMetrics()`, `serveMetrics()`, and `trapClosedConnErr()` implement Prometheus metrics serving.
- Control flow: `main()` parses flags; `-ver` prints `smb.GetVersionYAML`; otherwise it warns on empty node ID, starts metrics if configured, creates the driver, and blocks in CSI serving. Metrics are served asynchronously on `/metrics` through the legacy registry.
- State and persistence behavior: process state is flag-derived configuration and metrics listener state. Durable volume state is delegated to `pkg/smb`; this entrypoint only passes cache directories, mount working directory, and delete/cleanup policies.
- Dependencies/integration points: `github.com/kubernetes-csi/csi-driver-smb/pkg/smb`, Kubernetes component-base metrics, `klog`, net/http, CSI endpoints from manifests, Kerberos defaults from image config, and kubeconfig for out-of-cluster use.
- Risks: metrics listener failures only warn and continue; `nodeid` is allowed empty for controller but dangerous for node mode; `trapClosedConnErr` relies on error string matching; privileged mount behavior is hidden in the driver package.
- Test signals: `main_test.go` covers version-path exit behavior and closed-listener error filtering; broader coverage requires integration/e2e CSI tests for flag combinations and node/controller modes.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/main.go -->
