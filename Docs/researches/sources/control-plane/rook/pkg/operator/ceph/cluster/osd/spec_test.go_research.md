# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/spec_test.go

## Purpose
`spec_test.go` is the focused unit/integration test suite for the OSD prepare pod and deployment spec builders. It locks down pod commands, scheduler and priority behavior, placement merging, host networking, resource assignment, PVC raw/LVM init-container composition, encryption/KMS paths, log collector process namespace, probes, services, and device-class update semantics.

## Important APIs, Types, and Functions
The tests exercise `provisionPodTemplateSpec()`, `makeJob()`, `makeDeployment()`, `getPVCEncryptionOpenInitContainerActivate()`, `getPVCEncryptionInitContainerActivate()`, `deploymentOnPVC()`, `deploymentOnNode()`, `createOSDService()`, and helper functions `crushDeviceClassEnvValue()` and `newClusterWithAllowDeviceClassUpdate()`. `testPodDevices()` is the central scenario builder for node OSDs, PVC LVM OSDs, PVC raw OSDs, and encrypted PVC variants.

## Control Flow, State, and Persistence
Tests construct fake clusters and Kubernetes clients, call spec builders, and inspect in-memory Kubernetes objects. They assert exact init-container order for non-PVC activation, PVC LVM config/copy/mapper flow, PVC raw mapper/activate/expand flow, encrypted PVC open/copy/status/resize flow, and metadata/WAL additions. Placement tests compare node-affinity expression counts when `OnlyApplyOSDPlacement` is toggled. Service tests create/update fake Services and compare exposed ports for msgr1+msgr2 vs msgr2-only modes.

## Dependencies and Integration Points
The suite touches `cephv1` placement/resource/health/network specs, `k8sutil` labels and owner info, fake Kubernetes apps/core clients, OSD config store settings, KMS connection details for Vault and KMIP, and controller-generated probes/log collector behavior. It also verifies `ROOK_CUSTOM_HOSTNAME_LABEL` integration through node selectors.

## Risks
Many assertions use exact counts of volumes, mounts, and init containers. That is valuable for detecting accidental pod-spec drift but can require careful updates for legitimate additions. The tests reveal ordering dependencies: encryption open must precede encrypted block copy, activation must precede expansion/key update/chown, and KMS key retrieval must precede cryptsetup open. Device class behavior has multiple precedence paths, where per-device class beats node-level class when updates are allowed, but existing OSD class remains when updates are disabled.

## Test Signals
Strong signals are the PVC matrix with raw/LVM, encrypted/unencrypted, metadata and WAL PVCs, Vault/KMIP/TLS KMS, tuning flags, host-network DNS policy, OSD resource lookup by device class, prepare resource lookup, probe override application, service port selection, and placement expression merging across `all`, `osd`, `prepareosd`, and device-set placement.
