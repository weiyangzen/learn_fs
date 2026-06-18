# subset-b-000340 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof_helper.go -->
## sources/control-plane/ceph-csi/e2e/nvmeof_helper.go

### Purpose
`nvmeof_helper.go` contains e2e helpers for stressing NVMe-oF pod attach/detach behavior, especially the NodeServer GroupLock path. It deliberately separates ControllerServer PVC provisioning/deletion from NodeServer pod create/delete operations so tests can exercise concurrent `NodeStage` and `NodeUnstage` activity without mixing in provisioning concurrency.

### Important APIs, Types, And Functions
`concurrentPodsResult` records a generated pod-name prefix, operation count, per-index errors, and failure count. Its `String`, `HasErrors`, and `LogErrors` methods provide compact result inspection and framework logging.

`createConcurrentPods(totalCount, pvcBaseName, pvcStartIndex, appPath, f)` loads a pod template with `loadApp`, sets the namespace, deep-copies the pod per goroutine, assigns a unique pod name, points the first volume at an existing PVC, and calls `createApp`.

`deleteConcurrentPods(result, f)` mirrors creation by deleting generated pod names in parallel with `deletePod`.

`mixedCreateDeletePodsOnly(totalCount, batchSize, pvcPath, appPath, storageClassName, f)` is the higher-level scenario. It creates all PVCs sequentially, creates the first pod batch, then for each later batch concurrently creates the next batch while deleting the previous one, validates running state, deletes the final batch, and finally deletes all PVCs.

### Control Flow
The top-level helper validates `batchSize > 0` and exact divisibility, then loads and configures the PVC template once. All PVCs are provisioned one by one with unique names and `createPVCAndvalidatePV`. A cleanup closure deletes any active pod batch and then attempts every PVC deletion to reduce leaked cluster state on early failures.

The initial pod batch is created with `createConcurrentPods` and each pod is checked with `waitForPodInRunningState`. Later iterations run two goroutines under a `sync.WaitGroup`: one creates the new batch against the next PVC offset, and one deletes the previous batch. Errors from both sides are collected, but the flow still validates the current batch's running pods before advancing `previousResult`. After the loop, the last pod batch is deleted and all PVCs are removed sequentially.

### State, Persistence, And Dependencies
The helper persists no process-local state beyond stack variables and per-call slices. Cluster state is the real state under test: PVCs, PVs, pods, volume attachments, and CSI side effects. Unique names come from `github.com/google/uuid`. Kubernetes integration is through `framework.Framework`, `f.ClientSet`, `loadPVC`, `loadApp`, `createPVCAndvalidatePV`, `deletePVCAndValidatePV`, `createApp`, `deletePod`, and `waitForPodInRunningState`.

### Integration Points
This file is intended for Ceph-CSI e2e specs that need deterministic NVMe-oF attach/detach pressure. It uses YAML templates owned elsewhere in the e2e suite and the common `deployTimeout`, `poll`, and framework logging conventions. The explicit "pods only" concurrency makes it a focused integration point for nodeplugin locking behavior rather than storage-class or controller provisioning behavior.

### Risks
`createConcurrentPods` assumes the loaded pod template has `Spec.Volumes[0].PersistentVolumeClaim` populated; malformed templates can panic rather than return an error. The concurrent create/delete loop writes `createResult` and `deleteResult` from goroutines and reads them after `Wait`, which is safe for visibility after synchronization but would be fragile if later logic read them before the wait. If current-batch creation has failures, the code still references `createResult.uniqueName` during running-state validation; a completely failed create result still has a name, but follow-on errors can obscure the original failure set. Cleanup ignores deletion errors by design, so leaked resources are possible when the API server or CSI cleanup path is unhealthy.

### Test Signals
Strong signals are validation of invalid `batchSize` and non-divisible totals, successful multi-batch create/delete interleaving, injected pod-create and pod-delete failures with logged per-index errors, cleanup after initial batch failure, and resource-leak checks after failures. Tests should also include templates with multiple volumes or missing volume claims if this helper is reused outside its current NVMe-oF fixtures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/openshift.go -->
## sources/control-plane/ceph-csi/e2e/openshift.go

### Purpose
`openshift.go` detects whether the e2e suite is running on OpenShift. It probes the OpenShift `clusterversion.config.openshift.io/version` resource and reports a boolean instead of forcing non-OpenShift clusters to fail.

### Important APIs, Types, And Functions
`detectOpenShift() (bool, error)` is the only function. It calls `e2ekubectl.RunKubectl` in the `openshift` namespace with a JSONPath query for `.status.desired.version`. It uses `isNoSuchResourceCLIError` to distinguish absence of the OpenShift API from other kubectl failures and logs the version through `framework.Logf` when detection succeeds.

### Control Flow
The function runs `kubectl get clusterversion.config.openshift.io/version`. If kubectl returns an error that means the resource type is unavailable, it returns `(false, nil)`. Any other error is returned as `(false, err)`. On success, the detected desired version is logged and the function returns `(true, nil)`.

### State, Persistence, And Dependencies
There is no local or persistent state. The function depends on the external kubectl command path used by Kubernetes e2e framework helpers, cluster RBAC permitting access to the clusterversion object, and the local `isNoSuchResourceCLIError` classifier defined elsewhere in the e2e package.

### Integration Points
Other e2e tests can use this helper to conditionally run OpenShift-specific assertions or skip behavior that differs between OpenShift and vanilla Kubernetes. It uses the same kubectl wrapper and logging approach as the rest of the Ceph-CSI e2e code.

### Risks
The command uses the namespace argument `openshift`, but `clusterversion` is a cluster-scoped OpenShift resource; this works with kubectl but may be confusing when diagnosing RBAC failures. Detection can return an error rather than `false` if kubectl is unavailable, credentials are invalid, or permissions deny the get request. The JSONPath includes shell-style quotes as part of the argument; this matches the wrapper's current usage but could be brittle if the wrapper changes quoting behavior.

### Test Signals
Useful signals are mocked kubectl success with a version string, "no such resource" errors producing `false, nil`, RBAC or connection errors being propagated, and caller behavior on non-OpenShift clusters. Integration tests should also validate detection against a real OpenShift cluster because the helper relies on kubectl's CRD/resource discovery behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/openshift.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/operator.go -->
## sources/control-plane/ceph-csi/e2e/operator.go

### Purpose
`operator.go` implements the e2e deployment-method adapter for Ceph-CSI when it is managed by the Ceph-CSI operator. It maps common RBD and CephFS deployment operations onto operator-created deployment and daemonset names and patches the operator config CR for cluster-name and topology-domain settings.

### Important APIs, Types, And Functions
`OperatorConfigName` is the fixed CR name `ceph-csi-operator-config`. `OperatorDeployment` embeds `DriverInfo`, so it satisfies the existing deployment method interfaces through shared methods plus operator-specific methods.

`NewRBDOperatorDeployment(c)` returns an `RBDDeploymentMethod` configured with operator RBD deployment/daemonset names and RBD container names. `NewCephFSOperatorDeployment(c)` returns a `CephFSDeploymentMethod` configured with operator CephFS names and the CephFS container.

`getPodSelector()` returns a selector matching Helm labels and operator deployment/daemonset names. `setClusterName(value)` patches `spec.driverSpecDefaults.clusterName` with a merge patch. `setDomainLabels(labels)` builds a JSON Patch adding `nodePlugin`, `topology`, and `domainLabels` under `spec.driverSpecDefaults`.

### Control Flow
Constructors populate `DriverInfo` with the clientset, expected controller deployment, nodeplugin daemonset, and driver container names. Runtime selection and readiness checks inherited from `DriverInfo` use `getPodSelector` to find Ceph-CSI pods across Helm-like labels and operator names. Configuration methods build kubectl patch argument lists and call `retryKubectlArgs` in the Ceph-CSI namespace with `deployTimeout`; errors are wrapped with operation-specific context.

### State, Persistence, And Dependencies
The Go object holds only client and naming metadata. Persistent state is modified in the Kubernetes API by patching the `operatorconfigs.csi.ceph.io` resource named by `OperatorConfigName`. Dependencies include local constants for operator and Helm names, deployment interfaces (`RBDDeploymentMethod`, `CephFSDeploymentMethod`), `DriverInfo`, `retryKubectlArgs`, `kubectlPatch`, `cephCSINamespace`, and standard JSON marshaling for JSON Patch serialization.

### Integration Points
This adapter lets existing deployment-agnostic e2e tests run against operator-managed Ceph-CSI. Topology and cluster-name tests can call the same interface methods regardless of whether the suite deployed via Helm/manifests or the operator, while this file translates those calls into operator config patches.

### Risks
`setDomainLabels` uses JSON Patch `add` operations for intermediate paths. If `nodePlugin` or `topology` already exists, Kubernetes JSON Patch may reject duplicate additions or replace behavior may not match test intent; a merge patch could be safer if repeated calls are expected. `getPodSelector` mixes Helm labels with operator names, so a broad selector could match stale pods during transitions. These helpers patch config but do not themselves wait for operator reconciliation; callers must restart or wait for affected CSI pods where needed.

### Test Signals
Tests should verify constructor interface compatibility, generated selectors for RBD and CephFS, successful merge patch JSON for cluster names, correct JSON Patch payload for domain labels, retry behavior on transient kubectl errors, and idempotency or expected failure behavior when `setDomainLabels` is called more than once against an existing config.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/operator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/pod.go -->
## sources/control-plane/ceph-csi/e2e/pod.go

### Purpose
`pod.go` is the Ceph-CSI e2e suite's pod and nodeplugin helper layer. It loads pod templates, creates and deletes application pods, waits for daemonset and pod readiness, executes shell commands inside pods or CSI daemonset containers, validates RWOP and SELinux/read-affinity behavior, and verifies Ceph metadata tied to pod/node lifecycle.

### Important APIs, Types, And Functions
The file defines error-string constants for generic command failure and old/new Kubernetes ReadWriteOncePod conflict messages, plus `noError` as the nil expected-error sentinel.

Pod selection and execution helpers include `getDaemonSetLabelSelector`, `waitForDaemonSets`, `findPodAndContainerName`, `getCommandInPodOpts`, `execCommandInDaemonsetPod`, `getDaemonsetPodOnNode`, `listPods`, `execWithRetry`, `execCommandInPod`, `execCommandInContainer`, `execCommandInContainerByPodName`, `execCommandInToolBoxPod`, and `execCommandInPodAndAllowFail`.

Lifecycle helpers include `loadApp`, `createApp`, `createAppErr`, `waitForPodInRunningState`, `getPod`, `deletePod`, `deletePodWithLabel`, and `waitForPVCVolumeAttachmentsCleanup`.

Validation helpers include `calculateSHA512sum`, `appendToFileInContainer`, `getKernelVersionFromDaemonset`, `recreateCSIPods`, `validateRWOPPodCreation`, `verifySeLinuxMountOption`, `verifyReadAffinity`, `verifyMetadataRemoved`, `getAppAndPVC`, `verifyClientAddressMetadataExists`, and `verifyUserIdMappingMetadata`.

### Control Flow
The readiness functions poll Kubernetes resources until the desired condition appears or timeout expires. `waitForDaemonSets` repeatedly gets a daemonset and compares desired versus ready pod counts. `waitForPodInRunningState` polls a pod phase, accepts `Running`, treats completed phases as errors, and can treat expected event substrings as success when testing negative scheduling cases such as RWOP conflicts.

Execution flows resolve a target pod/container from selectors, build `e2epod.ExecOptions`, and run through `execWithRetry`, which retries only retryable API errors before returning captured stdout, stderr, and error. Higher-level command helpers log stderr but generally leave failure interpretation to callers.

Template and lifecycle flows unmarshal pod YAML, force `PullIfNotPresent` on all containers, create pods, wait for running state, and delete pods while polling for `NotFound`. CSI pod recreation deletes selected pods with kubectl and waits for both daemonset and deployment recovery.

Feature validations create PVC/app pairs, inspect Kubernetes and Ceph state, then clean up. SELinux validation modifies the bound PV mount options, starts an app, locates the nodeplugin pod on the app's node, and searches nodeplugin logs. Read-affinity validation creates an app, maps the PVC to an RBD image, reads `/sys/devices/rbd/*/config_info` from a CSI container, and validates `read_from_replica` and CRUSH location values. Metadata validation reads RBD image metadata or CephFS subvolume metadata for client address or user ID keys, deletes the pod, then waits for metadata removal.

### State, Persistence, And Dependencies
Most state is cluster state: pods, daemonsets, deployments, PVCs/PVs, VolumeAttachments, nodeplugin logs, and Ceph image/subvolume metadata. Local state is transient poll variables, command output, and loaded pod objects. Dependencies include Kubernetes core/apps/storage APIs, `wait.PollUntilContextTimeout`, e2e framework pod exec/log helpers, local constants for namespaces, labels, container names, topology values, Ceph metadata keys, and many helpers from adjacent files such as PVC helpers, deployment readiness, Ceph RBD/CephFS metadata access, image lookup, and kubectl retry wrappers.

### Integration Points
This file is central glue for RBD, CephFS, and NVMe-oF e2e tests. Other specs use it to run application pods against PVCs, execute verification commands in toolbox or nodeplugin pods, restart CSI components, validate Kubernetes scheduling errors, and assert that CSI node operations leave expected Ceph-side metadata. It also underpins `nvmeof_helper.go`, which uses `loadApp`, `createApp`, `deletePod`, and `waitForPodInRunningState`.

### Risks
`listPods` reads `podList.Items` before checking whether `List` returned an error, so a nil `podList` on error would panic. `waitForPVToBeDeleted` in the PVC file has a similar logging-before-error-check pattern; callers that combine these helpers should watch for API error paths. `calculateSHA512sum` uses `strings.Split(sha512sumOut, "")[0]`, which splits into characters rather than fields and will not return the checksum token; this looks like a concrete bug and should likely be `strings.Fields`. Several helpers assume selectors find at least one pod and that the first container is a useful default. `verifyReadAffinity` parses `key:value` pairs with fixed two-element indexing, so malformed `config_info` content can panic. Cleanup after validation failures is best-effort and may leak PVCs or pods if failures occur before the final cleanup call.

### Test Signals
High-value tests include selector resolution with empty, errored, and multi-container pod lists; exec retry behavior on retryable and permanent errors; pod readiness with expected RWOP event strings for both old and new Kubernetes messages; deletion polling on API errors and `NotFound`; checksum parsing against real `sha512sum` output; VolumeAttachment cleanup for bound, unbound, and deleted PVCs; SELinux mount-option log matching; read-affinity config parsing; and metadata removal for both RBD and CephFS after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/pod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/pvc.go -->
## sources/control-plane/ceph-csi/e2e/pvc.go

### Purpose
`pvc.go` provides PersistentVolumeClaim and PersistentVolume lifecycle helpers for Ceph-CSI e2e tests. It loads PVC templates, creates and deletes PVC/PV pairs, waits for binding or deletion, fetches bound resources, validates topology node affinity, and checks kubelet volume stats metrics for filesystem and block volumes.

### Important APIs, Types, And Functions
Template and create helpers are `loadPVC`, `createPVCAndvalidatePV`, `createPVCAndPV`, and `createPVC`. Lookup helpers are `getPersistentVolumeClaim`, `getPersistentVolume`, `getPVCAndPV`, and `getBoundPV`. Deletion helpers are `deletePVCAndPV`, `deletePVCAndValidatePV`, and `waitForPVToBeDeleted`.

Validation helpers are `checkPVSelectorValuesForPVC`, `getMetricsForPVC`, `parseVolumeStatsMetrics`, and `validateVolumeStatsMetrics`. They cover topology labels and kubelet `kubelet_volume_stats_*` metrics.

### Control Flow
`createPVCAndvalidatePV` creates a PVC, returns immediately if timeout is zero, then polls until the PVC has a `Spec.VolumeName`, fetches the PV, and delegates final binding checks to Kubernetes e2e `WaitOnPVandPVC`. While waiting for a volume name, it logs PVC events to make provisioning failures visible in test output.

`deletePVCAndPV` deletes both objects explicitly, then polls for PVC deletion and PV deletion. `deletePVCAndValidatePV` fetches the live PVC and backing PV before deleting only the claim, then polls until both the PVC and dynamically provisioned PV disappear. `getPersistentVolumeClaim` and `getPersistentVolume` wrap API gets in retry polling.

Topology validation fetches the bound PV and inspects the first required node-selector term, requiring exactly the expected region and zone keys/values and rejecting duplicate or unexpected keys. Metrics validation discovers a kubelet IP, curls its read-only metrics endpoint from the toolbox pod, extracts metrics for the PVC, and validates required capacity/used/available/inode relationships depending on volume mode.

### State, Persistence, And Dependencies
State is stored in Kubernetes resources and kubelet metrics, not in this helper. The helpers depend on Kubernetes core API clients, Kubernetes e2e PV waiting utilities, Ceph-CSI e2e polling/timeouts, toolbox pod command execution from `pod.go`, topology constants (`nodeCSIRegionLabel`, `nodeCSIZoneLabel`, `regionValue`, `zoneValue`), `getKubeletIP`, and local retryable API error classification.

### Integration Points
These helpers are used throughout Ceph-CSI e2e specs and by `nvmeof_helper.go` and `pod.go`. They provide the common contract that a created PVC is actually bound to a PV before a pod uses it, and that deletion waits for CSI/Kubernetes cleanup before the next test step. Metrics helpers integrate Kubernetes PVC state with node-level kubelet metrics exposed through the rook toolbox pod.

### Risks
`deletePVCAndValidatePV` logs `oldPV.Status` when a retryable error occurs after `oldPV` may be nil, which can panic on some API error paths. `waitForPVToBeDeleted` logs `pv.Status.String()` before checking `err`, so a failed get can also panic. `checkPVSelectorValuesForPVC` assumes `NodeAffinity`, `Required`, at least one selector term, and non-empty expression values; missing affinity structure can panic instead of returning an error. `createPVCAndPV` creates the PVC before the PV, which is fine for static tests but can briefly expose an unbound claim if PV creation fails. `getMetricsForPVC` relies on kubelet read-only port `10255`, so it will fail in clusters where that endpoint is disabled. `parseVolumeStatsMetrics` is intentionally simple and may not handle unusual Prometheus line formats beyond the expected kubelet metric lines.

### Test Signals
Tests should cover successful dynamic binding, provisioning events on delayed binding, timeout-zero create behavior, explicit PVC/PV create/delete, deletion with transient API errors, missing PVs, topology affinity success and malformed affinity structures, metric parsing with labels in different orders, filesystem versus block validation requirements, invalid metric values, and kubelet endpoint unavailability. Regression tests for nil-pointer paths in deletion polling would be particularly valuable.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/pvc.go -->
