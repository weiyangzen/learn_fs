# sources/control-plane/ceph-csi/internal/controller/controller.go

Purpose: starts and coordinates Ceph-CSI Kubernetes controller-runtime reconcilers that maintain auxiliary metadata such as PV journals and volume group replication journals.

Important APIs/types/functions: `Manager` interface requires `Add(manager.Manager, Config) error`; `Config` carries driver name, namespace, cluster name, and instance ID. `ControllerList` is the global registration list. `Start()` builds scheme/manager and runs all registered managers through `addToManager()`.

Control flow: `Start()` creates a runtime scheme with core Kubernetes and CSI-addons replication APIs, configures leader election using `<driverName>-<namespace>` leases, disables metrics, disables cache for full PV and Secret objects, gets in-cluster/rest config, switches content type to protobuf, creates the controller manager, registers all controllers, and blocks in `mgr.Start()` with signal handling.

State and persistence: process-global `ControllerList` is populated by package `Init()` functions. Kubernetes leader-election leases persist in the configured namespace. The manager uses API server state; PV/Secret caching is deliberately disabled to reduce memory in large clusters.

Dependencies and integration points: integrates controller-runtime, client-go scheme/rest config, CSI-addons replication CRDs, Kubernetes core API, and Ceph-CSI controller packages that append to `ControllerList`.

Risks: global registration order and repeated `Init()` calls can duplicate controllers. `GetConfigOrDie()` exits on config failure. Leader election ID depends on namespace and driver name, so misconfiguration can cause multiple active controllers or unwanted contention. Missing CRD handling is delegated to individual controllers.

Test signals: no direct tests here. Useful integration checks would start a fake manager with registered managers, verify cache disable configuration, and ensure each controller handles missing optional CRDs gracefully.
