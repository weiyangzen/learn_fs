# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/resources.go

Purpose: defines resource-spec map keys and lookup helpers for Kubernetes resource requirements of Ceph daemon pods, sidecars, and jobs.

Important APIs/types/functions: constants `ResourcesKeyMon`, `ResourcesKeyMgr`, `ResourcesKeyMgrSidecar`, `ResourcesKeyOSD`, `ResourcesKeyPrepareOSD`, `ResourcesKeyCmdReporter`, `ResourcesKeyMDS`, `ResourcesKeyCrashCollector`, `ResourcesKeyLogCollector`, `ResourcesKeyRBDMirror`, `ResourcesKeyFilesystemMirror`, `ResourcesKeyCleanup`, `ResourcesKeyCephExporter`, and `ResourcesKeyFloatingMonShutDownApp`. Helper functions include `GetMgrResources`, `GetMgrSidecarResources`, `GetMonResources`, `GetOSDResources`, `GetOSDResourcesForDeviceClass`, `getOSDResourceKeyForDeviceClass`, `GetPrepareOSDResources`, `GetCmdReporterResources`, `GetCrashCollectorResources`, `GetLogCollectorResources`, `GetFloatingMonShutDownAppResources`, `GetCleanupResources`, and `GetCephExporterResources`.

Control flow: most helpers are direct map lookups on `ResourceSpec`. OSD lookup has special logic: no device class returns the common `osd` resources; a device class first checks `osd-<class>`, then falls back to common `osd`. `GetOSDResourcesForDeviceClass` reports whether a class-specific key exists and returns an empty `ResourceRequirements` plus false when absent.

State and persistence: no persistence or mutation. Map reads on nil or missing keys yield zero-value Kubernetes resource requirements.

Dependencies/integration: depends on Kubernetes core `v1.ResourceRequirements`. Controllers use this file to consistently map CRD resource configuration onto pod containers and jobs.

Risks: several constants do not have corresponding getters in this file (`mds`, `rbdmirror`, `fsmirror`), implying other code may index them directly. Device-class keys are dynamically generated with a simple `osd-` prefix; class names containing unexpected characters still produce map keys. Missing keys silently become zero resource requests/limits.

Test signals: no direct tests in this subset. Useful tests would cover OSD device-class fallback, explicit class-specific retrieval, nil map behavior, and all daemon key constants used by reconcilers.
