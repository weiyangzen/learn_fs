# Research: subset-b-000365

Grouped research for NFS CSI release/e2e test helpers and SMB CSI CI plus Helm chart history. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned per-file output.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-shellcheck.sh -->
## sources/control-plane/csi-driver-nfs/release-tools/verify-shellcheck.sh

Purpose: verifies every tracked shell script in the NFS CSI repository with ShellCheck. It resolves `release-tools/util.sh`, accepts an optional root directory, gathers `*.sh` files while excluding generated/private, `.git`, and `vendor` paths, and also filters git-ignored files.

Important APIs and flow: `join_by` builds the comma-separated disabled rule list, `create_container` starts a long-lived `koalaman/shellcheck-alpine:v0.6.0` container, and `remove_container` cleans it through a release-tools trap. The script prefers a host `shellcheck` only when its reported version exactly matches `0.6.0`; otherwise it runs `docker exec` for each script.

State is limited to the fixed Docker container name `k8s-shellcheck` and the in-memory `errors` array. Dependencies include Docker, git, ShellCheck, Bash process substitution, and Kubernetes release-tool trap helpers. Risks are stale pinned ShellCheck version/image, collision with another container named `k8s-shellcheck`, and unchecked behavior when Docker is unavailable. Test signal is CI/static presubmit failure with collected ShellCheck output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-shellcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-spelling.sh -->
## sources/control-plane/csi-driver-nfs/release-tools/verify-spelling.sh

Purpose: runs the `misspell` checker over git-tracked repository files, excluding vendor content, to catch common spelling mistakes in source, scripts, and manifests. It accepts an optional root directory and defaults to the repository above `release-tools`.

Important flow: the script creates a temporary directory, installs `github.com/client9/misspell/cmd/misspell@v0.3.4` there when no `misspell` binary is on `PATH`, then runs `git ls-files -z | grep -z -v vendor | xargs -0 misspell --` into an error log. Non-empty errors are prefixed with `error:` and cause exit code 1.

State and persistence are temporary only through `mktemp -d`; the exit trap removes the directory. Dependencies are Go module installation, git, grep with null handling, xargs, and misspell. Risks include use of any host misspell version without version validation, broad text scope causing false positives, and vendor exclusion based on substring matching. Test signal is a presubmit/static spelling failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-subtree.sh -->
## sources/control-plane/csi-driver-nfs/release-tools/verify-subtree.sh

Purpose: checks that a directory managed through `git subtree` has not received local non-merge commits. It is intended for vendored release-tool copies or other upstream mirrored directories where changes should only arrive through subtree merge commits.

Important flow: the script requires one directory argument, then runs `git log -n1 --remove-empty --format=format:%H --no-merges -- "$DIR"`. If any non-merge commit touched the path, it prints the non-merge log for that directory and exits with failure; otherwise it reports the directory as a clean upstream copy.

State is entirely git history; no files are modified. Dependencies are POSIX shell and git. Risks include false negatives when a merge commit contains hand edits, false positives when legitimate local patches are expected, and reliance on local shallow history being complete enough. Test signal is a release verification failure when subtree-managed content drifts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-subtree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-vendor.sh -->
## sources/control-plane/csi-driver-nfs/release-tools/verify-vendor.sh

Purpose: verifies Go module metadata and optional `vendor/` content are up to date. It only runs in repositories with `go.mod`, then compares the working tree after `go mod tidy` and, when present, `go mod vendor`.

Important flow: in Prow presubmit jobs it can skip the check when dependency-relevant files and import blocks have not changed. Otherwise it executes `GO111MODULE=on go mod tidy`, fails if `go.mod` or `go.sum` changed, then refreshes `vendor` and fails if vendor status or diff changed.

State and persistence risk are important: the script intentionally mutates module and vendor files during verification and uses git status/diff to detect whether those changes were needed. Dependencies include Go modules, git, and Prow variables such as `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA`. Risks include unbound environment references in local `nounset`-free shell, shallow diff assumptions, and expensive vendor rewrites. Test signal is exact diff output for stale dependency artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/driver/driver.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/driver/driver.go

Purpose: defines the e2e driver abstraction used by NFS CSI storage tests. `PVTestDriver` composes dynamic provisioning and pre-provisioned volume capabilities so higher-level test suites can create StorageClasses and PVs without hard-coding driver implementation details.

Important APIs are `DynamicPVTestDriver.GetDynamicProvisionStorageClass`, `PreProvisionedVolumeTestDriver.GetPersistentVolume`, `GetPreProvisionStorageClass`, and shared helper `getStorageClass`. The helper fills default reclaim policy `Delete`, default binding mode `Immediate`, and always enables `AllowVolumeExpansion`.

State is Kubernetes object state represented in memory until tests call the API server. Dependencies are core/v1 and storage/v1 Kubernetes APIs. Integration points are `nfs_driver.go` and every testsuite setup method in `test/e2e/testsuites`. Risks include defaulting expansion to true for all StorageClasses and passing caller-provided parameter maps by reference. Test signal is indirect through dynamic provisioning, reclaim, resize, and topology scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/driver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/driver/nfs_driver.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/driver/nfs_driver.go

Purpose: implements the generic e2e PV driver interfaces for the NFS CSI driver. `InitNFSDriver` reads `NFS_CSI_DRIVER` and falls back to `nfs.DefaultDriverName`, making tests usable with alternate provisioner names.

Important APIs: `NFSDriver`, `normalizeProvisioner`, `GetDynamicProvisionStorageClass`, `GetPreProvisionStorageClass`, `GetPersistentVolume`, and `GetParameters`. StorageClass methods create generated names from namespace and driver name; PV creation builds a CSI PV with size, fs type, volume handle, optional node stage secret, and the legacy `pv.kubernetes.io/provisioned-by` annotation.

State is generated Kubernetes object metadata and environment-dependent driver name. Dependencies include the NFS package constants, Kubernetes core/storage APIs, resource parsing, and klog. Risks include a typo in the pre-provisioned PV generateName, inconsistent normalization in `GetPreProvisionStorageClass`, and unused/default Azure-like `skuName` parameters. Test signal comes from all e2e suites that instantiate `driver.InitNFSDriver`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/driver/nfs_driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/dynamic_provisioning_test.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/dynamic_provisioning_test.go

Purpose: declares the main Ginkgo e2e scenarios for NFS dynamic provisioning. It builds `PodDetails`, `VolumeDetails`, and typed testsuite structs to exercise StorageClass parameters, mount options, read-only mounts, pod restart persistence, reclaim policy behavior, multiple PVs, subpath mounts, inline volumes, delete-retain/archive modes, and resizing.

Important flow: `BeforeEach` runs `test/utils/check_driver_pods_restart.sh`, then stores the framework client and namespace. Each `It` case constructs a testsuite such as `DynamicallyProvisionedCmdVolumeTest`, `CollocatedPodTest`, `DeletePodTest`, `ReclaimPolicyTest`, or `ResizeVolumeTest` and calls `Run(ctx, cs, ns)`.

State is cluster-level: StorageClasses, PVCs, PVs, Pods, Deployments, and the test NFS server share. Dependencies include `e2e_suite_test.go` globals for storage parameters and driver/server constants. Risks include long-running pods requiring cleanup defers, hard-coded `default` secret namespace, Windows command conversion only for selected commands, and a restart check that logs but no longer fails. Test signal is high because this file is the scenario matrix for real provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/dynamic_provisioning_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/e2e_suite_test.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/e2e_suite_test.go

Purpose: bootstraps and tears down the NFS CSI e2e suite. It configures Kubernetes e2e flags, ensures `KUBECONFIG` exists, creates an in-process NFS CSI driver and controller server, installs an NFS server plus Helm driver deployment, and registers the Ginkgo suite.

Important APIs and globals include storage parameter maps for default, zero mount permissions, subDir, retain, archive, and archive subDir modes; `testCmd`; `execTestCmd`; `handleFlags`; `TestMain`; `TestE2E`; and `convertToPowershellCommandIfNecessary`. `BeforeSuite` runs `make install-nfs-server` and `make e2e-bootstrap`, then starts `nfsDriver.Run(false)` in a goroutine. `AfterSuite` prints logs, tears down Helm, and tests install/uninstall scripts.

State includes environment variables `NODE_ID`, `TEST_WINDOWS`, `KUBECONFIG`, a unix socket under `/tmp`, and cluster resources installed by make targets. Risks include process-wide `os.Chdir`, goroutine lifetime after tests, hard-coded NFS service DNS name, and shell command failures aborting the suite. Test signal is the full integration lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/e2e_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_cmd_volume_tester.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_cmd_volume_tester.go

Purpose: implements the simplest dynamic provisioning test pattern: create StorageClass/PVC/PV resources, mount each PVC into a pod, and require the pod command to exit successfully.

Important API: `DynamicallyProvisionedCmdVolumeTest.Run`. For each `PodDetails`, it calls `SetupWithDynamicVolumes`, defers all cleanup functions, creates the pod, defers pod cleanup, and waits for success through Kubernetes e2e pod helpers.

State is managed through Kubernetes objects created by `specs.go` and `testsuites.go`. Dependencies include the dynamic driver interface, Ginkgo logging, client-go, and core/v1 namespace types. Risks include cleanup order being controlled by deferred LIFO calls, single failure aborting remaining pods, and success relying on container exit rather than checking persisted data beyond the command. Test signal is direct for basic mount and read/write behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_cmd_volume_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go

Purpose: verifies multiple dynamically provisioned NFS-backed pods can run concurrently, optionally forcing later pods onto the same node as the first one.

Important API: `DynamicallyProvisionedCollocatedPodTest.Run`. It creates each pod with dynamic PVCs, optionally sets `NodeSelector` to `{"name": nodeName}` after the first pod, creates the pod, waits for running state, and records `Spec.NodeName` for later colocation.

State is live running pods and PVC/PV resources left until deferred cleanup. Dependencies are `PodDetails.SetupWithDynamicVolumes`, `TestPod.SetNodeSelector`, and Kubernetes scheduler/node labels. Risks include assuming nodes carry a `name` label matching `Spec.NodeName`, not verifying actual file writes after pods run, and cleanup being delayed until all pods are running. Test signal is useful for RWX-like concurrent mount scheduling but weaker for data correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_delete_pod_tester.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_delete_pod_tester.go

Purpose: validates persistence across pod replacement in a Deployment. It provisions one PVC, creates a Deployment that writes data, optionally verifies command output inside the pod, deletes that pod, waits for the replacement, and verifies accumulated data again.

Important types are `DynamicallyProvisionedDeletePodTest` and `PodExecCheck`. `Run` composes `PodDetails.SetupDeployment`, `TestDeployment.Create`, `WaitForPodReady`, `PollForStringInPodsExec`, and `DeletePodAndWait`. For restart verification it expects the second read to contain the expected string twice.

State is a Deployment, its managed pod, and the bound PVC/PV. Dependencies include e2e kubectl exec helpers and deployment helpers from `testsuites.go`. Risks include assuming one replica and one pod, string matching rather than exact file semantics, and shell command differences across Linux/Windows. Test signal directly covers volume persistence through pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_delete_pod_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_inline_volume.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_inline_volume.go

Purpose: verifies CSI inline ephemeral NFS volumes can be mounted into pods with explicit server, share, mount options, and read-only setting.

Important API: `DynamicallyProvisionedInlineVolumeTest.Run`. It loops over `PodDetails`, calls `SetupWithCSIInlineVolumes` rather than creating StorageClasses or PVCs, creates the pod, defers pod cleanup, and waits for the command to succeed.

State is pod-local CSI volume state; there is no PVC/PV persistence in this path. Dependencies include Kubernetes `CSIVolumeSource`, NFS driver name from `testsuites.go`, Ginkgo, and client-go. Risks include using `nfs.DefaultDriverName` inside the helper instead of the test driver's possibly overridden name, empty cleanup function slices, and mount option string formatting. Test signal covers inline volume lifecycle and command-level read/write success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_inline_volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_pod_with_multiple_pv.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_pod_with_multiple_pv.go

Purpose: validates one pod can consume multiple dynamically provisioned PVs. It is used by the top-level test that creates six PVCs and mounts them into a single pod.

Important API: `DynamicallyProvisionedPodWithMultiplePVsTest.Run`. For each pod definition, it calls `SetupWithDynamicMultipleVolumes`, defers all PVC/StorageClass cleanup, creates the pod, defers pod cleanup, and waits for command success.

State is a set of StorageClasses/PVCs/PVs and a single consuming pod. Dependencies include `specs.go` logic that decides between filesystem mounts and raw block device setup based on `VolumeMode`. Risks include creating one StorageClass per volume, which is heavier than needed, and validating only command success on the first mount path unless the command checks all mounts. Test signal covers multi-volume attachment/mount plumbing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_pod_with_multiple_pv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_read_only_volume_tester.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_read_only_volume_tester.go

Purpose: verifies a pod mounting a dynamic PVC read-only cannot write to that mount. The top-level scenario uses a `touch` command and expects failure.

Important API: `DynamicallyProvisionedReadOnlyVolumeTest.Run`. It provisions dynamic volumes, creates the pod, waits for pod failure using `TestPod.WaitForFailure`, reads pod logs, and asserts they contain `Read-only file system`.

State is the failed pod plus PVC/PV resources cleaned by defers. Dependencies include Gomega assertions, Kubernetes pod log retrieval, and the e2e framework. Risks include platform-specific error text, commands that fail before reaching the write operation, and reliance on failure phase rather than container exit details. Test signal is direct for Kubernetes readOnly volume mount enforcement and driver mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_read_only_volume_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go

Purpose: validates dynamic PV behavior for `Delete` and `Retain` reclaim policies. It provisions volumes, deletes the PVC through the common cleanup path, then performs policy-specific checks.

Important API: `DynamicallyProvisionedReclaimPolicyTest.Run`. For `Delete`, `tpvc.Cleanup` waits for PV deletion. For `Retain`, the test waits for the PV to enter `Released`, deletes the bound PV manually, and intentionally skips backing NFS directory cleanup because the in-process controller cannot resolve the test cluster NFS service.

State is PV/PVC lifecycle state and, for Retain, potentially retained backing directories. Dependencies include the NFS controller server type, though actual `DeleteBackingVolume` is commented out. Risks include leaked backing data for Retain tests, reliance on PV phase transitions, and one-volume-at-a-time execution. Test signal covers Kubernetes reclaim policy integration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_resize_volume_tester.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_resize_volume_tester.go

Purpose: verifies dynamic NFS PVC expansion is reflected in PVC request state and PV capacity. It first mounts and exercises the volume, then increases the requested storage by one GiB.

Important API: `DynamicallyProvisionedResizeVolumeTest.Run`. It creates a pod with dynamic volumes, waits for command success, reads the first PVC from the pod volume list, modifies `Spec.Resources.Requests["storage"]`, updates the PVC, sleeps 30 seconds, then compares the new PVC request and PV capacity.

State is Kubernetes PVC/PV storage size state. Dependencies include client-go, resource quantities, and the StorageClass default `AllowVolumeExpansion=true`. Risks include fixed sleep instead of polling resize conditions, string-based PV/PVC size comparison with `"Gi"` appended, ignoring errors on PV get, and only checking the first volume. Test signal covers controller expansion at a smoke-test level.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_resize_volume_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_volume_subpath_tester.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_volume_subpath_tester.go

Purpose: verifies dynamically provisioned PVCs can be mounted through a Kubernetes `subPath`. It uses the same success-command pattern as the basic volume tester but mounts each volume with `SubPath: "testSubpath"`.

Important API: `DynamicallyProvisionedVolumeSubpathTester.Run`. It delegates setup to `PodDetails.SetupWithDynamicVolumesWithSubpath`, defers StorageClass/PVC cleanup, creates the pod, defers pod cleanup, and waits for success.

State includes a PVC/PV and pod volume mounts with subPath. Dependencies include `TestPod.SetupVolumeMountWithSubpath`, kubelet subPath handling, and dynamic provisioning. Risks include the hard-coded subpath name being reused across volumes, command coverage usually hitting only one mount, and subPath directory creation semantics differing across Kubernetes versions. Test signal targets a known integration surface between CSI mounts and kubelet subPath.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_volume_subpath_tester.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/specs.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/specs.go

Purpose: provides declarative test input structs and setup methods that translate scenario data into StorageClasses, PVCs, Pods, Deployments, inline CSI volumes, raw block devices, and subPath mounts.

Important types are `PodDetails`, `VolumeMode`, `VolumeMountDetails`, `VolumeDeviceDetails`, `DataSource`, and `VolumeDetails`. Important methods include `SetupDynamicPersistentVolumeClaim`, `SetupWithDynamicVolumes`, `SetupWithCSIInlineVolumes`, `SetupDeployment`, `SetupWithDynamicMultipleVolumes`, and `SetupWithDynamicVolumesWithSubpath`.

State is the cleanup function list returned to caller and Kubernetes resources created through `testsuites.go` helpers. Dependencies include the e2e driver interface, storage/v1 binding modes, core/v1 typed data sources, and Ginkgo logging. Risks include one StorageClass per volume, limited data source fields, binding-mode paths that skip PV validation for WaitForFirstConsumer until pod use, and inline volumes ignoring the provided driver instance. Test signal is indirect but central because every dynamic provisioning scenario uses these builders.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/specs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/testsuites.go -->
## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/testsuites.go

Purpose: implements the shared Kubernetes object lifecycle for the NFS e2e tests. It creates and deletes StorageClasses, PVCs, Pods, Deployments, validates bound PVs, polls pod exec output, removes finalizers, and exposes CSI-specific cleanup hooks.

Important APIs include `TestStorageClass`, `TestPersistentVolumeClaim`, `TestPod`, `TestDeployment`, `NewTestPersistentVolumeClaim`, `generatePVC`, `WaitForBound`, `ValidateProvisionedPersistentVolume`, `NewTestPod`, `SetupVolume`, `SetupRawBlockVolume`, `Create`, `WaitForSuccess`, `WaitForRunning`, `NewTestDeployment`, `PollForStringInPodsExec`, `DeletePodAndWait`, `DeleteBackingVolume`, `SetupVolumeMountWithSubpath`, and `SetupCSIInlineVolume`.

State is live cluster state plus cached object pointers on the test structs. Dependencies include client-go, Kubernetes e2e framework helpers, deployment/pod/pv utilities, `kubectl` exec wrapper, CSI `DeleteVolumeRequest`, and NFS controller server. Risks include patching away PV finalizers as a workaround, process-level `context.Background` for backing deletion, fixed timeouts, direct field indexing into node affinity, and Linux node selectors in pod/deployment templates. Test signal is broad because failures here reflect lifecycle and cleanup correctness across all scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/e2e/testsuites/testsuites.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/external-e2e/run.sh -->
## sources/control-plane/csi-driver-nfs/test/external-e2e/run.sh

Purpose: runs Kubernetes external storage e2e tests against the NFS CSI driver under an alternate driver name. It installs Ginkgo, downloads Kubernetes v1.24.0 e2e binaries, installs the driver and NFS server, then invokes `e2e.test` with the external testdriver manifest.

Important flow: `setup_e2e_binaries` downloads and extracts `kubernetes-test-linux-amd64.tar.gz`, sets Helm overrides for `test.csi.k8s.io`, rewrites example StorageClass and SnapshotClass manifests with `sed`, copies them to `/tmp/csi`, and runs `make e2e-bootstrap` plus `make install-nfs-server`. `print_logs` runs example verification and driver log collection on exit.

State includes modified working-tree example manifests, `/tmp/csi` files, downloaded Kubernetes test binaries, Helm-installed cluster resources, and external test process state. Dependencies are curl, tar, sed, make, Ginkgo v1, Kubernetes external storage tests, and kubeconfig. Risks include destructive in-place `sed`, pinned old Kubernetes test version, broad focus/skip regex drift, and cleanup only printing logs. Test signal covers conformance-like external storage capabilities.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/external-e2e/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/external-e2e/testdriver.yaml -->
## sources/control-plane/csi-driver-nfs/test/external-e2e/testdriver.yaml

Purpose: configures Kubernetes external storage tests for the NFS CSI driver when run as `test.csi.k8s.io`. It points the external test suite at generated StorageClass and SnapshotClass inputs and declares supported driver capabilities.

Important content: `StorageClass.FromFile` uses `/tmp/csi/storageclass.yaml`, `SnapshotClass.FromName` expects an existing snapshot class, and `DriverInfo` advertises NFS fs type plus persistence, exec, multipods, RWX, fsGroup, PVC/snapshot data sources, controller expansion, and node expansion. `InlineVolumes` supplies server and share attributes for an inline NFS mount.

State is declarative; the external test binary reads it. Dependencies are the `/tmp/csi` files created by `run.sh`, the NFS service DNS name, and external e2e storage test schemas. Risks include over-advertising capabilities that may not hold on all clusters, hard-coded `default` namespace service, and snapshot class ambiguity. Test signal is the external conformance matrix selected by `run.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/external-e2e/testdriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/sanity/params.yaml -->
## sources/control-plane/csi-driver-nfs/test/sanity/params.yaml

Purpose: supplies the CSI sanity test volume parameters for a local NFS server. The file maps `server` to `127.0.0.1` and `share` to `/`, matching the local Docker NFS server launched by `run-test.sh`.

State is declarative and read by `csi-sanity` through `--csi.testvolumeparameters`. Dependencies are the NFS plugin's parameter schema and the local server setup. Risks include assuming loopback works from the plugin process namespace and using the root export for all sanity test volumes. Test signal is direct input for CSI RPC sanity tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/sanity/params.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/sanity/run-test.sh -->
## sources/control-plane/csi-driver-nfs/test/sanity/run-test.sh

Purpose: runs CSI sanity tests against a locally started `nfsplugin` process and Dockerized NFS server. It installs the CSI sanity binary, provisions a local NFS server, starts the plugin on a unix socket, and executes selected sanity cases.

Important flow: `cleanup` kills `nfsplugin`, removes `csi-test`, and deletes Docker container `nfs`. `install_csi_sanity_bin` clones `kubernetes-csi/csi-test` v5.4.0 into GOPATH with modules disabled and runs `make install`. `provision_nfs_server` installs `nfs-common` and runs `itsthenetwork/nfs-server-alpine`.

State includes GOPATH source checkout, Docker container `nfs`, `nfsshare` directory, `/tmp/csi.sock`, and a background plugin process. Dependencies include apt, Docker, git, make, local `bin/nfsplugin`, and csi-sanity. Risks include `pkill -f nfsplugin` killing unrelated processes, unpinned Docker image `latest`, root package installation, and skipped sanity cases masking unsupported idempotency/capability paths. Test signal is CSI interface-level sanity coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/sanity/run-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/utils/check_driver_pods_restart.sh -->
## sources/control-plane/csi-driver-nfs/test/utils/check_driver_pods_restart.sh

Purpose: checks kube-system NFS driver pods for restart counts before e2e tests. It prints restart status and warns if any pod matching `nfs` has a nonzero restart count.

Important flow: `kubectl get pods -n kube-system | grep nfs | awk '{print $4}'` extracts restart counts and loops over them. The former failure path is commented out, so the script currently logs restart detection but always prints success.

State is only live Kubernetes pod status. Dependencies are kubectl, grep, awk, and pod table column layout. Risks include matching unrelated NFS pods, no failure despite restarts, brittle parsing when kubectl output changes, and `set -e` causing no-match grep to fail the script. Test signal is weak because it is informational unless shell pipeline failure occurs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/utils/check_driver_pods_restart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/utils/nfs_log.sh -->
## sources/control-plane/csi-driver-nfs/test/utils/nfs_log.sh

Purpose: collects useful cluster and NFS CSI driver diagnostics at the end of e2e runs. It prints nodes, default namespace pods, kube-system pods, controller logs, and node logs.

Important flow: it defaults `NS=kube-system`, `CONTAINER=nfs`, and `DRIVER=nfs`, with an optional driver name argument. It selects controller pods by `app=csi-$DRIVER-controller` and node pods by `app=csi-$DRIVER-node`, then pipes pod names into `kubectl logs --prefix -c nfs`.

State is read-only cluster log/status data. Dependencies are kubectl, awk, xargs, standard app labels, and container name `nfs`. Risks include xargs running kubectl with no pod names, missing logs from restarted containers because `--previous` is not used, and hard-coded container/namespace assumptions. Test signal is diagnostic rather than pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/utils/nfs_log.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/utils/testutil/testutil.go -->
## sources/control-plane/csi-driver-nfs/test/utils/testutil/testutil.go

Purpose: provides a small test utility for building an absolute path under the current working directory. `GetWorkDirPath` reads `os.Getwd`, fails the test if it cannot, and appends the requested directory using `os.PathSeparator`.

State is process current working directory only. Dependencies are Go `os`, `fmt`, and `testing`. Integration points are unit or integration tests that need fixture paths relative to the test working directory. Risks include string concatenation instead of `filepath.Join`, behavior depending on caller working directory, and immediate `t.Fatalf` preventing caller-level recovery. Test signal is indirect through any tests using this helper.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/test/utils/testutil/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.cloudbuild.sh -->
## sources/control-plane/csi-driver-smb/.cloudbuild.sh

Purpose: is the Google Cloud Build entrypoint for the SMB CSI repository. It sources `release-tools/prow.sh` and delegates to `gcr_cloud_build`, which centralizes Kubernetes CSI image build and publish behavior.

There are no local functions beyond the script body. State and persistence are controlled by the sourced release-tools code and Cloud Build environment variables. Dependencies include Bash, the checked-out `release-tools` subtree, and whatever registry credentials and build metadata Cloud Build provides.

Risks are mostly delegated: a missing or incompatible `release-tools/prow.sh` breaks the build, and shellcheck suppresses SC1091 because the source path is repository-relative. Test signal is CI image build success or failure in the release/prow pipeline.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/dependabot.yaml -->
## sources/control-plane/csi-driver-smb/.github/dependabot.yaml

Purpose: configures Dependabot updates for the SMB CSI repo. It checks Go modules at `/`, GitHub Actions workflows at `/`, and Docker dependencies under `/cmd/smbplugin/`.

Important behavior: all ecosystems run daily and cap open PRs at one. PRs receive dependency, no-release-note, and ok-to-test labels; Docker updates also get `kind/cleanup` and run at 01:00 Asia/Shanghai.

State is GitHub Dependabot service state and generated pull requests. Dependencies are GitHub's `gomod`, `github-actions`, and `docker` ecosystem parsers. Risks include serialized update throughput from the one-PR cap, noisy daily Docker updates, and labels coupling to repository automation. Test signal appears as Dependabot PRs that then run the normal CI matrix.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/codeql-analysis.yml -->
## sources/control-plane/csi-driver-smb/.github/workflows/codeql-analysis.yml

Purpose: runs CodeQL analysis for Go on pushes, pull requests, and a daily schedule. It grants read permissions for actions/contents and write permission for security events.

Important flow: it sets up Go `^1.18`, checks out code with pinned actions, initializes CodeQL for language `go`, runs `make all` as the autobuild step, then invokes CodeQL analysis. The matrix is single-language but keeps `fail-fast: false`.

State is GitHub Actions workspace plus uploaded SARIF/security results. Dependencies include `make all`, vendored Go dependencies, CodeQL action v4, and setup-go. Risks include old Go version relative to current module needs, build failures blocking analysis, and analysis only covering Go. Test signal is GitHub security analysis completion and alerts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/codespell.yml -->
## sources/control-plane/csi-driver-smb/.github/workflows/codespell.yml

Purpose: checks common spelling mistakes on every push and pull request through `codespell-project/actions-codespell`.

Important behavior: it checks filenames, skips git metadata, the workflow file itself, image assets, checksum files, vendor, and `go.sum`, and ignores known SMB-related words `browseable` and `ro`.

State is limited to the GitHub Actions checkout. Dependencies are pinned checkout and codespell actions. Risks include false positives in generated/vendor-like files not skipped, false negatives from broad skip patterns, and maintaining the ignore word list as SMB terminology evolves. Test signal is a spelling-check CI job.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/darwin.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/darwin.yaml

Purpose: validates macOS build and package-level unit tests. It runs on push and pull request using `macos-latest`.

Important flow: setup Go `^1.16`, checkout, run `make smb-darwin` to cross/build the driver binary for Darwin, then run `go test -v -race ./pkg/...`.

State is only build artifacts under `_output` and Go test cache. Dependencies include macOS runner support, Makefile target `smb-darwin`, vendored modules, and package tests that are portable to Darwin. Risks include old Go version, package tests accidentally depending on Linux/Windows SMB utilities, and macOS runner image drift. Test signal is cross-platform compile and unit test success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/darwin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/linux.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/linux.yaml

Purpose: runs the main Linux unit, container build, sanity, and coverage workflow for SMB CSI on push and pull request.

Important flow: it installs `cifs-utils` and `procps`, runs `go test -race -covermode=atomic -coverprofile=profile.cov ./pkg/...`, builds the container with Docker CLI experimental enabled, runs `make` and `make sanity-test` with `GITHUB_ACTIONS=true`, installs `goveralls`, and uploads coverage using the GitHub token.

State includes local packages, coverage profile, built image, sanity test resources, and coverage upload. Dependencies include cifs tools, Docker, Makefile targets, Go `^1.16`, and secrets. Risks include old Go version, privileged/container assumptions in sanity tests, coverage upload flakiness, and external package install drift. Test signal is the broadest Linux CI pass.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/linux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/pluto.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/pluto.yaml

Purpose: detects deprecated or removed Kubernetes API versions in deployment manifests. It runs on push and pull request.

Important flow: checkout, install the pinned FairwindsOps Pluto action, run `pluto detect-files -d deploy --ignore-deprecations --ignore-removals`, then run `pluto detect-files -d deploy/example` without those ignores.

State is read-only manifest scanning. Dependencies are the Pluto action and the deploy/example trees. Risks include ignores making the main deploy folder less strict, scan scope excluding charts, and action version drift despite pinning. Test signal is CI failure when manifests use unsupported API versions according to Pluto.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/pluto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/publish-helm-oci.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/publish-helm-oci.yaml

Purpose: publishes release container images and the Helm chart to GHCR on GitHub Release publish or manual dispatch. It covers Linux images, Windows images, Windows HostProcess image, multi-arch manifest, Helm OCI packaging, and a job summary.

Important jobs: `validate` accepts only `v<major>.<minor>.<patch>` and emits stripped chart version; `build-linux` builds Go binaries and Docker images for amd64, arm64, ppc64le, and arm/v7; `build-windows` builds 1809 and ltsc2022 Windows images on matching runners; `build-windows-hp` publishes a HostProcess image; `manifest` creates and annotates a multi-platform Docker manifest; `publish-helm` validates chart directory/version, lints, logs into GHCR, packages, pushes, and verifies the chart.

State includes GHCR packages, Docker manifests, Helm OCI artifacts, and release summary output. Dependencies are pinned GitHub actions, Go 1.25.10, Docker/Buildx/QEMU, jq, Helm 3.17.0, and `GITHUB_TOKEN` package write access. Risks include version/chart directory mismatch, Windows base image os.version lookup failure, duplicated build logic with Makefile, and tag immutability. Test signal is release publication success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/publish-helm-oci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/shellcheck.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/shellcheck.yaml

Purpose: runs ShellCheck over repository shell scripts on master/release pushes, version tags, and pull requests to master/release branches.

Important behavior: it uses the pinned `ludeeus/action-shellcheck` action with warning severity, checks scripts together, emits GCC format, disables SC2034, and ignores `vendor`, `release-tools`, and `hack`.

State is read-only CI analysis. Dependencies are checkout and the action's bundled ShellCheck. Risks include warning-level severity possibly allowing risky scripts, ignored `hack` and `release-tools` scripts escaping coverage, and global SC2034 suppression. Test signal is static shell lint output in GitHub Actions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/shellcheck.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/static.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/static.yaml

Purpose: runs Go static analysis on push and pull request. It uses `golangci-lint-action` v7 with golangci-lint v2.10.

Important flow: setup Go `^1.19`, checkout, and run golangci-lint with explicit enabled linters: errcheck, govet, unused, ineffassign, staticcheck, revive, misspell, asciicheck, bodyclose, dogsled, durationcheck, errname, and forbidigo, with a 30 minute timeout.

State is analysis-only. Dependencies are `.golangci.yml`, the action, and Go module resolution. Risks include mismatch between inline `-E` linter list and config default, long runtime on large vendor trees if exclusions drift, and Go version lag. Test signal is lint failure before runtime tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/static.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/trivy.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/trivy.yaml

Purpose: scans the SMB CSI container image for OS and library vulnerabilities on master pushes and pull requests.

Important flow: setup Go 1.25.11, checkout, build a local image by setting `PUBLISH=true`, `REGISTRY=test`, `IMAGE_VERSION=latest`, and running `make container`, then run pinned `aquasecurity/trivy-action` against `test/smb-csi:latest` with table output and exit code 1 for all severities.

State includes the local Docker image and Trivy DB cache. Dependencies are Docker, Makefile container target, Trivy action, and the public ECR Trivy DB repository. Risks include scanning only the Linux image, high noise from LOW/UNKNOWN severity failures, and network/DB availability. Test signal is vulnerability gate failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/ubuntu-e2e.yml -->
## sources/control-plane/csi-driver-smb/.github/workflows/ubuntu-e2e.yml

Purpose: defines an Ubuntu e2e workflow for SMB CSI, but the job is explicitly disabled with `if: false`.

If enabled, it would setup Go `^1.16`, checkout, run `make deploy-kind`, build the default target, and run `make e2e-test`. State would include a kind cluster and e2e deployment resources, but none are created while disabled.

Dependencies are dormant: kind deployment utilities, Makefile e2e target, and cluster-capable GitHub runners. Risks are mostly coverage-related: Ubuntu e2e tests do not currently protect pull requests, so Linux runtime integration issues depend on other CI or external systems. Test signal is intentionally absent until the job is re-enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/ubuntu-e2e.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/windows.yaml -->
## sources/control-plane/csi-driver-smb/.github/workflows/windows.yaml

Purpose: validates Windows build and package tests for SMB CSI on push and pull request.

Important flow: matrix uses Go 1.16.x and `windows-latest`, runs `make smb-windows`, starts CSI Proxy v1.1.1 as a background PowerShell job with kubelet path set to the workspace, waits 30 seconds, lists named pipes, and runs `go test -v -race ./pkg/...`.

State includes a background CSI Proxy process, extracted proxy binaries, Windows named pipes, and `_output/amd64/smbplugin.exe`. Dependencies are Windows runner Docker/PowerShell environment, Azure Edge download, Makefile target, and package tests. Risks include fixed sleep for proxy readiness, unpinned runner OS behavior, external binary download, and old Go version. Test signal covers Windows-specific package code and CSI proxy integration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.github/workflows/windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.golangci.yml -->
## sources/control-plane/csi-driver-smb/.golangci.yml

Purpose: configures golangci-lint v2 behavior for the SMB CSI repository. It sets default linters to none, enables `staticcheck` in the config, and enables `gofmt` as a formatter.

Important settings: `staticcheck` runs `S*` checks; `depguard` defines a rule for non-test files allowing standard library, `k8s.io`, `sigs.k8s.io`, and `github.com` imports; exclusions use lax generated-file detection plus common false-positive presets and two revive text exclusions for v2 rule differences.

State is analysis configuration consumed by the static workflow and local lint runs. Dependencies are golangci-lint v2 schema and linter names. Risks include config enabling only staticcheck while workflow CLI adds many linters, depguard settings being inert if depguard is not enabled, and text-based revive exclusions hiding broader issues. Test signal is lint determinism.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/Makefile -->
## sources/control-plane/csi-driver-smb/Makefile

Purpose: is the main developer and CI command surface for building, testing, packaging, deploying, and publishing the SMB CSI driver. It imports `release-tools/build.make`, sets image/version metadata, builds binaries for Linux, Darwin, and Windows, builds Docker images, pushes manifests, and runs e2e/bootstrap helpers.

Important targets include `all`, `update`, `verify`, `unit-test`, `sanity-test`, `integration-test`, `deploy-kind`, `e2e-test`, `e2e-bootstrap`, `e2e-teardown`, `smb`, `smb-armv7`, `smb-windows`, `smb-darwin`, `container`, `container-linux`, `container-linux-armv7`, `container-windows`, `container-windows-hostprocess`, `container-all`, `push-manifest`, `push-latest`, `install-smb-provisioner`, and `create-metrics-svc`.

State and persistence include `_output` binaries, Docker images/manifests, Helm releases, Kubernetes secrets/resources, and registry pushes. Dependencies are Go, Docker Buildx/QEMU, jq, Helm, kubectl, release-tools, and environment flags such as `CI`, `PUBLISH`, `TEST_WINDOWS`, and `WINDOWS_USE_HOST_PROCESS_CONTAINERS`. Risks include duplicated release logic with the GHCR workflow, mutable defaults like `IMAGE_VERSION`, privileged binfmt setup, and chart version `latest` defaults. Test signal is all CI workflows that invoke Make targets.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/artifacthub-repo.yml -->
## sources/control-plane/csi-driver-smb/charts/artifacthub-repo.yml

Purpose: declares Artifact Hub repository metadata for the SMB CSI Helm chart repository. It stores the repository ID and owner contact.

State is declarative metadata consumed by Artifact Hub indexing. Dependencies are Artifact Hub schema expectations and the maintainer email remaining valid. Risks are low but operational: stale ownership data can break repository claiming or notifications. Test signal is external Artifact Hub repository validation rather than in-repo CI.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/artifacthub-repo.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/index.yaml -->
## sources/control-plane/csi-driver-smb/charts/index.yaml

Purpose: is the Helm repository index for packaged SMB CSI charts. It maps chart name `csi-driver-smb` to historical versions, package URLs in the GitHub raw chart tree, digests, app versions, and created timestamps.

Important behavior is declarative: Helm clients use `apiVersion: v1`, `entries`, and `generated` to resolve chart packages. The index includes current 1.x releases, older v0.x releases, and two `v0.0.0`/latest entries pointing at latest or v1.9.0 packages.

State is persisted release metadata and SHA digests. Dependencies are Helm repo index format and package files matching URLs/digests. Risks include duplicate version semantics around `v0.0.0`, mixed `v`-prefixed and unprefixed versions in newer releases, stale raw GitHub URLs, and digest mismatch after package regeneration. Test signal is `helm repo update/search/install` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/index.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/Chart.yaml

Purpose: declares the mutable latest SMB CSI Helm chart. It uses chart API v1, chart name `csi-driver-smb`, description, appVersion `latest`, and version `v0.0.0`.

State is chart metadata read by Helm packaging, linting, and install commands. Dependencies include templates and values in the same chart directory. Risks include using a synthetic `v0.0.0` version for latest, which can confuse SemVer sorting and release workflow version validation, and appVersion `latest` tying deployments to mutable image tags when values are not overridden. Test signal is Helm lint/package/install behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: optionally deploys CSI Proxy as a Windows HostProcess DaemonSet when `.Values.windows.csiproxy.enabled` is true. This supports non-HostProcess SMB node deployments that need named pipe access to host filesystem and SMB operations.

Important template behavior: it renders a DaemonSet with rolling update, release namespace, labels, optional tolerations/affinity, Windows HostProcess security context, host networking, Windows nodeSelector, priority class, pull secrets, and a `csi-proxy` container. Image resolution supports either baseRepo-relative repositories or absolute repositories.

State is a cluster DaemonSet and its Windows host process pods. Dependencies include Windows nodes, HostProcess support, csi-proxy image, values for username/nodeSelector, and helper templates `smb.labels` and `smb.pullSecrets`. Risks include disabled default while needed for non-HostProcess mode, privileged host access, and Windows HostProcess version compatibility. Test signal is Helm render/install and Windows e2e mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the Linux controller Deployment for SMB CSI. It hosts external provisioner, external resizer, liveness probe, and the `smb` controller service sharing a unix CSI socket.

Important behavior: supports explicit affinity or `runOnControlPlane`/`runOnMaster` node affinity, host networking, DNS policy, service account, Linux nodeSelector, security context, tolerations, pull secrets, and resource values. Sidecars use leader election in the release namespace, extra create metadata, VolumeAttributesClass disabled, retry tuning, and volume-in-use resize handling disabled. The driver container exposes metrics, liveness, driver name, endpoint, and working mount directory.

State is Deployment pods plus ephemeral socket `emptyDir`. Dependencies include Kubernetes sidecar images, SMB plugin image, RBAC, service accounts, and host networking. Risks include privileged controller container, Recreate strategy causing control-plane downtime, feature-gate pinning, and tight coupling to sidecar CLI flags. Test signal is Helm lint/render and dynamic provisioning/resize tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the cluster-scoped `CSIDriver` object for SMB. It identifies the driver name, optional labels, and driver behavior to Kubernetes.

Important spec fields: `attachRequired: false`, `podInfoOnMount: true`, and `volumeLifecycleModes` containing `Persistent` plus conditional `Ephemeral` when `.Values.feature.enableInlineVolume` is true.

State is a Kubernetes storage.k8s.io/v1 CSIDriver object. Dependencies include values for driver name/labels and cluster support for CSI inline volumes. Risks include driver name changes breaking existing PVs/StorageClasses, enabling inline volume RBAC requirements, and cluster-scoped object ownership conflicts across releases. Test signal is Helm install and Kubernetes storage tests that require CSIDriver discovery.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

Purpose: renders the preferred Windows node DaemonSet when Windows support and HostProcess containers are enabled. It runs the SMB plugin directly on the host network as `NT AUTHORITY\SYSTEM`.

Important behavior: an init container creates the kubelet plugin directory, then `node-driver-registrar` registers the CSI socket and `smbplugin.exe` runs with node id, driver name, get-volume-stats, remove-mapping, and `--enable-windows-host-process=true`. It selects Windows nodes, uses HostProcess security context, release service account, pull secrets, and Windows-specific resources.

State is host-level plugin socket directories and DaemonSet pods. Dependencies include Windows HostProcess support, image tag with `-windows-hp`, kubelet path values, and RBAC/service account. Risks include high host privilege, path escaping mistakes, no liveness probe sidecar in this mode, and image tag coupling to release pipeline. Test signal is Windows e2e and Helm render/install.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the legacy/non-HostProcess Windows SMB node DaemonSet when Windows is enabled and `.Values.windows.useHostProcessContainers` is false.

Important behavior: it runs liveness probe, node-driver-registrar, and `smb` containers using Windows paths under `C:\csi` and kubelet plugin directories. The SMB container mounts kubelet directories and CSI Proxy named pipes for filesystem and SMB APIs, including v1 and v1beta1 compatibility pipes, and exposes a health endpoint.

State includes hostPath mounts, named pipe mounts, plugin socket paths, and Windows DaemonSet pods. Dependencies include external CSI Proxy availability, Windows kubelet path, service account, and sidecar images. Risks include CSI Proxy pipe compatibility, hostPath path escaping, security context limitations on Windows, and needing `.Values.windows.csiproxy.enabled` or a manually installed proxy. Test signal is Windows mount/unmount e2e coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux SMB node DaemonSet. It deploys liveness probe, node-driver-registrar, and privileged SMB node plugin on Linux nodes.

Important behavior: the template supports node affinity, host networking, DNS policy, node service account, Linux nodeSelector, priority class, pod security context, tolerations, pull secrets, and resource blocks. The registrar can expose its own liveness endpoint. The SMB container sets driver name, endpoint, node id, get-volume-stats, and Kerberos prefix; it mounts `/csi`, kubelet with bidirectional propagation, and optional Kerberos cache directory.

State includes kubelet plugin and registration host paths, mount propagation state, optional Kerberos cache host path, and DaemonSet pods. Dependencies include privileged containers, kubelet path, sidecar images, RBAC, and Linux CIFS tooling in the image. Risks include privileged host mount access, Kerberos directory misconfiguration, socket path conflicts, and liveness settings causing restarts during slow mounts. Test signal is Linux e2e and node registration success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service accounts and RBAC for SMB CSI controller and node components when enabled by values. It covers external provisioner, external resizer, and optional node secret access for inline volumes.

Important resources: controller and node ServiceAccounts, `smb-external-provisioner-role` with PV/PVC/StorageClass/CSI node/node/event/lease/secret reads, provisioner binding, `smb-external-resizer-role` with PV/PVC status/event/lease privileges, resizer binding, and conditional node secret role/binding when inline volumes are enabled.

State is cluster-scoped RBAC plus namespace service accounts. Dependencies include release namespace, sidecar permission requirements, and `.Values.rbac.name`. Risks include broad secret `get` permissions, cluster role naming collisions across releases, missing RBAC when service accounts are externally managed, and inline-volume secret access exposure. Test signal is provisioning/resizing failures with RBAC denial events.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/storageclass.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/storageclass.yaml

Purpose: optionally renders one or more StorageClass objects from `.Values.storageClasses`. By default the values file comments out examples, so no StorageClass is created unless users configure the list.

Important behavior: for each item it sets name, shared chart labels, optional annotations, provisioner from `.Values.driver.name`, arbitrary parameters, default reclaim policy `Delete`, default volumeBindingMode `Immediate`, default `allowVolumeExpansion: true` unless explicitly set, and optional mountOptions.

State is cluster-scoped StorageClass resources. Dependencies include SMB driver name, user-provided secret names/namespaces, SMB source paths, and mount options. Risks include leaking credential references into chart values, unsafe mount options, default expansion enabled, and multiple releases trying to manage the same StorageClass names. Test signal is Helm render plus actual dynamic provisioning behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/values.yaml

Purpose: defines the default configuration surface for the latest SMB CSI Helm chart. It controls image repositories/tags, service accounts, RBAC names, driver features, controller and node scheduling/resources, Linux/Windows modes, labels/annotations, priority class, security context, and optional StorageClasses.

Important values include sidecar tags for provisioner, resizer, liveness probe, registrar, CSI Proxy, `feature.enableGetVolumeStats`, `feature.enableInlineVolume`, controller metrics/liveness ports, Linux Kerberos cache settings, Windows HostProcess defaults, Windows remove-mapping behavior, and commented StorageClass examples with SMB source and credential references.

State is declarative input to all templates. Dependencies include image registry conventions where repositories beginning with `/` are joined with `baseRepo`, cluster support for HostProcess and RuntimeDefault seccomp, and sidecar CLI compatibility. Risks include mutable `canary` plugin tag, Windows enabled by default, privileged host mounts, and default `noserverino` guidance only in comments. Test signal is Helm lint/render/install across value combinations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/Chart.yaml

Purpose: declares the first v0.1.0 SMB CSI Helm chart. It uses chart API v1, appVersion `v0.1.0`, description, name, and matching chart version.

State is immutable release metadata for historical installs. Dependencies are the v0.1.0 templates and package index. Risks include old `v`-prefixed chart version semantics and compatibility with modern Helm/Kubernetes clusters. Test signal is historical chart packaging/install behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the early SMB `CSIDriver` object for chart v0.1.0. It uses `storage.k8s.io/v1beta1` and hard-codes name `smb.csi.k8s.io`.

Important behavior is minimal: declare the CSIDriver and driver name without later fields such as attachRequired, podInfoOnMount, or lifecycle modes. State is a cluster-scoped beta API object. Dependencies are Kubernetes versions that still serve v1beta1 CSIDriver. Risks include incompatibility with modern clusters where v1beta1 is removed and lack of explicit inline/persistent lifecycle signaling. Test signal is Helm install on older clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the original Windows SMB node DaemonSet for chart v0.1.0 when Windows is enabled. It predates HostProcess support and relies on Windows containers plus CSI Proxy named pipes.

Important behavior: deploys liveness probe, node-driver-registrar, and SMB plugin with hard-coded driver name/socket paths under `C:\var\lib\kubelet`, health port 39613, and v1beta1 CSI Proxy pipe mounts. Image tags come from the compact v0.1.0 values file.

State is Windows DaemonSet pods, kubelet plugin host paths, and named pipe mounts. Dependencies include early sidecar versions, CSI Proxy beta pipes, and Kubernetes Windows CSI support. Risks include removed beta APIs/pipes, no configurable kubelet path, hard-coded ports, and no HostProcess mode. Test signal is historical Windows node registration/mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the original Linux SMB node DaemonSet for chart v0.1.0. It deploys node liveness probe, node-driver-registrar, and SMB plugin on Linux nodes.

Important behavior: it hard-codes DaemonSet name `csi-smb-node`, namespace, labels, health port 39613, plugin socket under `/csi/csi.sock`, registration path under `/var/lib/kubelet/plugins/smb.csi.k8s.io/csi.sock`, and privileged SMB container with kubelet hostPath mount propagation.

State is Linux node plugin pods and kubelet hostPath directories. Dependencies include early sidecar images from `mcr.microsoft.com`, privileged mount propagation, and v0.1.0 image. Risks include limited configurability, old sidecar flags such as `--connection-timeout`, and no resource/security hardening. Test signal is node registration and mount success on old clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/values.yaml

Purpose: contains the minimal defaults for the first SMB CSI chart. It sets the SMB image repository/tag, liveness probe image/tag, node-driver-registrar image/tag, and booleans for Linux and Windows enablement.

State is declarative chart input. Dependencies are legacy Microsoft image registries and sidecar versions `v1.1.0` and `v1.2.0`. Risks include no controller/provisioner values in this release, no resource settings, old image locations, and Windows/Linux defaults that may not match modern clusters. Test signal is historical Helm render/install.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/Chart.yaml

Purpose: declares the v0.2.0 SMB CSI Helm chart release metadata. It uses API v1, appVersion `v0.2.0`, description, chart name, and matching version.

State is historical Helm metadata. Dependencies are v0.2.0 templates, including the newly added controller deployment and RBAC. Risks are legacy `v`-prefixed version handling and compatibility with modern Helm/Kubernetes. Test signal is chart package/index validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: introduces the controller Deployment for dynamic provisioning in chart v0.2.0. It runs external provisioner, liveness probe, and SMB controller sharing a CSI socket.

Important behavior: hard-coded deployment name `csi-smb-controller`, Linux node selection, controller service account, provisioner sidecar from values, liveness health port 29632, and privileged SMB container with endpoint and driver name. State is controller pods and socket `emptyDir`. Dependencies include v1.4.0 provisioner and RBAC template. Risks include older liveness flags, no resizer sidecar, fixed ports, and limited scheduling/resource configuration. Test signal is dynamic provisioning on v0.2.0 installs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the SMB CSIDriver object for chart v0.2.0. Like v0.1.0, it uses `storage.k8s.io/v1beta1` and hard-codes `smb.csi.k8s.io`.

State is the beta CSIDriver object. Dependencies are Kubernetes clusters that still support v1beta1 CSIDriver. Risks include modern API removal and missing explicit lifecycle mode fields. Test signal is successful Helm install and driver discovery on older clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.2.0 Windows node DaemonSet. It remains the non-HostProcess, CSI Proxy pipe based deployment.

Important behavior: liveness probe, node-driver-registrar, and SMB plugin use hard-coded kubelet paths and driver name, health port 39613, and Windows node selector. State includes host paths and CSI Proxy pipe mounts. Dependencies are old sidecar images and CSI Proxy beta interfaces. Risks include hard-coded paths, old flags, no configurable resources, and dependency on removed beta pipe names. Test signal is Windows node plugin registration and mounts in v0.2.0 environments.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.2.0 Linux node DaemonSet, still close to v0.1.0 but coexisting with the new controller chart resources.

Important behavior: liveness probe health port 39613, registrar socket registration, privileged SMB plugin, Linux node selector, kubelet hostPath and plugin directories. State is node plugin pods and host mount state. Dependencies include legacy sidecar images and privileged mount propagation. Risks include fixed labels/ports, older liveness flag names, no resource settings, and no feature toggles. Test signal is Linux node registration and static/dynamic mount use.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: provides the initial controller ServiceAccount, ClusterRole, and ClusterRoleBinding for the SMB external provisioner in chart v0.2.0.

Important permissions include PV create/patch/delete, PVC get/list/watch/update, StorageClass get/list/watch, events create/update/patch, and secret get. State is cluster-scoped RBAC plus namespace service account. Dependencies are provisioner sidecar requirements and fixed names such as `smb-external-provisioner-role`. Risks include broad cluster scope, fixed name collisions, no resizer permissions, and secret read exposure. Test signal is whether dynamic provisioning succeeds without RBAC denial.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/values.yaml

Purpose: expands v0.1.0 values with controller and provisioner configuration. It defines SMB, csi-provisioner, liveness probe, and registrar images; service account names; and Linux/Windows enablement.

State is declarative chart input. Dependencies are Microsoft-hosted image repositories and sidecar versions. Risks include old image registries, limited scheduling/resource customization, and no resizer or feature toggles. Test signal is Helm render and v0.2.0 provisioning behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/Chart.yaml

Purpose: declares chart metadata for SMB CSI v0.3.0. It keeps API v1, appVersion `v0.3.0`, chart name, description, and version.

State is historical release metadata. Dependencies are v0.3.0 templates, which mainly adjust health ports from v0.2.0. Risks are the same legacy version/API compatibility issues as earlier v0.x charts. Test signal is Helm packaging and historical install success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.3.0 controller Deployment for dynamic SMB provisioning. It is structurally similar to v0.2.0 but uses the later controller health port 29642.

Important behavior: external provisioner, liveness probe, and privileged SMB controller share `/csi/csi.sock`; sidecars and service accounts come from values; Linux node scheduling is fixed. State is controller pod and socket volume. Dependencies are csi-provisioner v1.4.0, livenessprobe v1.1.0, and RBAC. Risks include no resizer, old sidecar flags, fixed names/ports, and no scheduling/resource knobs beyond values booleans. Test signal is provisioning success in v0.3.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.3.0 beta CSIDriver for SMB. It remains `storage.k8s.io/v1beta1` with hard-coded name `smb.csi.k8s.io`.

State is a cluster-scoped beta object. Dependencies are older Kubernetes versions and Helm install ordering. Risks include API removal in newer clusters and lack of explicit attach/lifecycle settings. Test signal is successful chart install and driver discovery.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.3.0 Windows node DaemonSet. Compared with earlier charts, the health port aligns to 29643, but deployment remains CSI Proxy pipe based.

Important behavior: Windows liveness probe, registrar, and SMB plugin use hard-coded paths and driver name; SMB plugin receives endpoint and node id. State includes Windows hostPath/plugin directories and CSI Proxy pipe mounts. Dependencies are old sidecars and Windows CSI proxy. Risks include old beta API/pipes, no HostProcess mode, fixed paths, and sparse configuration. Test signal is Windows node registration and mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.3.0 Linux node DaemonSet. It uses health port 29643 and otherwise follows the early node deployment pattern.

Important behavior: liveness probe, registrar, and privileged SMB plugin share the kubelet plugin socket and mount host kubelet directories with bidirectional propagation. State is node plugin pods and hostPath directories. Dependencies are sidecar images from values and privileged Linux node access. Risks include fixed names/ports, old flags, no resource defaults, and no optional Kerberos or stats features. Test signal is Linux node plugin readiness and mount success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders the v0.3.0 provisioner ServiceAccount and RBAC. It remains focused on the external provisioner and does not include later resizer or node-secret roles.

Important state is cluster-scoped provisioner ClusterRole/Binding and namespace ServiceAccount. Dependencies are fixed names and provisioner permissions. Risks include name collisions, broad secret get, and missing permissions for newer sidecars/features. Test signal is provisioning API access in v0.3.0 deployments.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/values.yaml

Purpose: supplies v0.3.0 chart defaults: SMB image `v0.3.0`, csi-provisioner v1.4.0, livenessprobe v1.1.0, node-driver-registrar v1.2.0, service account names, and Linux/Windows enablement.

State is declarative input. Dependencies are legacy Microsoft image locations and early sidecar CLIs. Risks include minimal configurability, no resource requests/limits, no resizer, and old registry dependencies. Test signal is Helm render/install and basic provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/Chart.yaml

Purpose: declares SMB CSI chart v0.4.0 metadata. It maintains API v1, appVersion `v0.4.0`, description, name, and version.

State is historical Helm metadata. Dependencies are v0.4.0 chart templates, which begin adding a shared `node` values group. Risks include legacy Kubernetes API use and old chart version prefixing. Test signal is chart package/install behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.4.0 controller Deployment. It is close to v0.3.0, retaining provisioner, liveness probe, and SMB controller containers.

Important behavior: controller health port remains 29642, Linux scheduling remains fixed, and the chart gains small value-structure changes around node settings elsewhere. State is the Deployment and shared socket. Dependencies are old csi-provisioner/liveness sidecars and provisioner RBAC. Risks include no resizer, fixed deployment names, old sidecar flags, and privileged controller. Test signal is dynamic provisioning in v0.4.0 installs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.4.0 SMB CSIDriver object with `storage.k8s.io/v1beta1` and fixed name.

State is beta cluster-scoped driver metadata. Dependencies are clusters still serving the beta API. Risks include API removal on modern Kubernetes and no attach/lifecycle flags. Test signal is install success and driver discovery.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.4.0 Windows node DaemonSet. It keeps the non-HostProcess architecture and adds minor value-driven node update controls.

Important behavior: liveness probe and registrar use health port 29643, SMB plugin runs with endpoint/nodeid, and hostPath/named pipe mounts integrate with CSI Proxy. State is Windows DaemonSet and host plugin directories. Dependencies include old Windows sidecars, beta CSI Proxy pipe paths, and Kubernetes Windows support. Risks include fixed kubelet path, old pipe names, no HostProcess option, and low configurability. Test signal is Windows node plugin readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.4.0 Linux node DaemonSet. It includes early support for chart-level node settings such as rolling update maxUnavailable.

Important behavior: deploys liveness probe, registrar, and privileged SMB plugin, with health port 29643 and kubelet hostPath mount propagation. State is node pods and host plugin/registration directories. Dependencies are sidecar values and privileged Linux mounts. Risks include old liveness flag syntax, hard-coded driver/path details, no resource controls, and old image registry defaults. Test signal is node registration and mount operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders v0.4.0 provisioner RBAC. It creates the controller service account, external provisioner role, and binding.

State is cluster RBAC and namespace service account. Dependencies are fixed resource names and provisioner sidecar needs. Risks include broad secret get, cluster-wide permissions, no resizer permissions, and collisions with other installations. Test signal is absence of RBAC denial during dynamic provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/values.yaml

Purpose: supplies v0.4.0 chart values, adding a `node` section on top of image, serviceAccount, controller, linux, and windows settings.

Important defaults include SMB image v0.4.0, csi-provisioner v1.4.0, livenessprobe v1.1.0, node-driver-registrar v1.2.0, controller replicas, node maxUnavailable, and Linux/Windows enabled flags. State is declarative Helm input. Risks include old sidecars, no resource/security settings, no resizer, and legacy registry locations. Test signal is Helm render/install.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/Chart.yaml

Purpose: declares SMB CSI chart v0.5.0 metadata. It uses API v1 and matching appVersion/version `v0.5.0`.

State is historical chart release metadata. Dependencies are v0.5.0 templates and package index. Risks include v-prefixed chart version compatibility and legacy CSIDriver API use in templates. Test signal is Helm package/install behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.5.0 SMB controller Deployment. The main chart evolution is sidecar image migration to registry.k8s.io-era versions and liveness flag change from connection-timeout to probe-timeout.

Important behavior: provisioner, liveness probe, and SMB controller share `/csi/csi.sock`, use controller service account, and run on Linux. State is controller Deployment and socket volume. Dependencies include csi-provisioner v2.0.4 and livenessprobe v2.1.0. Risks include no resizer, fixed names/ports, privileged SMB container, and compatibility with provisioner v2 flags. Test signal is dynamic provisioning and liveness health.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.5.0 SMB CSIDriver object. It still uses `storage.k8s.io/v1beta1` with fixed name `smb.csi.k8s.io`.

State is beta cluster metadata. Dependencies are Kubernetes versions supporting the beta API. Risks include incompatibility with newer Kubernetes and lack of attach/lifecycle declarations. Test signal is chart install and CSI driver discovery.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.5.0 Windows node DaemonSet using non-HostProcess containers and CSI Proxy named pipes.

Important behavior: liveness probe now uses sidecar v2 style `--probe-timeout`, registrar v2.0.1 registers the driver, and SMB plugin mounts kubelet paths plus CSI Proxy pipes. State includes Windows host paths and DaemonSet pods. Dependencies are registry.k8s.io sidecars, Microsoft SMB image, and CSI Proxy. Risks include beta CSIDriver, fixed kubelet path, no HostProcess support, and pipe compatibility. Test signal is Windows node registration and mount health.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.5.0 Linux node DaemonSet. It updates sidecar image versions and liveness probe flags while retaining the early chart structure.

Important behavior: liveness probe, node-driver-registrar, and privileged SMB plugin run on Linux, with kubelet/plugin hostPath mounts and health port 29643. State is node pod and kubelet mount state. Dependencies include livenessprobe v2.1.0, registrar v2.0.1, and privileged host access. Risks include no resource controls, no stats/Kerberos feature flags, and fixed paths/names. Test signal is node registration and mount success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders the v0.5.0 external provisioner RBAC. It remains a provisioner-only role/binding plus service account.

State is cluster-level RBAC. Dependencies are csi-provisioner v2.0.4 permissions and fixed names. Risks include no resizer RBAC, broad secret get, and cluster role collisions. Test signal is dynamic provisioning API access.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/values.yaml

Purpose: provides v0.5.0 values with updated sidecar repositories and versions. It sets SMB image v0.5.0, csi-provisioner v2.0.4, livenessprobe v2.1.0, node-driver-registrar v2.0.1, service accounts, controller replicas, node maxUnavailable, and Linux/Windows flags.

State is declarative chart configuration. Dependencies include registry.k8s.io sidecar availability and legacy SMB image repo. Risks include limited scheduling/resource customization, no resizer, old CSIDriver API in templates, and Windows defaults requiring CSI Proxy. Test signal is Helm render/install and provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/Chart.yaml

Purpose: declares SMB CSI chart v0.6.0 metadata. It uses chart API v1 with appVersion and version `v0.6.0`.

State is historical Helm metadata referenced by the chart index and packaged archive. Dependencies are v0.6.0 templates, especially the adjusted Windows kubelet path value. Risks include legacy CSIDriver API and v-prefixed chart version handling. Test signal is Helm package/install success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.6.0 controller Deployment for SMB dynamic provisioning. It is largely the same as v0.5.0, using provisioner v2.0.4, livenessprobe v2.1.0, and SMB controller image v0.6.0.

Important behavior: controller pods run on Linux, use the controller service account, share a CSI socket, and expose liveness on port 29642. State is Deployment pods and socket volume. Dependencies include provisioner RBAC and sidecar flag compatibility. Risks include no resizer, fixed names/ports, privileged SMB container, and old chart API choices. Test signal is v0.6.0 provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.6.0 SMB CSIDriver object. It remains on `storage.k8s.io/v1beta1` and fixed driver name `smb.csi.k8s.io`.

State is beta cluster-scoped driver metadata. Dependencies are Kubernetes versions still serving v1beta1. Risks include install failure on newer clusters and missing explicit attach/lifecycle fields. Test signal is driver discovery after Helm install.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.6.0 Windows node DaemonSet. It is the non-HostProcess CSI Proxy based mode, with a notable change toward configurable Windows kubelet path via `.Values.kubelet.windowsPath` in the registrar path.

Important behavior: liveness probe and registrar run sidecar v2 images, SMB plugin receives endpoint and node id, and hostPath/named pipe mounts connect to kubelet and CSI Proxy. State is Windows node pods, plugin registration paths, and pipe mounts. Dependencies are Windows kubelet path values, CSI Proxy, and v0.6.0 SMB image. Risks include path value mismatch, no HostProcess support, beta CSIDriver, and old pipe compatibility. Test signal is Windows e2e/node readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
