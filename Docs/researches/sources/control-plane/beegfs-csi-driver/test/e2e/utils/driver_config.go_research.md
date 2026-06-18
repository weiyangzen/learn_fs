<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/driver_config.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/utils/driver_config.go

Purpose: helpers for locating and mutating the BeeGFS driver configuration used by e2e tests.
Important APIs/functions: `GetBeegfsDriverInUse`, `GetConfigMapInUse`, `GetPluginConfigInUse`, and `UpdatePluginConfigInUse`; package-level GVR for `beegfsdrivers.beegfs.csi.netapp.com/v1`.
Control flow/state: detects operator-enabled clusters through the dynamic client; otherwise finds the controller pod and the mounted `csi-beegfs-config*` ConfigMap. Updates either the BeegfsDriver CR or the ConfigMap, then deletes controller/node pods for ConfigMap-based deployments so they reload config.
Dependencies/integration: uses client-go dynamic and typed clients, operator API types, YAML strict marshal/unmarshal, and pod utility functions in this package.
Risks/test signals: expects exactly one BeegfsDriver in operator clusters; ConfigMap lookup depends on volume naming convention; updates are live cluster state and need log archival before restart. Success is pod restart/re-read without client errors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/driver_config.go -->
