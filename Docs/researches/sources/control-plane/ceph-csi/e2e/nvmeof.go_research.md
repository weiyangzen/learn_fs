# sources/control-plane/ceph-csi/e2e/nvmeof.go

Purpose: defines the NVMe-oF CSI e2e suite, covering basic provisioning/deletion, filesystem and block resize, service-account restriction, and node-side GroupLock concurrency behavior.

Important APIs/types/functions: constant `nvmeofPool` names the RBD pool used by the gateway. The Ginkgo `Describe("nvmeof")` gates on `testNVMeoF`, skips helm/operator deployments, sets a privileged framework, and uses `deployGateway()`, `createNVMeoFCredentials()`, `deployNVMeoFPlugin()`, and `createNVMeoFStorageClass()` in setup. Specs call `createPVCAndvalidatePV()`, `validateRBDImageCount()`, `validateOmapCount()`, `validateServiceAccountVolumeRestriction()`, `resizePVCAndValidateSize()`, `createConcurrentPods()`, `deleteConcurrentPods()`, and `mixedCreateDeletePodsOnly()`.

Control flow: `BeforeEach(... OncePerOrdered)` checks Ceph version and skips below Tentacle/v20, deploys the gateway, creates namespace if needed, creates Ceph credentials, deploys the CSI plugin, and creates a per-suite StorageClass targeting `nvmeofPool`. `AfterEach(... OncePerOrdered)` logs CSI and gateway pods on failure, dumps namespace info, deletes plugin, gateway, and StorageClass. The ordered context creates and deletes a PVC, then validates service-account restriction and backend cleanup; resizes filesystem and raw-block PVCs; creates three PVCs then concurrent pods and concurrent deletions to test node GroupLock; and runs a larger mixed create/delete workload with 15 PVCs in batches of five.

State and persistence: creates gateway/pool, CSI resources, StorageClass, PVC/PV/Pod objects, RBD images, omap entries, and service-account metadata. Each spec validates backend image and omap counts return to zero.

Dependencies and integration points: depends on Ceph version helpers, RBD validation helpers, NVMe-oF deployment/gateway helpers, shared PVC/pod concurrency helpers, Ginkgo/Gomega, Kubernetes framework, and pod-security admission.

Risks: suite requires Ceph v20/Tentacle and a working gateway image; otherwise it skips. It only supports simple YAML deployment, not helm/operator. StorageClass gateway IP can stale if gateway restarts. GroupLock tests focus on node-stage/unstage pod operations and deliberately avoid controller concurrency, so they do not cover all lock interactions.

Test signals: successful skip on unsupported Ceph, CSI readiness, backend image/omap counts matching PVC lifecycle, successful service-account restriction, resize validation for filesystem and block, no errors/deadlocks in concurrent pod create/delete flows, and zero backend artifacts after cleanup.
