# Research Report: subset-b-000372

This grouped report covers the requested SMB CSI driver test files and csi-lib-utils support packages. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/suite_test.go -->
# sources/control-plane/csi-driver-smb/test/e2e/suite_test.go

## Purpose
This is the Ginkgo/Gomega e2e suite bootstrap for the SMB CSI driver. It installs or reuses the SMB provisioner and CSI driver, starts an in-process SMB driver endpoint for direct CSI cleanup calls, configures test storage-class parameters, adapts Linux test commands for Windows clusters, and performs suite teardown/log collection.

## Important APIs, Types, And Functions
Key constants define environment-variable contracts: `KUBECONFIG`, `ARTIFACTS`, `TEST_WINDOWS`, `WINDOWS_SERVER_VERSION`, `PRE_INSTALL_SMB_PROVISIONER`, `TEST_SMB_SOURCE`, `TEST_SMB_SECRET_NAME`, and `TEST_SMB_SECRET_NAMESPACE`. Package globals hold `smbDriver`, Windows/preinstall flags, and storage-class parameter maps for default, subdir, retain, archive, and no-provisioner-secret modes. `testCmd` models an external command with start/end log messages. `BeforeSuite` and `AfterSuite` are the main lifecycle hooks. `TestMain` wires Kubernetes e2e flags, `TestE2E` runs specs with a JUnit reporter, `execTestCmd` runs project-root commands, `convertToPowershellCommandIfNecessary` maps known shell snippets to PowerShell, and `skipIfTestingInWindowsCluster` centralizes Windows skips.

## Control Flow
`BeforeSuite` ensures `KUBECONFIG`, optionally runs `make install-smb-provisioner`, `make e2e-bootstrap`, and `make create-metrics-svc`, then starts `smb.Driver.Run` against a random Unix socket. For Windows clusters it changes to the project root, obtains either an Azure File source for host-process deployments or the public SMB service IP, and rewrites all storage-class parameter maps. `AfterSuite` runs example validation for non-Windows clusters, always prints SMB logs, tears down the e2e driver unless preinstalled, and validates install/uninstall scripts.

## State, Persistence, And Dependencies
Persistent state is external: Kubernetes resources, generated JUnit XML under `ARTIFACTS` or `test/e2e`, and potential `/tmp/csi-*.sock` sockets. It depends on `make` targets, shell scripts under `test/utils`, Kubernetes e2e framework packages, Ginkgo v2, Gomega, and the SMB driver package.

## Integration Points
The suite supplies globals consumed by dynamic provisioning specs and testsuite structs. It integrates with Kubernetes via kubeconfig, with Makefile deployment targets, with Windows-specific helper scripts, and with the local CSI driver object used by reclaim-policy tests.

## Risks And Test Signals
Risks include process-wide `os.Chdir`, mutable global storage-class maps, hard-coded command translations, base64-encoded host-process test account data, and command failures surfaced only during suite startup/teardown. The primary test signals are Ginkgo spec results, JUnit output, Kubernetes events/logs from `smb_log.sh`, and direct Gomega expectations around external command success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_cmd_volume_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_cmd_volume_tester.go

## Purpose
This testsuite verifies that dynamically provisioned SMB-backed PVCs can be mounted into pods whose command completes successfully.

## Important APIs, Types, And Functions
`DynamicallyProvisionedCmdVolumeTest` carries a `driver.DynamicPVTestDriver`, a list of `PodDetails`, and storage-class parameters. Its single API, `Run(ctx, client, namespace)`, is invoked by e2e specs to exercise one or more pod definitions.

## Control Flow
For each pod definition, `Run` calls `PodDetails.SetupWithDynamicVolumes`, defers all returned cleanup functions, creates the pod, defers pod cleanup, and waits for `WaitForSuccess`. Dynamic provisioning, PVC binding, PV validation, and volume attachment are delegated to shared helpers in `specs.go` and `testsuites.go`.

## State, Persistence, And Dependencies
The test creates StorageClasses, PVCs, PVs, and Pods in the provided namespace. Cleanup uses deferred Kubernetes delete calls. Dependencies include the Kubernetes clientset, Ginkgo step logging, and the SMB e2e driver abstraction.

## Integration Points
Specs configure `Pods` with commands and volume details; this runner only enforces successful pod completion. It is the base pattern reused by multiple specialized dynamic-volume tests.

## Risks And Test Signals
Risk is mainly deferred cleanup ordering across multiple pods; failures before defers can leak resources. The direct signal is pod success within the shared timeout, with provisioning failures surfacing through helper assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_cmd_volume_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go

## Purpose
This testsuite validates that multiple dynamically provisioned SMB volumes can be used by pods, optionally forcing later pods onto the same node as the first pod.

## Important APIs, Types, And Functions
`DynamicallyProvisionedCollocatedPodTest` contains `CSIDriver`, `Pods`, `ColocatePods`, and storage-class parameters. `Run` is the sole entry point.

## Control Flow
The runner provisions volumes and pods one-by-one. When `ColocatePods` is true and a previous pod has established `nodeName`, it sets a node selector `{"name": nodeName}` on the next pod. Each pod is created, cleanup is deferred, and `WaitForRunning` confirms that it is live rather than waiting for command completion.

## State, Persistence, And Dependencies
State is Kubernetes resources plus the in-memory `nodeName` captured from the first scheduled pod. It depends on shared pod/PVC helpers and assumes nodes expose a `name` label matching `pod.Spec.NodeName`.

## Integration Points
Specs use this to exercise multi-pod or same-node behavior for SMB mounts. It integrates with dynamic provisioning and scheduler placement.

## Risks And Test Signals
The node selector can be brittle because Kubernetes commonly uses `kubernetes.io/hostname` rather than `name`. The test signal is pod Running state; it does not validate file contents or concurrent writes directly in this runner.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_delete_pod_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_delete_pod_tester.go

## Purpose
This testsuite verifies that an SMB-backed PVC remains usable across deletion and recreation of a Deployment-managed pod.

## Important APIs, Types, And Functions
`DynamicallyProvisionedDeletePodTest` holds the CSI driver, a single `PodDetails`, optional `PodExecCheck`, `SkipAfterRestartCheck`, and storage-class parameters. `PodExecCheck` contains an exec command and expected output string.

## Control Flow
`Run` creates a Deployment with one dynamically provisioned PVC, waits for the pod to be ready, optionally polls `kubectl exec` output, deletes the pod, waits for Deployment reconciliation to produce a running replacement, and optionally checks output again. The second expected string is doubled to detect persisted/appended content after restart unless explicitly skipped.

## State, Persistence, And Dependencies
Persistent state is the PVC/PV and application data written by the pod command. The Deployment object drives pod recreation. The runner relies on sleeps, shared Deployment helpers, and kubectl exec polling.

## Integration Points
This is used by specs that test SMB mount durability and pod lifecycle behavior. It integrates with Deployment controller behavior, Kubernetes exec, and dynamic volume provisioning.

## Risks And Test Signals
The fixed five-second sleep is a timing assumption. The doubled-string assertion assumes command behavior appends exactly once per pod start. Signals include Deployment readiness, pod deletion completion, and observed exec output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_delete_pod_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_inline_volume.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_inline_volume.go

## Purpose
This file tests CSI inline SMB volumes, where the pod spec embeds `CSIVolumeSource` attributes instead of using a dynamically provisioned PVC.

## Important APIs, Types, And Functions
`DynamicallyProvisionedInlineVolumeTest` includes a dynamic driver field, pod definitions, SMB `Source`, `SecretName`, and `ReadOnly`. `Run` is the entry point.

## Control Flow
For each pod, `Run` calls `SetupWithCSIInlineVolumes`, creates the pod, defers cleanup, and waits for successful command completion. The actual inline volume construction is in `TestPod.SetupCSIInlineVolume`.

## State, Persistence, And Dependencies
No StorageClass, PVC, or PV objects are created. State lives in the pod spec and the external SMB share. Dependencies include a pre-existing secret name in the namespace and the SMB CSI node driver.

## Integration Points
Specs provide source and secret values, usually derived from suite defaults. It integrates directly with kubelet CSI inline-volume mounting rather than controller provisioning.

## Risks And Test Signals
The cleanup slice is currently empty, so all cleanup is pod cleanup. Risks include missing secret/source validation until pod mount time. The signal is pod success or mount failure surfaced by Kubernetes pod status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_inline_volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_pod_with_multiple_pv.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_pod_with_multiple_pv.go

## Purpose
This testsuite validates a single pod mounting multiple dynamically provisioned SMB-backed persistent volumes.

## Important APIs, Types, And Functions
`DynamicallyProvisionedPodWithMultiplePVsTest` contains `CSIDriver`, `Pods`, and storage-class parameters. `Run` is the only method.

## Control Flow
Each configured pod is expanded through `SetupWithDynamicMultipleVolumes`, which loops through `VolumeDetails`, creates a StorageClass/PVC for each volume, attaches all claims to one pod, then `Run` creates the pod and waits for success.

## State, Persistence, And Dependencies
The runner creates multiple StorageClass/PVC/PV sets per pod and one Pod object. It depends on shared helpers for cleanup, binding, and PV validation.

## Integration Points
Specs use this for multi-volume mount semantics and path naming generated from `VolumeMountDetails`.

## Risks And Test Signals
The implementation duplicates `SetupWithDynamicVolumes` behavior and relies on generated mount names remaining unique. The signal is a successful pod exit after all volumes are provisioned and mounted.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_pod_with_multiple_pv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_read_only_volume_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_read_only_volume_tester.go

## Purpose
This testsuite verifies that read-only SMB volume mounts prevent writes and expose an expected error in pod logs.

## Important APIs, Types, And Functions
`DynamicallyProvisionedReadOnlyVolumeTest` carries a dynamic driver, pod details, and storage-class parameters. `Run` provisions volumes and checks failure behavior.

## Control Flow
For each pod, it selects the expected log substring: `"Read-only file system"` for Linux or `"FileOpenFailure"` for Windows. It sets up dynamic volumes, creates the pod, waits for failure, then reads pod logs and asserts that the selected substring is present.

## State, Persistence, And Dependencies
State includes the Kubernetes resources and pod log stream. Dependencies include Gomega string matching, framework error handling, and shared provisioning helpers.

## Integration Points
Specs must configure a pod command that attempts a write to a read-only mount. This runner integrates with the shared `TestPod.WaitForFailure` condition and Kubernetes pod log retrieval.

## Risks And Test Signals
The expected error text is platform-specific and could change with base image or shell behavior. The signal is a failed pod plus matching log text; a mount failure with different wording may fail the test even if read-only behavior is correct.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_read_only_volume_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go

## Purpose
This testsuite validates SMB dynamic provisioning behavior for Kubernetes reclaim policies and SMB driver `onDelete` behavior.

## Important APIs, Types, And Functions
`DynamicallyProvisionedReclaimPolicyTest` holds the e2e dynamic driver, a list of `VolumeDetails`, a concrete `*smb.Driver`, and storage-class parameters. `Run` is the entry point.

## Control Flow
For each volume, it provisions a PVC/PV pair, defers StorageClass deletion manually, calls PVC cleanup, then checks retain behavior. If the PV reclaim policy is `Retain`, it waits for `Released`, deletes the bound PV, and invokes `smb.Driver.DeleteVolume` directly to remove backing SMB data.

## State, Persistence, And Dependencies
State is Kubernetes PV/PVC lifecycle and backend SMB directories. Unlike most tests, it uses the in-process SMB driver to delete backing storage after retained PV cleanup.

## Integration Points
The suite’s global `smbDriver` is passed into this test. It integrates Kubernetes reclaim-policy behavior with SMB driver DeleteVolume semantics.

## Risks And Test Signals
Direct driver cleanup bypasses Kubernetes controller flow and assumes `VolumeHandle` remains valid. StorageClass cleanup is manual because the cleanup returned by setup is ignored. Signals are PVC deletion, PV phase/deletion, and direct DeleteVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_resize_volume_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_resize_volume_tester.go

## Purpose
This testsuite validates dynamic PVC expansion for SMB volumes by increasing a claim by 1 GiB and checking PVC/PV sizes.

## Important APIs, Types, And Functions
`DynamicallyProvisionedResizeVolumeTest` contains `CSIDriver`, `Pods`, and storage-class parameters. `Run` performs provisioning, pod validation, claim update, and size checks.

## Control Flow
For each pod, it provisions and runs a pod successfully, fetches the first PVC from the pod spec, adds 1 GiB to `Spec.Resources.Requests["storage"]`, updates the PVC, sleeps 30 seconds, then fetches the PVC and PV to compare requested/capacity sizes.

## State, Persistence, And Dependencies
State is the PVC spec update and PV capacity. Dependencies include Kubernetes storage expansion support, resource quantity arithmetic, and the controller expansion capability advertised by the driver.

## Integration Points
Specs provide a storage class configured for expansion. This integrates Kubernetes PVC update APIs with SMB controller expansion.

## Risks And Test Signals
The fixed 30-second sleep can be flaky on slow clusters and the code ignores the error from fetching the new PV. It checks spec/capacity equality but not filesystem resize inside a running pod. Signals are PVC update success and PV capacity matching the new requested size.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_resize_volume_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_restart_driver_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_restart_driver_tester.go

## Purpose
This testsuite verifies that restarting the SMB CSI node driver does not disrupt an already mounted SMB volume used by a running Deployment pod.

## Important APIs, Types, And Functions
`DynamicallyProvisionedRestartDriverTest` contains the dynamic driver, a `PodDetails`, optional `PodExecCheck`, storage-class parameters, and a `RestartDriverFunc`.

## Control Flow
`Run` provisions a deployment-backed PVC, waits for pod readiness, optionally checks volume access through exec, invokes `RestartDriverFunc`, then repeats the exec check against the original pod.

## State, Persistence, And Dependencies
The persistent state is the running pod mount and PVC/PV. Restart behavior is delegated to an injected function, usually a shell script that deletes/reapplies node daemonsets.

## Integration Points
This connects e2e tests with cluster-level deployment mechanics. It uses shared Deployment helpers and kubectl exec polling for verification.

## Risks And Test Signals
The runner does not wait explicitly for the restarted daemonset to become ready; that must be handled by the injected function or the exec polling. The signal is preserved expected output after driver restart.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_restart_driver_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_volume_cloning_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_volume_cloning_tester.go

## Purpose
This testsuite validates PVC cloning for SMB dynamic provisioning, including optional cloned volume size changes.

## Important APIs, Types, And Functions
`DynamicallyProvisionedVolumeCloningTest` includes the dynamic driver, a source `Pod`, a `PodWithClonedVolume`, optional `ClonedVolumeSize`, and storage-class parameters. `Run` performs the clone scenario.

## Control Flow
The runner creates a StorageClass once, assigns it to the source volume, creates and runs the source pod, sleeps five seconds, then constructs a cloned `VolumeDetails` whose data source is the source PVC name and kind `PersistentVolumeClaim`. It optionally overrides claim size, assigns the same StorageClass, creates a second pod with the clone, and waits for success.

## State, Persistence, And Dependencies
State includes the source PVC content and the cloned PVC/PV. Dependencies include Kubernetes PVC data source support and SMB driver clone behavior.

## Integration Points
It integrates `CreateStorageClass`, `SetupWithDynamicVolumes`, and PVC `DataSource` wiring. The constants in `specs.go` provide the PVC kind.

## Risks And Test Signals
The five-second sleep is a coarse consistency delay before clone creation. The test confirms cloned volume usability through pod success but does not directly compare byte-for-byte content unless the pod commands do so.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_volume_cloning_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_volume_subpath_tester.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_volume_subpath_tester.go

## Purpose
This testsuite verifies SMB dynamic volumes mounted with a Kubernetes `subPath`.

## Important APIs, Types, And Functions
`DynamicallyProvisionedVolumeSubpathTester` contains `CSIDriver`, `Pods`, and storage-class parameters. `Run` is the single entry point.

## Control Flow
For each pod, it calls `SetupWithDynamicVolumesWithSubpath`, which provisions the PVC and mounts it using `SetupVolumeMountWithSubpath` with the fixed subpath `testSubpath`. It then creates the pod, defers cleanup, and waits for success.

## State, Persistence, And Dependencies
State includes the dynamically provisioned PVC/PV and the subpath directory behavior inside the mounted SMB share. Dependencies are the kubelet subPath implementation and shared dynamic provisioning helpers.

## Integration Points
Specs provide commands that should work through the subpath mount. The test integrates StorageClass/PVC provisioning with pod volume mount subPath handling.

## Risks And Test Signals
The subpath name is fixed, so parallel tests only remain isolated because PVCs and shares are isolated. The signal is successful pod completion, with mount/setup failures surfacing as pod failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_volume_subpath_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/specs.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/specs.go

## Purpose
This file defines declarative data structures used by SMB e2e specs to describe pods, volumes, mounts, devices, data sources, and provisioning modes, plus setup methods that turn those descriptions into Kubernetes test resources.

## Important APIs, Types, And Functions
Core types are `PodDetails`, `VolumeDetails`, `VolumeMode`, `VolumeMountDetails`, `VolumeDeviceDetails`, and `DataSource`. Constants include `FileSystem`, `Block`, `VolumePVCKind`, and `APIVersionv1beta1`. Important methods are `SetupWithDynamicVolumes`, `SetupWithDynamicMultipleVolumes`, `SetupWithPreProvisionedVolumes`, `SetupWithCSIInlineVolumes`, `SetupDeployment`, `SetupWithDynamicVolumesWithSubpath`, `VolumeDetails.SetupDynamicPersistentVolumeClaim`, `SetupPreProvisionedPersistentVolumeClaim`, and `CreateStorageClass`.

## Control Flow
Pod setup methods create a `TestPod` or `TestDeployment`, iterate over configured volumes, provision claims through dynamic or pre-provisioned helpers, and attach either filesystem mounts or raw block devices. Dynamic PVC setup creates a StorageClass, creates a PVC with an optional data source, waits for binding unless `WaitForFirstConsumer` is configured, and validates the PV. Pre-provisioned setup creates a PV first, creates a PVC without a StorageClass, waits for binding, and returns cleanup functions.

## State, Persistence, And Dependencies
The methods persist StorageClasses, PVs, PVCs, Pods, Deployments, and Secrets through Kubernetes APIs. Cleanup functions are returned in creation order and executed by caller defers. Dependencies include the SMB e2e driver interfaces, Kubernetes API types, Ginkgo, and client-go.

## Integration Points
All dynamic provisioning tester files call into this layer. It abstracts driver-specific StorageClass/PV generation behind `driver.DynamicPVTestDriver` and `driver.PreProvisionedVolumeTestDriver`.

## Risks And Test Signals
Because cleanup is caller-owned, missing defers leak resources. `SetupWithDynamicMultipleVolumes` is currently identical to `SetupWithDynamicVolumes`, so divergence risk is low but duplication exists. Test signals are PV/PVC binding validation, pod/deployment readiness, and helper assertions on Kubernetes object properties.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/specs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/testsuites.go -->
# sources/control-plane/csi-driver-smb/test/e2e/testsuites/testsuites.go

## Purpose
This is the shared e2e resource helper library for SMB CSI tests. It wraps Kubernetes StorageClass, PV, PVC, Pod, Deployment, and Secret creation/cleanup, validates dynamic provisioning results, and provides polling/logging utilities.

## Important APIs, Types, And Functions
Key wrappers include `TestStorageClass`, `TestPreProvisionedPersistentVolume`, `TestPersistentVolumeClaim`, `TestDeployment`, `TestPod`, and `TestSecret`. Constructors include `NewTestStorageClass`, `NewTestPersistentVolumeClaim`, `NewTestPersistentVolumeClaimWithDataSource`, `NewTestDeployment`, `NewTestPod`, and `NewTestSecret`. Important methods include `Create`, `Cleanup`, `WaitForBound`, `ValidateProvisionedPersistentVolume`, `DeleteBoundPersistentVolume`, `DeleteBackingVolume`, `WaitForSuccess`, `WaitForRunning`, `WaitForFailure`, `WaitForFailedMountError`, `SetupVolume`, `SetupRawBlockVolume`, `SetupCSIInlineVolume`, `SetupVolumeMountWithSubpath`, `PollForStringInPodsExec`, and `DeletePodAndWait`.

## Control Flow
StorageClass/PV/PVC helpers create resources through client-go and validate expected capacity, access modes, claim references, reclaim policy, mount options, and topology/affinity. PVC cleanup deletes the claim, removes PV finalizers for CSI delete cases as a workaround, waits for PV deletion under Delete reclaim policy, and waits for PVC disappearance. Pod/Deployment helpers generate Linux or Windows pod specs, attach volumes, create resources, wait for pod states, collect logs, and delete resources. Exec polling launches goroutines per pod and aggregates errors.

## State, Persistence, And Dependencies
All state is Kubernetes API state plus backend volume state. `DeleteBackingVolume` calls `smb.Driver.DeleteVolume` directly. The file depends heavily on Kubernetes e2e framework packages, `client-go`, CSI types, SMB driver types, Ginkgo/Gomega, and Kubernetes image utilities.

## Integration Points
The individual testsuite runners and suite specs depend on this file for all resource operations. It integrates with kubelet events for FailedMount detection, kubectl exec via e2e framework, and Deployment utilities.

## Risks And Test Signals
Risks include mutating PV finalizers, hard-coded Windows images/tolerations, fixed timeouts, direct kubelet event reason matching, and helper argument order in `waitForPersistentVolumeClaimDeleted` being easy to misuse. The strongest signals are PVC/PV object validation, pod phase transitions, Deployment readiness, log collection, and exec output polling.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/testsuites/testsuites.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/external-e2e/run.sh -->
# sources/control-plane/csi-driver-smb/test/external-e2e/run.sh

## Purpose
This script runs Kubernetes external storage e2e tests against the SMB CSI driver using an alternate driver name.

## Important APIs, Types, And Functions
Shell functions are `install_ginkgo`, `setup_e2e_binaries`, and `print_logs`. Variables include `PROJECT_ROOT` from `git rev-parse` and `DRIVER=test`.

## Control Flow
The script installs Ginkgo v1.14.0, downloads Kubernetes v1.24.0 e2e binaries, mutates the example StorageClass and metrics service manifests for the alternate driver name, installs the SMB provisioner and driver, registers a trap to print logs, copies the StorageClass to `/tmp/csi/storageclass.yaml`, then runs `ginkgo -p` with external storage focus and selected skips.

## State, Persistence, And Dependencies
It downloads and extracts binaries in the workspace, modifies tracked example YAMLs in place with `sed -i`, creates cluster resources via `make`, and writes `/tmp/csi/storageclass.yaml`. Dependencies include curl, tar, Go, Ginkgo, Make, Kubernetes e2e binaries, kubeconfig, and a working cluster.

## Integration Points
It pairs with `testdriver.yaml`, `deploy/example/storageclass-smb.yaml`, deployment Make targets, and `smb_log.sh`.

## Risks And Test Signals
In-place manifest mutation can dirty the worktree or affect later tests. Pinned old Ginkgo/Kubernetes versions may drift from current dependencies. Signals are external e2e test results and teardown logs from `print_logs`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/external-e2e/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/external-e2e/testdriver.yaml -->
# sources/control-plane/csi-driver-smb/test/external-e2e/testdriver.yaml

## Purpose
This YAML describes the SMB CSI driver to Kubernetes external storage e2e tests.

## Important APIs, Types, And Functions
It defines `ShortName: smb`, a `StorageClass.FromFile` path at `/tmp/csi/storageclass.yaml`, and `DriverInfo` for `test.csi.k8s.io`.

## Control Flow
There is no code flow. The external e2e binary reads this manifest to discover the driver name, storage class source, and capabilities.

## State, Persistence, And Dependencies
The file depends on `run.sh` having copied a valid StorageClass to `/tmp/csi/storageclass.yaml`. Capability flags advertise persistence, exec, multipods, RWX, fsGroup, controller expansion, volume mount group, and PVC data sources; node expansion is disabled.

## Integration Points
It integrates with Kubernetes external storage tests via `--storage.testdriver`.

## Risks And Test Signals
Incorrect capability flags can enable tests the driver cannot satisfy or skip needed coverage. Test signals come from external e2e cases selected by the capability matrix.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/external-e2e/testdriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/run-e2e-test.sh -->
# sources/control-plane/csi-driver-smb/test/run-e2e-test.sh

## Purpose
This script prepares and runs SMB CSI e2e tests for Windows-enabled environments, especially GCE/GKE-style CI.

## Important APIs, Types, And Functions
Functions are `configure_docker` and `setup_e2e`. Variables are `PROJECT_ROOT`, `GCE_PROJECT`, `TEST_WINDOWS=true`, and `REGISTRY=gcr.io/$GCE_PROJECT`.

## Control Flow
The script reads the active gcloud project, configures Docker auth, runs `make e2e-bootstrap`, `make install-smb-provisioner`, and `make create-metrics-svc`, then runs `make e2e-test`.

## State, Persistence, And Dependencies
It changes cluster state by installing the driver/provisioner and metrics service, and changes local Docker auth state. Dependencies include gcloud, Docker, Make, kubeconfig, and a cluster with Windows nodes.

## Integration Points
The script feeds `TEST_WINDOWS` into the Go e2e suite and uses Make targets from the SMB driver repository.

## Risks And Test Signals
It assumes `gcloud config get-value project` is valid and that Docker auth is safe to mutate. Signals are make target exit codes and the downstream Ginkgo/JUnit results.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/run-e2e-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/sanity/params.yaml -->
# sources/control-plane/csi-driver-smb/test/sanity/params.yaml

## Purpose
This YAML provides CSI sanity test volume parameters for the SMB driver.

## Important APIs, Types, And Functions
The single parameter is `source: //127.0.0.1/share`.

## Control Flow
There is no code flow. `csi-sanity` reads the file via `--csi.testvolumeparameters`.

## State, Persistence, And Dependencies
The value assumes a local Samba server exposing a `share` over SMB on localhost, which is provisioned by `test/sanity/run-test.sh`.

## Integration Points
It integrates with SMB driver CreateVolume/NodeStage behavior during CSI sanity tests.

## Risks And Test Signals
The file is intentionally minimal; any additional driver parameters must come from test defaults or secrets. The test signal is whether CSI sanity can create and stage volumes using this source.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/sanity/params.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/sanity/run-test.sh -->
# sources/control-plane/csi-driver-smb/test/sanity/run-test.sh

## Purpose
This script runs CSI sanity tests for the SMB CSI driver against a locally launched Samba container and local SMB plugin process.

## Important APIs, Types, And Functions
Functions are `cleanup`, `install_csi_sanity_bin`, and `provision_samba_server`. Important variables are `endpoint=unix:///tmp/csi.sock`, `nodeid`, normalized `ARCH`, `CSI_SANITY_BIN`, and `skipTests`.

## Control Flow
The script starts a Samba Docker container, installs `csi-sanity` from `kubernetes-csi/csi-test` v5.4.0 if absent, starts `_output/${ARCH}/smbplugin` with the Unix endpoint and node ID, sleeps briefly, then runs `csi-sanity` with secrets, volume parameters, endpoint, and skip regex. Cleanup kills `smbplugin`, removes `csi-test`, and deletes the Samba container.

## State, Persistence, And Dependencies
It creates a Docker container named `samba`, may clone into `$GOPATH/src/github.com/kubernetes-csi/csi-test`, starts a local plugin process, and uses `/tmp/csi.sock`. Dependencies include Docker, Go/GOPATH, Make, the built `_output/<arch>/smbplugin`, and possibly sudo on GitHub Actions.

## Integration Points
It consumes `params.yaml` and `secrets.yaml` and tests the driver through the CSI gRPC endpoint.

## Risks And Test Signals
`pkill -f smbplugin` can kill unrelated local processes. The install path disables modules while cloning csi-test. Fixed Samba image and skipped tests define the expected compatibility envelope. Signals are csi-sanity pass/fail and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/sanity/run-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/sanity/secrets.yaml -->
# sources/control-plane/csi-driver-smb/test/sanity/secrets.yaml

## Purpose
This YAML supplies static SMB credentials for CSI sanity operations.

## Important APIs, Types, And Functions
It defines `NodeStageVolumeSecret` and `CreateVolumeSecret`, each with `username: sanity` and `password: sanitytestpassword`.

## Control Flow
There is no code flow. `csi-sanity` passes these secret maps into the relevant CSI RPCs.

## State, Persistence, And Dependencies
The credentials must match the local Samba container configured by `run-test.sh`.

## Integration Points
The file integrates with the SMB driver's CreateVolume and NodeStageVolume secret handling.

## Risks And Test Signals
These are test-only credentials but are still plain text. Mismatch with the Samba container causes authentication failures in CSI sanity tests. The signal is successful volume creation/staging with supplied secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/sanity/secrets.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/azure/azure_helpers.go -->
# sources/control-plane/csi-driver-smb/test/utils/azure/azure_helpers.go

## Purpose
This package provides Azure helper clients for SMB driver tests that need real Azure resources such as resource groups, virtual machines, NICs, virtual networks, and subnets.

## Important APIs, Types, And Functions
`Client` wraps Azure environment, subscription ID, and resource/compute/network clients. Public functions/methods include `GetAzureClient`, `EnsureResourceGroup`, `DeleteResourceGroup`, `EnsureVirtualMachine`, `EnsureNIC`, `EnsureVirtualNetworkAndSubnet`, and `GetVirtualNetworkSubnet`. Internal helpers are `getOAuthConfig`, `getClient`, and `stringPointer`.

## Control Flow
`GetAzureClient` resolves an Azure cloud environment, creates OAuth config and service-principal token, then constructs authorized Azure SDK clients. Resource creation methods call Azure `CreateOrUpdate`, wait for async futures, and return the resulting resource. VM creation ensures networking first, then creates a DS2_v2 Ubuntu 16.04 VM with hard-coded admin credentials. Resource group creation preserves existing tags and adds CI correlation tags.

## State, Persistence, And Dependencies
State is persisted in Azure: resource groups, VNets, subnets, NICs, and VMs. Dependencies are legacy Azure SDK packages, autorest/adal auth, and environment variables `BUILD_ID` and `JOB_NAME` for tags.

## Integration Points
The helpers are intended for higher-level Azure-backed SMB tests. They integrate with credentials generated by `test/utils/credentials` and Azure cloud selection.

## Risks And Test Signals
Risks include hard-coded weak VM password, old Ubuntu image, broad `10.0.0.0/8` address space, legacy SDK/auth libraries, and teardown warning suppression for known autorest issues. Signals are Azure API errors, future completion, and resource lookup results.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/azure/azure_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/check_driver_pods_restart.sh -->
# sources/control-plane/csi-driver-smb/test/utils/check_driver_pods_restart.sh

## Purpose
This script checks SMB CSI driver pods for restarts in the installed namespace.

## Important APIs, Types, And Functions
It uses `CSI_DRIVER_INSTALLED_NAMESPACE`, defaulting to `kube-system`, and parses `kubectl get pods` output for rows matching `smb`.

## Control Flow
The script lists matching pods, extracts the fourth column as restart counts, prints a warning if any count is nonzero, then prints a success message. The intended nonzero exit is currently commented out.

## State, Persistence, And Dependencies
No persistent state is changed. It depends on kubectl, a current kubeconfig, and table output column positions.

## Integration Points
It is a post-test diagnostic or guard around SMB driver stability.

## Risks And Test Signals
Because the failure exit is disabled, restarts do not fail CI. Parsing table output and grepping `smb` can include unintended pods. The signal is log text only unless the exit is re-enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/check_driver_pods_restart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/create_smbcreds_windows.sh -->
# sources/control-plane/csi-driver-smb/test/utils/create_smbcreds_windows.sh

## Purpose
This script creates the `smbcreds` Kubernetes Secret needed by Windows host-process SMB tests.

## Important APIs, Types, And Functions
It decodes base64-encoded `username` and `pwd` values, deletes any existing `smbcreds` secret in `default`, and recreates it with username, password, and mount options.

## Control Flow
With `set -e`, it decodes credentials, runs `kubectl delete secret smbcreds --ignore-not-found`, then runs `kubectl create secret generic` with literal values.

## State, Persistence, And Dependencies
It mutates the default namespace by replacing a Secret. Dependencies include base64, kubectl, and a valid cluster context.

## Integration Points
`suite_test.go` invokes this for Windows host-process deployments before rewriting SMB source to an Azure File endpoint.

## Risks And Test Signals
The script embeds encoded credential material and uses unquoted shell expansions. It overwrites any existing default `smbcreds`. Signal is kubectl exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/create_smbcreds_windows.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/credentials/credentials.go -->
# sources/control-plane/csi-driver-smb/test/utils/credentials/credentials.go

## Purpose
This package generates a temporary Azure credential JSON file for SMB tests from environment variables or Prow-provided TOML credentials.

## Important APIs, Types, And Functions
Constants define cloud names, default locations, env vars, resource group prefix, and `/tmp/azure.json`. Types are `Config`, `FromProw`, and `Credentials`. Public APIs are `CreateAzureCredentialFile(isAzureChinaCloud bool)` and `DeleteAzureCredentialFile`. Internal functions are `getCredentialsFromAzureCredentials` and `parseAndExecuteTemplate`.

## Control Flow
`CreateAzureCredentialFile` selects public or China env vars, generates a UUID resource group if absent, applies default location, and prefers complete direct env credentials. If incomplete and running in Azure Prow, it reads `AZURE_CREDENTIALS` TOML and converts it to JSON. Otherwise it returns an error listing required env vars. Template execution writes `/tmp/azure.json`.

## State, Persistence, And Dependencies
The main persistent artifact is `/tmp/azure.json`, containing secrets in plain JSON. Dependencies include `go-toml/v2`, `pborman/uuid`, `html/template`, and `testutil` Prow detection.

## Integration Points
Azure helper clients and test setup consume the generated credential file. The file format mirrors Azure File CSI driver credential expectations.

## Risks And Test Signals
Secrets are written to a fixed world-default temp path via `os.Create`, so concurrent tests can collide and file permissions depend on umask. In Azure Prow, `cloud` is based on requested test mode while tenant/client values come from TOML. Signals are returned credential structs, file contents, and cleanup success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/credentials/credentials.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/credentials/credentials_test.go -->
# sources/control-plane/csi-driver-smb/test/utils/credentials/credentials_test.go

## Purpose
This test file verifies Azure credential file generation for both Azure public cloud and Azure China cloud, using both direct environment variables and Prow-style TOML credentials.

## Important APIs, Types, And Functions
Tests are `TestCreateAzureCredentialFileOnAzureChinaCloud` and `TestCreateAzureCredentialFileOnAzurePublicCloud`. Helpers are `withAzureCredentials` and `withEnvironmentVariables`. `fakeAzureCredentials` provides TOML input.

## Control Flow
Each top-level test runs two subtests. The Prow-style path clears direct env vars, writes fake TOML to a temp file, sets `AZURE_CREDENTIALS`, calls `CreateAzureCredentialFile`, then asserts returned fields and JSON file contents. The direct env path sets all env vars and performs the same assertions.

## State, Persistence, And Dependencies
Tests mutate process environment and write `/tmp/azure.json`. They remove both the temp TOML and credential JSON with defers. Dependencies include `testify/assert` and `text/template` for expected JSON.

## Integration Points
The tests cover `credentials.go` and implicitly `testutil.IsRunningInAzureProw` through `AZURE_CREDENTIALS`.

## Risks And Test Signals
Environment variables are not restored with `t.Setenv`, so test ordering or parallelism could leak state. The fixed `/tmp/azure.json` path prevents safe parallel execution. Signals are field equality and `assert.JSONEq` on generated file content.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/credentials/credentials_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/deploy-kind.sh -->
# sources/control-plane/csi-driver-smb/test/utils/deploy-kind.sh

## Purpose
This script provisions a local kind cluster, deploys a Samba server, and installs the SMB CSI driver for tests.

## Important APIs, Types, And Functions
Variables are `KUBERNETES_VERSION=v1.18.8` and `KUBECONFIG=$HOME/.kube/config`. It downloads kind v0.9.0 and kubectl for the configured Kubernetes version.

## Control Flow
The script installs binaries with sudo, creates a kind cluster, writes kubeconfig, waits for DNS, creates `smbcreds`, deploys the example SMB server, waits for it, installs the driver, and waits for controller and node pods to become Ready.

## State, Persistence, And Dependencies
It mutates `/usr/local/bin`, creates a kind cluster, changes `$HOME/.kube`, and creates Kubernetes resources. Dependencies include curl, sudo, kind, kubectl, and repository deployment manifests.

## Integration Points
It prepares the environment expected by SMB e2e tests and example storage classes.

## Risks And Test Signals
Pinned old Kubernetes/kind versions may be incompatible with current host tooling. Readiness waits parse JSONPath strings and loop indefinitely. Signals are kubectl readiness checks and final installation log.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/deploy-kind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/deploy-minikube.sh -->
# sources/control-plane/csi-driver-smb/test/utils/deploy-minikube.sh

## Purpose
This script provisions a local minikube cluster and installs the SMB CSI driver and example Samba server.

## Important APIs, Types, And Functions
It exports minikube environment variables, sets `KUBECONFIG`, and pins Kubernetes v1.18.1 plus minikube v1.8.1.

## Control Flow
The script downloads kubectl and minikube, initializes kube/minikube directories, starts minikube with `--vm-driver=none`, updates context, adjusts ownership for Travis, waits for DNS, creates SMB credentials and server, installs the driver, and waits for controller/node readiness.

## State, Persistence, And Dependencies
It mutates host binaries, `$HOME/.kube`, `$HOME/.minikube`, local minikube state, and cluster resources. Dependencies include sudo, curl, minikube, kubectl, and Travis-style filesystem assumptions.

## Integration Points
It is an older CI/local setup path for the same e2e environment used by SMB tests.

## Risks And Test Signals
The script assumes a `travis` user, rootless none-driver behavior, and old Kubernetes versions. Infinite readiness loops can hang. Signals are command exit codes and readiness loops reaching Ready.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/deploy-minikube.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/get_smb_svc_public_ip.sh -->
# sources/control-plane/csi-driver-smb/test/utils/get_smb_svc_public_ip.sh

## Purpose
This script extracts the public IP of the `smb-server` service from the default namespace.

## Important APIs, Types, And Functions
It runs `kubectl get svc smb-server -n default | grep smb | awk '{print $4}'`.

## Control Flow
With `set -e`, any kubectl or grep failure exits the script. Successful output is the fourth column of kubectl table output.

## State, Persistence, And Dependencies
No state is changed. It depends on kubectl, service existence, and table column layout.

## Integration Points
`suite_test.go` uses this for Windows clusters to rewrite SMB source to `//<public-ip>/share`.

## Risks And Test Signals
The table parser is brittle and does not wait for load balancer ingress. A pending IP can propagate into tests. Signal is stdout containing the IP or script failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/get_smb_svc_public_ip.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/restart_driver_daemonset.sh -->
# sources/control-plane/csi-driver-smb/test/utils/restart_driver_daemonset.sh

## Purpose
This script restarts SMB CSI node daemonsets by deleting and reapplying Linux and Windows node manifests.

## Important APIs, Types, And Functions
It uses `kubectl delete -f ./deploy/csi-smb-node.yaml`, `kubectl delete -f ./deploy/csi-smb-node-windows.yaml`, sleeps 15 seconds, then applies both manifests.

## Control Flow
With strict shell settings, delete failures other than ignored not-found failures stop execution. After deletion and sleep, both daemonsets are reapplied.

## State, Persistence, And Dependencies
It mutates cluster daemonsets and pods. Dependencies include kubectl, current working directory at repository root, and deployment manifests.

## Integration Points
The restart-driver e2e tests can inject this script as `RestartDriverFunc`.

## Risks And Test Signals
It does not wait for new daemonset rollout after apply, leaving readiness to callers. Applying Windows manifests on clusters without Windows support may fail depending on manifest validity. Signal is kubectl exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/restart_driver_daemonset.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/smb_log.sh -->
# sources/control-plane/csi-driver-smb/test/utils/smb_log.sh

## Purpose
This diagnostic script prints Kubernetes node, pod, driver, Samba server, service, metrics, and crash/restart information for SMB e2e runs.

## Important APIs, Types, And Functions
`cleanup` traps errors and exits 0. Variables are `NS=kube-system`, `CONTAINER=smb`, and `DRIVER=smb` or the first argument. It uses kubectl, xargs, awk, and curl.

## Control Flow
The script prints node and default namespace status, Samba server logs/events, kube-system pod status, controller logs, restart/crash details with previous container logs, Linux node logs, Windows node events/logs, services, and metrics from `csi-$DRIVER-controller` service IP on port 29644.

## State, Persistence, And Dependencies
No cluster state is intentionally changed. It depends on label conventions `app=csi-$DRIVER-*`, container name `smb`, service naming, kubectl access, and network access to metrics.

## Integration Points
The e2e suite and external e2e script call this in teardown/traps to collect failure evidence.

## Risks And Test Signals
The ERR trap masks diagnostic failures by exiting 0. Several pipelines can fail when no pods match unless guarded. Metrics IP extraction assumes service ClusterIP in column four. Signals are logs and events printed to test artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/smb_log.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/testutil/testutil.go -->
# sources/control-plane/csi-driver-smb/test/utils/testutil/testutil.go

## Purpose
This package contains small test helpers for OS-specific expected errors, Prow environment detection, and working directory paths.

## Important APIs, Types, And Functions
`TestError` contains `WindowsError` and `DefaultError`. Methods/functions include `GetExpectedError`, `AssertError`, `IsRunningInProw`, `IsRunningInGcpProw`, `IsRunningInAzureProw`, private `isWindows`, and `GetWorkDirPath`.

## Control Flow
Error helpers choose Windows-specific expectations only when running on Windows and a Windows error is provided. Prow helpers check for `GOOGLE_APPLICATION_CREDENTIAL` or `AZURE_CREDENTIALS`. `GetWorkDirPath` calls `os.Getwd` and appends a subdirectory.

## State, Persistence, And Dependencies
No persistent state is changed. It reads environment variables and runtime GOOS.

## Integration Points
`credentials.go` uses Azure Prow detection. Other tests can use `TestError` to normalize platform-specific assertions.

## Risks And Test Signals
`reflect.DeepEqual` on errors is stricter than comparing messages or `errors.Is`. Prow detection depends on env var names, including singular `GOOGLE_APPLICATION_CREDENTIAL`. Signals are helper return values in unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/utils/testutil/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/.prow.sh -->
# sources/control-plane/csi-lib-utils/.prow.sh

## Purpose
This script is the Prow entrypoint for csi-lib-utils CI jobs.

## Important APIs, Types, And Functions
It sets a default `CSI_PROW_TESTS=unit`, sources `release-tools/prow.sh`, and calls `main`.

## Control Flow
The only control flow is default variable assignment followed by delegated execution in release-tools.

## State, Persistence, And Dependencies
State and behavior are controlled by the sourced release-tools script and environment variables. This file itself does not mutate repository state.

## Integration Points
Prow jobs invoke it to run the standardized Kubernetes CSI release-tools test pipeline.

## Risks And Test Signals
The script assumes `release-tools/prow.sh` exists and is compatible. Signals are produced by the delegated `main`, primarily unit test/build output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/Makefile -->
# sources/control-plane/csi-lib-utils/Makefile

## Purpose
This Makefile defines the basic build and test integration for csi-lib-utils.

## Important APIs, Types, And Functions
`CMDS=` indicates no command binaries. `all` runs `go build` over non-vendor packages. It includes `release-tools/build.make` and maps `test` to `test-logcheck`.

## Control Flow
Make delegates most targets to release-tools. The local `all` target builds all packages from `go list ./... | grep -v vendor`.

## State, Persistence, And Dependencies
It produces Go build cache artifacts and depends on Go modules/vendor state plus release-tools make fragments.

## Integration Points
CI and local workflows use it for standardized build/test behavior.

## Risks And Test Signals
Backtick command substitution and grep filtering are simple but less precise than `go list` package filters. The `test` target explicitly enables contextual logging checks. Signals are Go build/test/logcheck failures.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/accessmodes/access_modes.go -->
# sources/control-plane/csi-lib-utils/accessmodes/access_modes.go

## Purpose
This package maps Kubernetes PersistentVolume access modes to CSI `VolumeCapability.AccessMode` values, with special handling for drivers that support `SINGLE_NODE_MULTI_WRITER`.

## Important APIs, Types, And Functions
Public API is `ToCSIAccessMode(pvAccessModes, supportsSingleNodeMultiWriter)`. Internal functions are `toCSIAccessMode`, `toSingleNodeMultiWriterCapableCSIAccessMode`, and `uniqueAccessModes`.

## Control Flow
The public function selects one of two mapping tables. Both deduplicate Kubernetes access modes, reject `ReadWriteOncePod` combined with anything else, let `ReadWriteMany` take precedence, reject `ReadOnlyMany` combined with `ReadWriteOnce`, and map remaining single modes. With single-node-multi-writer support, `ReadWriteOnce` maps to `SINGLE_NODE_MULTI_WRITER` and `ReadWriteOncePod` maps to `SINGLE_NODE_SINGLE_WRITER`; otherwise both map to `SINGLE_NODE_WRITER`.

## State, Persistence, And Dependencies
The code is stateless. Dependencies are Kubernetes core/v1 access mode constants and CSI protobuf enums.

## Integration Points
CSI sidecars and drivers use it while translating Kubernetes PV semantics into CSI volume capabilities.

## Risks And Test Signals
Ordering is intentionally lost through deduplication. `ReadWriteMany` precedence means invalid combinations involving RWX are accepted as multi-writer. Errors include the original mode slice for diagnostics. Unit tests cover supported and rejected combinations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/accessmodes/access_modes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/accessmodes/access_modes_test.go -->
# sources/control-plane/csi-lib-utils/accessmodes/access_modes_test.go

## Purpose
This unit test verifies Kubernetes-to-CSI access mode translation for both normal drivers and drivers supporting `SINGLE_NODE_MULTI_WRITER`.

## Important APIs, Types, And Functions
The single test `TestToCSIAccessMode` uses table-driven cases with `pvAccessModes`, expected CSI mode, expected error, and capability flag.

## Control Flow
Each case calls `ToCSIAccessMode`, verifies whether an error is expected, and compares the returned mode for non-error cases.

## State, Persistence, And Dependencies
The test is stateless and depends on Go testing plus Kubernetes/CSI constants.

## Integration Points
It directly covers `access_modes.go`.

## Risks And Test Signals
The table covers empty input, RWO, ROX, RWX, RWOP, ROX+RWO, and ROX+RWOP for both capability modes. It does not explicitly test duplicate modes or RWX combined with other modes. The signal is pass/fail of expected mapping and error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/accessmodes/access_modes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/config/config.go -->
# sources/control-plane/csi-lib-utils/config/config.go

## Purpose
This package builds Kubernetes REST configs for CSI sidecars using either an explicit kubeconfig or in-cluster configuration, then applies standard API QPS/burst settings.

## Important APIs, Types, And Functions
Public API is `BuildConfig(kubeconfig string, opts standardflags.SidecarConfiguration)`. Internal `buildConfig` chooses `clientcmd.BuildConfigFromFlags` or `rest.InClusterConfig`.

## Control Flow
`BuildConfig` obtains a config, returns early on error, then sets `config.QPS` and `config.Burst` from `opts.KubeAPIQPS` and `opts.KubeAPIBurst`.

## State, Persistence, And Dependencies
The code is stateless. Dependencies are `client-go/rest`, `clientcmd`, and csi-lib-utils `standardflags`.

## Integration Points
Sidecars can use this after parsing standard flags to construct clients with consistent throttling.

## Risks And Test Signals
There are no tests in this subset. Risks are that zero QPS/burst values from opts overwrite client-go defaults, so callers must pass initialized standard options. Errors come directly from kubeconfig or in-cluster config loading.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/connection/connection.go -->
# sources/control-plane/csi-lib-utils/connection/connection.go

## Purpose
This package creates CSI gRPC client connections with secret-sanitized logging, optional metrics, optional OpenTelemetry tracing, configurable timeout, and Unix-socket connection-loss behavior.

## Important APIs, Types, And Functions
Public APIs include `SetMaxGRPCLogLength`, `Connect`, deprecated `ConnectWithoutMetrics`, options `OnConnectionLoss`, `ExitOnConnectionLoss`, `WithTimeout`, `WithMetrics`, `WithOtelTracing`, interceptor `LogGRPC`, `ExtendedCSIMetricsManager.RecordMetricsClientInterceptor`, and `RecordMetricsServerInterceptor`. Types include `Option`, `AdditionalInfo`, `AdditionalInfoKeyType`, and `ExtendedCSIMetricsManager`.

## Control Flow
`Connect` prepends a 30-second timeout and metrics option when provided, then calls `connect`. The internal function builds insecure blocking dial options with 1-second max backoff and no idle timeout, applies unary interceptors, normalizes absolute paths to `unix://`, and installs a custom Unix dialer that detects first connection loss and optionally disables reconnect. It dials in a goroutine and logs "Still connecting" every 10 seconds until dial completion. `LogGRPC` logs sanitized requests/replies and caps response length when configured. Metrics interceptors measure duration and record gRPC status, with optional migration label from context.

## State, Persistence, And Dependencies
Package-level state is `maxLogChar`. `ExitOnConnectionLoss` writes `/dev/termination-log` and exits via klog. Dependencies include grpc, klog, OpenTelemetry grpc instrumentation, csi-lib-utils metrics, and protosanitizer.

## Integration Points
CSI sidecars use this to talk to drivers. Metrics integrate with `metrics.CSIMetricsManager`; logging integrates with `protosanitizer` to avoid secret leakage.

## Risks And Test Signals
Blocking dial plus timeout controls startup behavior; `WithTimeout(0)` can wait indefinitely. Connection-loss callback is only supported for Unix addresses. The dialer uses closure state that assumes serialized dial behavior. Tests cover Unix path/prefix, timeout, reconnect/disconnect modes, metrics, and tracing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/connection/connection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/connection/connection_test.go -->
# sources/control-plane/csi-lib-utils/connection/connection_test.go

## Purpose
This test file validates CSI gRPC connection setup, Unix reconnect behavior, metrics interceptors, and OpenTelemetry tracing support.

## Important APIs, Types, And Functions
Helpers are `tmpDir` and `startServer`. Tests include `TestConnect`, `TestConnectUnix`, `TestConnectWithoutMetrics`, `TestConnectWithOtelTracing`, `TestWaitForServer`, `TestTimeout`, `TestReconnect`, `TestDisconnect`, `TestExplicitReconnect`, `TestConnectMetrics`, and `TestConnectWithOtelGrpcInterceptorTraces`.

## Control Flow
Tests create temporary Unix sockets and lightweight grpc servers, then call `Connect` with different options. Reconnect tests stop and restart servers and assert gRPC status codes. Metrics tests invoke CSI Identity calls and compare gathered Prometheus output, ignoring duration sum diffs. Tracing tests enable OpenTelemetry stats handling and assert basic span context behavior.

## State, Persistence, And Dependencies
Tests create temp directories, Unix sockets, grpc servers, and metrics registries. Dependencies include CSI protobuf servers/clients, grpc status/connectivity, klog test context, Kubernetes metrics testutil, and testify.

## Integration Points
The tests cover `connection.go` plus `metrics` integration through client/server interceptors.

## Risks And Test Signals
Timing-sensitive tests use sleeps and epsilon comparisons around reconnect and delayed server startup. Signals are connection state, grpc status codes, callback counts, metrics output, and absence of unexpected errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/connection/connection_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/deprecatedflags/deprecatedflags.go -->
# sources/control-plane/csi-lib-utils/deprecatedflags/deprecatedflags.go

## Purpose
This package lets binaries register flags that are accepted for backward compatibility but ignored with a warning.

## Important APIs, Types, And Functions
Public APIs are `Add(name string) bool` and `AddBool(name string) bool`. Internal type `deprecated` implements `flag.Value` and `IsBoolFlag`.

## Control Flow
`Add` and `AddBool` register a `deprecated` value with the global `flag` package and return true for compatibility with global variable initialization patterns. When the flag is set, `Set` writes a warning to stderr and returns nil. `IsBoolFlag` marks boolean flags so `-flag` syntax is accepted.

## State, Persistence, And Dependencies
State is registered in the process-global flag set. It writes warnings to stderr. Dependencies are only standard library packages.

## Integration Points
Sidecars can use this when removing old flags without breaking command lines immediately.

## Risks And Test Signals
There are no tests in this subset. The warning omits a trailing newline, which can merge with other stderr output. The package uses global `flag` instead of an injected FlagSet.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/deprecatedflags/deprecatedflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/leaderelection/leader_election.go -->
# sources/control-plane/csi-lib-utils/leaderelection/leader_election.go

## Purpose
This package wraps client-go leader election for CSI sidecars, including lease-based locking, optional health checks, standard flag integration, labels on lease objects, and release-on-cancel support.

## Important APIs, Types, And Functions
Constructors are `NewLeaderElection` and `NewLeaderElectionWithLeases`. Fluent setters include `WithIdentity`, `WithNamespace`, `WithLeaseDuration`, `WithRenewDeadline`, `WithRetryPeriod`, `WithReleaseOnCancel`, `WithLabels`, and `WithContext`. Other APIs include `PrepareHealthCheck`, `Run`, `RunWithLeaderElection`, `defaultLeaderElectionIdentity`, `sanitizeName`, `inClusterNamespace`, and `adaptCheckToHandler`.

## Control Flow
`Run` defaults identity to hostname and namespace from pod env/serviceaccount/default, starts an event broadcaster, creates a labeled Lease resource lock, builds `LeaderElectionConfig`, and calls `leaderelection.RunOrDie`. On leadership start it invokes the caller's run function; on loss it logs and exits. `RunWithLeaderElection` either calls `run` directly or creates a separate clientset, configures leader election from `standardflags.SidecarConfiguration`, optionally registers health checks, and runs election.

## State, Persistence, And Dependencies
Persistent state is the Kubernetes Lease object and Events in the selected namespace. Dependencies include client-go leader election, resource locks, Kubernetes events, klog, standardflags, and HTTP muxes.

## Integration Points
CSI sidecars call `RunWithLeaderElection` around their main loop. Health checks are exposed at `/healthz/leader-election`.

## Risks And Test Signals
`sanitizeName` assumes non-empty input and appends `X` when the sanitized name ends in a dash. Loss of leadership exits the process. There is limited unit coverage here; most behavior depends on client-go. Tests cover name sanitization only.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/leaderelection/leader_election.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/leaderelection/leader_election_test.go -->
# sources/control-plane/csi-lib-utils/leaderelection/leader_election_test.go

## Purpose
This unit test verifies the `sanitizeName` helper used for leader election lock names and identities.

## Important APIs, Types, And Functions
The only test is `Test_sanitizeName`, with table cases for unchanged names, invalid characters, and trailing invalid characters.

## Control Flow
Each case calls `sanitizeName` and compares the output string to the expected sanitized form.

## State, Persistence, And Dependencies
The test is stateless and uses only Go testing.

## Integration Points
It covers the helper used before creating Kubernetes resource locks.

## Risks And Test Signals
Coverage is narrow: it does not test empty strings, namespace detection, health checks, lease labels, or leader election callbacks. Signal is strict string equality.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/leaderelection/leader_election_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/metrics/metrics.go -->
# sources/control-plane/csi-lib-utils/metrics/metrics.go

## Purpose
This package provides Prometheus/Kubernetes metrics management for CSI sidecars and plugins, centered on CSI operation latency histograms labeled by driver, method, gRPC status, and optional custom labels.

## Important APIs, Types, And Functions
Public interface `CSIMetricsManager` exposes registry access, `RecordMetrics`, `WithLabelValues`, `HaveAdditionalLabel`, `WithAdditionalRegistry`, `SetDriverName`, `RegisterToServer`, and `RegisterPprofToServer`. Options include `WithSubsystem`, `WithStabilityLevel`, `WithLabelNames`, `WithLabels`, `WithMigration`, `WithProcessStartTime`, and `WithCustomRegistry`. Constructors are `NewCSIMetricsManagerForSidecar`, `NewCSIMetricsManager`, `NewCSIMetricsManagerForPlugin`, and `NewCSIMetricsManagerWithOptions`. Helpers include `VerifyMetricsMatch` and `getErrorCode`.

## Control Flow
The constructor initializes a kube registry, applies options, optionally registers `process_start_time_seconds`, builds a histogram vector with default/additional labels, sets the driver name or `unknown-driver`, registers metrics, and initializes gatherers. `RecordMetrics` builds label values and observes duration. `WithLabelValues` returns immutable-ish wrappers that accumulate values and reject undefined or overwritten labels. HTTP registration exposes gathered metrics and pprof handlers.

## State, Persistence, And Dependencies
State lives in the manager instance: registry, driver name, label definitions, gatherers, and histogram vector. Dependencies include Prometheus client, Kubernetes component-base metrics, grpc status/codes, net/http/pprof, and standard time/string utilities.

## Integration Points
`connection.go` uses this through interceptors. CSI sidecars/plugins use it to serve `/metrics` and optionally pprof endpoints.

## Risks And Test Signals
Registering process start time by default can conflict with other registries, so an option disables it. Additional registry mutation appends gatherers in place. Missing label values become empty strings. Unit tests cover metrics shape, labels, endpoint registration, pprof, and process start metric existence.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/metrics/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/metrics/metrics_test.go -->
# sources/control-plane/csi-lib-utils/metrics/metrics_test.go

## Purpose
This test file validates csi-lib-utils metrics construction, label handling, HTTP serving, pprof registration, and process start time registration.

## Important APIs, Types, And Functions
Tests include `TestRecordMetrics`, `TestFixedLabels`, `TestVaryingLabels`, `TestTwoVaryingLabels`, `TestVaryingLabelsBackfill`, `TestVaryingLabels_NameError`, `TestVaryingLabels_OverwriteError`, `TestCombinedLabels`, `TestRecordMetrics_NoDriverName`, `TestRecordMetrics_Negative`, `TestRegisterToServer_Noop`, `TestRegisterPprofToServer_AllEndpointsAvailable`, and `TestProcessStartTimeMetricExist`.

## Control Flow
The tests create managers with different constructors/options, record fixed durations, and compare gathered Prometheus text against expected histograms. Label tests check fixed sorted labels, varying label wrappers, missing-value backfill, undefined label errors, and overwrite errors. HTTP tests use `httptest` with a mux to verify `/metrics` and pprof paths.

## State, Persistence, And Dependencies
Tests use in-memory registries and HTTP recorders. Dependencies include Kubernetes component-base metrics testutil, grpc status/codes, net/http/httptest, and Go testing.

## Integration Points
They cover `metrics.go` directly and support confidence for connection interceptors that rely on the same metric manager.

## Risks And Test Signals
Expected metric text is verbose and sensitive to bucket/label ordering. Time sum values are deterministic because tests use fixed durations. Signals are gather comparisons, expected errors for bad labels, HTTP status 200, pprof index content, and presence of `process_start_time_seconds`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/metrics/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer.go -->
# sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer.go

## Purpose
This package provides a safe `fmt.Stringer` wrapper for logging CSI protobuf messages as one-line JSON while stripping fields marked with the CSI secret protobuf extension.

## Important APIs, Types, And Functions
Public API is `StripSecrets(msg interface{}) fmt.Stringer`. Internal type `stripSecrets` implements `String`. Helpers are `stripSingleValue`, `stripValue`, `stripMessage`, and `isCSI1Secret`.

## Control Flow
`StripSecrets` returns a lightweight wrapper. When stringified, scalar values are marshaled directly; protobuf messages are reflected field-by-field. Secret fields are replaced with `"***stripped***"`. Non-secret message, enum, list, and map values are recursively converted into JSON-marshalable Go values. Unknown enum values are emitted numerically.

## State, Persistence, And Dependencies
The package is stateless and does not mutate the original message. Dependencies include CSI protobuf definitions and `google.golang.org/protobuf` reflection.

## Integration Points
`connection.LogGRPC` uses this for request/response logging to avoid leaking CSI secrets.

## Risks And Test Signals
`isCSI1Secret` type-asserts the extension value to bool, so it assumes CSI 1.0+ descriptors with the extension available. Unknown protobuf fields are not emitted through normal reflection, which is a privacy advantage but may omit debugging detail. Tests cover current CSI, future secret fields, maps/lists/oneofs, scalar values, immutability, and benchmarks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer_test.go -->
# sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer_test.go

## Purpose
This test file validates secret stripping and JSON formatting for CSI protobuf messages and scalar values.

## Important APIs, Types, And Functions
`TestStripSecrets` is the main test. Benchmarks are `BenchmarkStrip` and `BenchmarkStripLarge`. `testReq` is a representative CSI CreateVolumeRequest.

## Control Flow
The test builds current CSI and generated future-spec messages with secret maps, secret scalars, repeated secret fields, map values, oneof secret fields, nested secrets, and unknown enum values. It compares `StripSecrets(...).String()` and fmt `%v`/`%+v` output to expected JSON, confirms the original object string is unchanged, and verifies `%#v` does not reveal the chosen secret name/value. It also marshals a future message into current CSI type to verify unknown fields do not leak.

## State, Persistence, And Dependencies
Tests are in-memory. Dependencies include CSI protobufs, generated `protosanitizer/test/csitest`, protobuf marshal/unmarshal, and testify.

## Integration Points
The tests validate the safety property relied on by gRPC logging in `connection`.

## Risks And Test Signals
Expected JSON depends on protobuf reflection field names and map ordering as produced by JSON marshal. Benchmarks provide performance signals for regular and large topology-heavy requests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/test/Makefile -->
# sources/control-plane/csi-lib-utils/protosanitizer/test/Makefile

## Purpose
This Makefile generates Go bindings for a test protobuf schema used by protosanitizer tests to simulate future CSI secret-field layouts.

## Important APIs, Types, And Functions
Targets include `all`, `$(GOBIN)/protoc-gen-go`, `$(PROTOC)`, generated `$(CSI_GO)`, `build`, `clean`, and `clobber`. Variables configure GOPATH, `PROTOC_VER=25.2`, OS/arch mapping, download URL, and paths.

## Control Flow
The Makefile ensures `protoc-gen-go` is installed from the parent module, downloads a platform-specific protoc zip into `.protoc`, unzips it, and runs protoc over `csitest.proto` with source-relative Go output into the `csitest` package. `clean` removes generated Go package files and `clobber` also removes downloaded protoc.

## State, Persistence, And Dependencies
It writes `.protoc/`, installs `protoc-gen-go` into `GOBIN`, and generates `csitest/csitest.pb.go`. Dependencies include curl, unzip, Go, protoc releases, and the parent `go.mod`.

## Integration Points
The generated package is imported by `protosanitizer_test.go`.

## Risks And Test Signals
The download URL depends on platform naming and external GitHub availability. `GOBIN` must be set or Go's install path behavior must be acceptable. Signal is successful generation of `csitest.pb.go`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/test/Makefile -->
