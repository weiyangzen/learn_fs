# subset-b-000339 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/cephfs.go -->
# sources/control-plane/ceph-csi/e2e/cephfs.go

Purpose: defines the ordered CephFS CSI end-to-end suite and the CephFS deployment helpers used by it. The file covers installing/removing CephFS CSI YAML resources, creating per-suite config, secrets, Vault, Ceph users, subvolume groups, and then exercising Kubernetes storage behavior against real CephFS backend state.

Important APIs/types/functions: `CephFSDeployment` embeds `DriverInfo`; `deployCephfsPlugin()`, `deleteCephfsPlugin()`, and `createORDeleteCephfsResources()` apply CSI driver, RBAC, provisioner, nodeplugin, config, and fencing-enabled YAML. `validateSubvolumeCount()`, `validateCephFSSnapshotCount()`, and `validateSubvolumePath()` bridge Kubernetes PVC/PV state to CephFS subvolume state. `NewCephFSDeployment()` selects the default driver metadata, while the Ginkgo `Describe(cephfsType)` owns setup, teardown, and all specs.

Control flow: `BeforeEach(..., OncePerOrdered)` gates on flags, optionally creates the Ceph-CSI namespace, deploys the plugin, writes `config.json`, creates provisioner/node Ceph users and Secrets, deploys Vault, enables cluster name and fencing in the deployment, creates the `e2e` subvolume group, and discovers the metadata pool. `AfterEach(..., OncePerOrdered)` gathers CSI/debug logs on failure, deletes config/Secrets/storageclasses/Vault/subvolume group/plugin resources, and removes the namespace when it created it. The ordered context then performs readiness, helm binding, user-id/client-address metadata, WaitForFirstConsumer, mount options, generic ephemeral volumes, RWOP, static PVs, fscrypt KMS variants, PVC/PV metadata, custom volume prefixes, fuse recovery, normal-user access, multi-PVC lifecycle, data persistence, manual unmount deletion, missing-backend cleanup, multiple cluster/subvolume-group config, resize, read-only mounts, snapshot metadata/restore/retention, concurrent snapshot clones, service-account restrictions, encrypted snapshot-backed volumes, snapshot-backed and non-backingSnapshot restores, ROX/RWX clone flows, PVC-to-PVC clones, 500M PVC creation, volume group snapshots, rados namespace isolation, and destructive pool/user cleanup.

State and persistence: the suite creates durable Kubernetes objects and Ceph backend objects: StorageClasses, PVCs, PVs, Pods/Deployments, VolumeSnapshots, VolumeSnapshotContents, Secrets, ConfigMaps, Ceph users, subvolumes, subvolume snapshots, omap entries, and Vault passphrases. Many tests assert cleanup by checking subvolume, snapshot, RBD/omap counts return to zero. Global `subvolumegroup`, `fileSystemName`, `metadataPool`, `radosNamespace`, and `cephCSINamespace` shape backend operations, with deferred restoration in the rados namespace test.

Dependencies and integration points: uses Ginkgo/Gomega, Kubernetes e2e framework/client-go, external-snapshotter APIs, pod-security admission, Ceph toolbox helpers, Vault helpers, configmap/namespace/deployment utilities, PVC/snapshot/resize/static PV helpers, Ceph user helpers, and operator/helm deployment variants. It integrates CSI YAML under `../deploy/cephfs/kubernetes/` and examples under `../examples/cephfs/`.

Risks: the suite mutates shared globals and backend Ceph resources, so ordered execution and cleanup correctness are critical. Several tests are destructive or concurrent; failures can leave Ceph users, subvolumes, snapshots, omap keys, Vault keys, or custom configmaps behind. The destructive pool/user cleanup is intentionally skipped when NFS tests also need CephFS. Backend command parsing depends on PV CSI attributes and Ceph CLI output. The fscrypt/Vault and fuse recovery tests are sensitive to container names, pod placement, and exact kernel/user-space error strings.

Test signals: this file is itself the main CephFS signal. Useful pass criteria are CSI deployment readiness, successful PVC/app binding, matching CephFS subvolume and omap counts after create/delete, metadata keys matching PVC/PV/snapshot objects, Vault passphrase creation and destruction, read-only/RWOP enforcement, clone/snapshot checksum behavior, service-account PermissionDenied paths, volume group snapshot success, and cleanup checks that all backend counts return to zero.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/cephfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/cephfs_helper.go -->
# sources/control-plane/ceph-csi/e2e/cephfs_helper.go

Purpose: provides CephFS-specific helper functions used by CephFS and NFS e2e suites to create StorageClasses/Secrets, inspect CephFS backend objects, validate fscrypt and KMS behavior, delete backing resources, and enforce service-account based volume access restrictions.

Important APIs/types/functions: `createCephfsStorageClass()`, `createCephfsStorageClassWaitForFirstConsumer()`, `updateStorageClassParameters()`, `createStorageClass()`, and `createCephfsSecret()` prepare Kubernetes storage primitives. Backend inspection types include `cephfsSubVolume`, `cephfsSubvolumeMetadata`, `cephfsSnapshotMetadata`, and `cephfsSnapshot`. Listing/getter helpers cover subvolumes, subvolume metadata, snapshots, snapshot metadata, and subvolume paths. `deleteBackingCephFSVolume()` and `deleteBackingCephFSSubvolumeSnapshot()` intentionally remove backend resources. `validateEncryptedCephfs()`, `validateFscryptAndAppBinding()`, and `validateFscryptClone()` validate fscrypt xattrs and KMS passphrase lifecycle. `validateCephFSServiceAccountVolumeRestriction()` validates metadata-driven service-account authorization. `verifyClientAddressMetadataSnapshotBacked()` and `verifyUserIdMappingMetadataSnapshotBacked()` check snapshot-backed mount metadata.

Control flow: StorageClass creation loads example YAML, injects fsName, secret references, optional pool, caller parameters, and clusterID before polling Kubernetes create. CephFS backend helpers execute `ceph fs subvolume ...` commands in the toolbox pod and parse JSON or trimmed stdout. Snapshot-name resolution follows VolumeSnapshot to VolumeSnapshotContent and extracts the CSI snapshot UUID from `SnapshotHandle`. Fscrypt validation creates PVC/app pairs, locates the PV volume handle, checks `ceph.fscrypt.auth` on the mounted path from the nodeplugin container, probes KMS passphrases while mounted, deletes resources, and verifies key deletion/destruction. Service-account restriction creates three SAs, sets CephFS metadata on the subvolume, verifies allowed mount, verifies denied mount failure, waits for attachment cleanup, updates metadata to a comma-separated allow list, and retests.

State and persistence: helpers create StorageClasses and Secrets in Kubernetes and mutate CephFS subvolume metadata. Some functions deliberately delete backend subvolumes/snapshots to test CSI cleanup behavior. KMS validation expects Vault or metadata secrets to persist during the volume lifetime and disappear or be destroyed after deletion. Service-account tests use defers to remove SAs, PVCs, and metadata.

Dependencies and integration points: uses Kubernetes client-go, storage APIs, external-snapshotter APIs, Ceph toolbox command execution, global suite variables (`fileSystemName`, `subvolumegroup`, `cephCSINamespace`, `radosNamespace`, secret names), and shared PVC/app/snapshot helper functions. It is reused by CephFS tests and some NFS tests because NFS volumes are backed by CephFS subvolumes.

Risks: many helpers build shell commands with test-derived names and parse stdout/stderr, so quoting and unusual names matter. Metadata keys are hard-coded CSI contracts; driver changes can break tests. Snapshot-name regex assumes the handle suffix format. Service-account restriction requires detachment before metadata updates to trigger a fresh publish path. Helper functions mix returned errors and `logAndFail`, making some paths hard to compose in unit tests.

Test signals: successful helper behavior is visible through Kubernetes object creation, Ceph CLI JSON parsing, exact metadata values, fscrypt xattr presence, Vault passphrase read/delete/destroy checks, denied pod errors containing `PermissionDenied` and restriction text, and cleanup of subvolumes/metadata after tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/cephfs_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/clone.go -->
# sources/control-plane/ceph-csi/e2e/clone.go

Purpose: contains a shared clone-size validation helper for e2e tests that need to verify cloning a PVC into a larger PVC and then mounting the clone in an application.

Important APIs/types/functions: `validateBiggerCloneFromPVC(f, pvcPath, appPath, pvcClonePath, appClonePath)` loads source PVC/app YAML, forces the source PVC to `1Gi`, creates the source PVC and app, loads the clone PVC/app YAML, points the clone `DataSource.Name` at the source PVC, forces the clone request to `2Gi`, creates the clone and app, deletes the source pair, and validates the clone size.

Control flow: the helper creates the source workload with a stable app label used for later pod selection, then creates the clone workload with the same label. After deleting the parent PVC/app, it branches on `VolumeMode`: filesystem clones are checked through `checkDirSize()`, while block-mode clones are checked through `checkDeviceSize()`. It then deletes the clone workload.

State and persistence: creates two PVC/app pairs in the framework namespace and relies on CSI clone provisioning to create backend state. It expects deleting the parent after clone creation not to invalidate the clone. No durable state should remain after `deletePVCAndApp()` calls complete.

Dependencies and integration points: uses `loadPVC()`, `loadApp()`, `createPVCAndApp()`, `deletePVCAndApp()`, `checkDirSize()`, and `checkDeviceSize()` from the e2e helper set, Kubernetes core resource quantity parsing, and framework namespace state. CephFS invokes this for larger PVC-to-PVC clone coverage.

Risks: clone and app use the same label selector, so concurrent same-namespace callers could select unexpected pods. The function calls `logAndFail()` on clone load failures instead of returning errors consistently. It assumes the clone template has a non-nil data source and that the clone can be larger than the parent.

Test signals: passing signals are successful clone provisioning, successful source deletion after clone creation, observed `2Gi` filesystem directory or block device size in the clone app, and final cleanup without leftover PVC/PV/app resources.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/clone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/configmap.go -->
# sources/control-plane/ceph-csi/e2e/configmap.go

Purpose: creates, updates, and deletes the Ceph-CSI cluster configuration ConfigMap used by e2e-deployed drivers. It converts live Ceph monitor and cluster metadata into the `config.json` payload consumed by Ceph-CSI.

Important APIs/types/functions: `deleteConfigMap(pluginPath)` deletes the YAML-defined ConfigMap. `createConfigMap(pluginPath, c, f)` loads the template, discovers cluster ID and monitors, builds a `[]cephcsi.ClusterInfo`, fills RBD/CephFS/read-affinity fields, and creates or updates the ConfigMap. `createCustomConfigMap(c, pluginPath, clusterInfo)` writes multiple cluster entries with caller-specified `subvolumeGroup` and `radosNamespace`.

Control flow: default creation unmarshals `<pluginPath>/<configMap>`, calls `getClusterID()` and `getMons()`, marshals cluster info into `Data["config.json"]`, sets the target namespace, then updates an existing ConfigMap or creates one if not found. Upgrade testing forces the CephFS subvolume group to `csi` before writing the config. Custom creation builds one cluster info entry per map key, fills monitor lists, applies supported per-cluster options, marshals JSON, and updates the existing ConfigMap.

State and persistence: persists `config.json` in the `cephCSINamespace` ConfigMap. It embeds global `radosNamespace`, `subvolumegroup`, secret names, read-affinity labels, and current monitor endpoints. Tests often restart CSI pods after changing it so drivers reload state.

Dependencies and integration points: uses Kubernetes ConfigMap API, Ceph-CSI deploy API structs, `unmarshal()`, `getClusterID()`, `getMons()`, `retryKubectlFile()`, and global deployment constants. It is used by CephFS, NFS, RBD migration, and NVMe-oF deployment helpers.

Risks: Go map iteration in `createCustomConfigMap()` makes cluster order nondeterministic, which is usually fine but can complicate diffs. Unsupported keys in `clusterInfo` are silently ignored. Updating config without pod restart may not affect running CSI components. Upgrade-test mutation of global `subvolumegroup` can influence later tests if not reset.

Test signals: valid ConfigMap creation/update, JSON parsable by Ceph-CSI, monitor and cluster ID accuracy, expected subvolume group/rados namespace routing, and successful CSI pod operation after config changes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/configmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/deploy-vault.go -->
# sources/control-plane/ceph-csi/e2e/deploy-vault.go

Purpose: deploys the HashiCorp Vault example stack and tenant service-account setup used by encryption/KMS e2e tests.

Important APIs/types/functions: path globals identify Vault example YAMLs. `deployVault(c, deployTimeout)` clears any helm-created KMS ConfigMap, applies Vault resources, and waits for the Vault pod. `deleteVault()` removes those resources. `createORDeleteVault(action)` applies service/statefulset, RBAC, and KMS config templates with namespace replacements. `createTenantServiceAccount(c, ns)`, `deleteTenantServiceAccount(ns)`, and `createORDeleteTenantServiceAccount(action, ns)` create/delete tenant service account resources and the admin Job that configures Vault policy.

Control flow: Vault deployment deletes `ceph-csi-encryption-kms-config` if present, applies templated YAML through kubectl input, lists pods with `app=vault`, asserts exactly one pod, and waits for it to run. Template processing replaces default namespace references and Vault service DNS with `cephCSINamespace`. Tenant setup creates the tenant SA in the tenant namespace, applies an admin job in the Ceph-CSI namespace with `TENANT_NAMESPACE` and Vault URL rewritten, then waits for the job to complete.

State and persistence: creates Vault workload/RBAC/ConfigMap objects in `cephCSINamespace`, tenant SAs in test namespaces, and Vault-side policy/kv setup through the admin job. Cleanup is kubectl-driven and assumes example labels/names remain stable.

Dependencies and integration points: uses `replaceNamespaceInTemplate()`, `retryKubectlArgs()`, `retryKubectlInput()`, `retryKubectlFile()`, pod wait/job wait helpers, Kubernetes client-go, and Gomega expectations. CephFS fscrypt tests and KMS helpers use the resulting Vault service and token/tenant configurations.

Risks: string replacement is broad (`default`, `vault.default`, `value: default`) and can mis-edit templates if content changes. The helper assumes one Vault pod and a fixed root token. Failure cleanup is limited when `logAndFail()` aborts. Tenant deletion expects both tenant and admin resources to still exist.

Test signals: Vault pod reaches Running, tenant admin job completes, KMS config exists in the CSI namespace, encrypted volume tests can read passphrases from Vault, and deletion removes the Vault resources without blocking subsequent tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/deploy-vault.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/deployment.go -->
# sources/control-plane/ceph-csi/e2e/deployment.go

Purpose: supplies generic deployment and YAML-resource helpers for the e2e suites, including pod command execution, Deployment lifecycle waits, CSI deployment readiness waits, generic resource deployers, and rollout-safe container argument updates.

Important APIs/types/functions: `execCommandInPodWithName()` wraps Kubernetes e2e pod exec. `loadAppDeployment()`, `createDeploymentApp()`, `deleteDeploymentApp()`, `waitForDeploymentInAvailableState()`, and `waitForDeploymentComplete()` manage app Deployments. `waitForCSI()` waits for a provisioner Deployment and nodeplugin DaemonSet concurrently. `ResourceDeployer`, `yamlResource`, and `yamlResourceNamespaced` abstract kubectl create/delete over raw or templated YAML. `waitForDeploymentUpdateScale()`, `waitForDeploymentUpdate()`, and `waitForContainersArgsUpdate()` update Deployment scale/spec/arguments with polling.

Control flow: Deployment creation goes through client-go create then availability polling. Deletion polls until the Deployment is not found. Completion polling checks ready replica count against desired replica count. `waitForCSI()` uses `errgroup` to wait for controller and node sides together. `yamlResource.Do()` reads a file, optionally applies replacement strings and custom namespace, then sends it to kubectl. `yamlResourceNamespaced.Do()` first performs namespace replacement, log-level replacement, temporary VGS alpha disabling, optional one-replica conversion, topology/read-affinity/fencing/crush-label injection, then applies via kubectl. Argument update scales a Deployment down, edits selected container args, clears server-managed metadata, updates the Deployment, scales back, and waits for restored replica count.

State and persistence: mutates Kubernetes Deployments and arbitrary YAML resources, including CSI control-plane/nodeplugin objects. The argument updater preserves the original replica count and rewrites persisted Deployment specs.

Dependencies and integration points: uses client-go Apps/Core APIs, Kubernetes deployment util, e2e pod framework, wait polling, shared kubectl helpers, YAML text transformation helpers, and `isRetryableAPIError()`. It underpins CephFS, NFS, NVMe-oF, Vault, and gateway deployment paths.

Risks: YAML transformation is text-based and depends on template structure. `waitForDeploymentInAvailableState()` only checks that an Available condition exists, not its status. `waitForDeploymentComplete()` compares status replicas and ready replicas, which may be zero during scale-down. Argument matching compares args exactly to `key` but writes `--key=value`, so existing args must follow expected form. Resetting `ResourceVersion` to `"0"` is unusual and can conflict with API expectations.

Test signals: deployment helpers are validated indirectly by CSI readiness, app availability, successful kubectl resource application, scale/update convergence, and failure logs showing namespace resource state when readiness does not converge.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/deployment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/e2e_test.go -->
# sources/control-plane/ceph-csi/e2e/e2e_test.go

Purpose: is the e2e suite entry point. It registers command-line flags, initializes Kubernetes e2e framework configuration, detects OpenShift, and starts the Ginkgo suite.

Important APIs/types/functions: `init()` registers flags controlling deploy/test enablement for CephFS, RBD, NFS, NVMe-oF, fscrypt, NBD, helm/operator/upgrade modes, namespaces, filesystem, cluster ID, NFS driver name, and timeouts. `setDefaultKubeconfig()` defaults `KUBECONFIG` to `$HOME/.kube/config`. `TestE2E(t)` registers Gomega failure handling, detects OpenShift, sets fail-fast Ginkgo config, and runs specs. `handleFlags()` wires Kubernetes framework flags, parses flags, and derives dependent feature toggles.

Control flow: package initialization redirects log output to `GinkgoWriter`, registers local and framework flags, sets kubeconfig, parses flags, applies derived behavior (`testCephFS` enables NFS testing/deploy, `testNVMeoF` enables NVMe-oF deployment, operator mode rewrites `cephCSINamespace`), and logs deployment timeout. The test function runs in parallel at the Go test level but Ginkgo ordered contexts control suite internals.

State and persistence: mutates global flags and suite globals such as `deployCephFS`, `deployNFS`, `deployNVMeoF`, `testNFS`, `cephCSINamespace`, `rookNamespace`, `fileSystemName`, `clusterID`, and `isOpenShift`. It sets the process environment variable `KUBECONFIG` if absent.

Dependencies and integration points: uses Go `testing`, Ginkgo/Gomega, Kubernetes e2e `framework` and `config`, and local `detectOpenShift()`. Every e2e file depends on the globals initialized here.

Risks: `testCephFS` implicitly enables NFS tests and NFS deployment, which may surprise callers expecting only CephFS. `testing.Init()` and `flag.Parse()` in `init()` can make package composition brittle. `t.Parallel()` allows this suite to overlap with other Go tests if invoked together. Operator mode hard-codes the operator namespace.

Test signals: successful flag parsing, OpenShift detection, suite start, and correct skip/deploy behavior across flag combinations are the main signals. Fail-fast means the first failing spec aborts later coverage in a run.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/e2e_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/errors.go -->
# sources/control-plane/ceph-csi/e2e/errors.go

Purpose: centralizes retryability and kubectl stderr parsing helpers used by the e2e suite to distinguish transient API errors from terminal failures and to recognize idempotent CLI errors.

Important APIs/types/functions: `isRetryableAPIError(err)` recognizes Kubernetes internal/timeout/server-timeout/too-many-requests errors, EOF/reset/refused network errors, suggested client delays, and known transient strings. `getStdErr(errString)` extracts the `stderr:` section from the formatted kubectl error wrapper. `isAlreadyExistsCLIError(err)`, `isNotFoundCLIError(err)`, and `isNoSuchResourceCLIError(err)` classify kubectl stderr lines while ignoring blanks and warnings.

Control flow: API retryability first checks structured Kubernetes and network predicates, then falls back to string matches such as `etcdserver: request timed out`, `unable to upgrade connection`, `transport is closing`, missing content type, and pod host assignment. CLI helpers require a non-empty extracted stderr region and then scan each line, accepting only the expected error type aside from blank/warning lines.

State and persistence: no persistent state; helpers are pure string/error classifiers.

Dependencies and integration points: uses `k8s.io/apimachinery/pkg/api/errors`, `k8s.io/apimachinery/pkg/util/net`, and `strings`. Deployment, namespace, storage, and kubectl retry helpers consume these predicates to decide whether to poll again, ignore idempotent errors, or fail.

Risks: `getStdErr()` depends on exact formatting from Kubernetes e2e kubectl utilities. CLI classification is all-or-nothing across multi-resource stderr, so mixed NotFound/AlreadyExists output is rejected. Warning filtering is substring-based and could ignore meaningful lines containing `Warning`. String retryability can hide real persistent infrastructure problems until timeout.

Test signals: unit tests cover stderr extraction and AlreadyExists detection for representative kubectl output. Broader signals are reduced flakes in e2e polling loops and correct handling of idempotent create/delete operations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/errors_test.go -->
# sources/control-plane/ceph-csi/e2e/errors_test.go

Purpose: unit-tests the kubectl stderr extraction and AlreadyExists classification helpers from `errors.go`.

Important APIs/types/functions: `TestGetStdErr(t)` defines table-driven cases with formatted kubectl output and checks both `getStdErr()` and `isAlreadyExistsCLIError()`.

Control flow: the test runs in parallel and each subtest also runs in parallel. Cases cover normal output containing `stderr:` and `error:` delimiters with two AlreadyExists server errors, output missing `stderr:`, and output missing the trailing `error:` delimiter. For each case it compares the extracted stderr string and the AlreadyExists boolean.

State and persistence: no external state; all data is inline sample text.

Dependencies and integration points: uses Go `testing` and `fmt.Errorf()` to wrap sample strings into errors. It directly exercises the helper contract used by kubectl retry logic elsewhere in the e2e package.

Risks: coverage is narrow: NotFound, no-such-resource, warnings, blank-line-only stderr, mixed errors, and retryable API predicates are not unit-tested here. Parallel subtests are safe because helpers are pure.

Test signals: passing tests confirm the current kubectl wrapper format is parsed as expected and that missing delimiters produce empty stderr plus false classification.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/kms.go -->
# sources/control-plane/ceph-csi/e2e/kms.go

Purpose: models KMS configurations used by encryption tests and provides validation hooks for reading and verifying deletion of encryption passphrases, especially in HashiCorp Vault.

Important APIs/types/functions: `kmsConfig` defines `canGetPassphrase()`, `getPassphrase()`, `canVerifyKeyDestroyed()`, and `verifyKeyDestroyed()`. `simpleKMS` is a provider-only implementation for KMS modes that cannot be inspected directly. `vaultConfig` embeds `simpleKMS`, adds `backendPath` and `destroyKeys`, and implements Vault CLI-based passphrase and deletion checks. Globals define `noKMS`, `secretsMetadataKMS`, `vaultKMS`, `vaultTokensKMS`, and `vaultTenantSAKMS`.

Control flow: simple KMS implementations return false/empty results. Vault `getPassphrase()` logs in to the in-cluster Vault service with the sample root token, then runs `vault kv get -field=data` for `backendPath+key` inside the Vault pod. `verifyKeyDestroyed()` reads Vault KV metadata `deletion_time`; non-empty stdout means the key metadata still exists and destruction failed, while empty stdout is treated as destroyed.

State and persistence: does not create KMS state itself, but reads state created by CSI encryption flows. Backend paths encode whether keys live under `secret/ceph-csi/`, `secret/`, or `tenant/`; `destroyKeys` expresses expected cleanup strength.

Dependencies and integration points: uses e2e pod exec helpers, `cephCSINamespace`, `metav1.ListOptions` selecting `app=vault`, and CephFS fscrypt validation helpers. It assumes Vault was deployed by `deploy-vault.go` and contains the sample token/config.

Risks: uses a hard-coded root token and Vault DNS name. CLI output parsing treats trimmed stdout/stderr as authoritative; Vault CLI or KV version changes can break expectations. `verifyKeyDestroyed()` assumes empty stdout means destruction even if stderr contains a transient Vault error, so callers must inspect returned message in context.

Test signals: encrypted volume tests can read passphrases while volumes exist, cannot read them after deletion, and for `destroyKeys` configs observe destroyed metadata rather than soft-deleted key records.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/kms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/log.go -->
# sources/control-plane/ceph-csi/e2e/log.go

Purpose: collects CSI and gateway pod logs for e2e failure diagnostics, including fallback to previous container logs when current logs are unavailable.

Important APIs/types/functions: `logsCSIPods(label, c)` lists pods in `cephCSINamespace` by label and logs each. `kubectlLogPod(c, pod)` iterates all containers in a pod, fetches current logs or previous logs, and writes formatted output to the framework log. `getPreviousPodLogs(c, namespace, podName, containerName)` calls the pod log subresource with `previous=true` and rejects responses containing `Internal Error`.

Control flow: failure hooks call `logsCSIPods()` for provisioner/nodeplugin labels. For each pod/container, the helper first calls Kubernetes e2e `GetPodLogs`; if that fails, it tries the previous log endpoint. It logs any retrieval failure but continues through remaining containers.

State and persistence: read-only against Kubernetes logs; writes diagnostic text to the test log stream.

Dependencies and integration points: uses Kubernetes CoreV1 pod list/log REST APIs, e2e framework logging, and pod framework log retrieval. CephFS, NFS, and NVMe-oF failure hooks rely on it before dumping namespace info.

Risks: large logs can make failing job output heavy. Previous-log fallback can mask current-log retrieval failure but still omit logs if the pod never restarted. The `Internal Error` string check is heuristic.

Test signals: visible `STARTLOG`/`ENDLOG` sections in failed e2e runs, including container name and node name, are the main signal. There are no direct unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/migration.go -->
# sources/control-plane/ceph-csi/e2e/migration.go

Purpose: supports RBD in-tree-to-CSI migration e2e scenarios by generating migration-style volume IDs, custom cluster ID config, migration Secrets, StorageClasses, and Ceph users.

Important APIs/types/functions: `composeIntreeMigVolID(mons, rbdImageName)` creates a migration volume ID from monitor hash, image UUID, and encoded pool name. `generateClusterIDConfigMapForMigration(f, c)` computes monitor hash cluster ID, writes a custom configmap, and restarts RBD CSI pods. `createRBDMigrationSecret()`, `createMigrationUserSecretAndSC()`, `createMigrationSC()`, `createProvNodeCephUserAndSecret()`, `deleteProvNodeMigrationSecret()`, `setupMigrationCMSecretAndSC()`, and `tearDownMigrationSetup()` manage secrets, users, storageclass, config, and cleanup.

Control flow: setup fetches monitors, hashes them to the in-tree migration cluster ID, updates the configmap, restarts RBD CSI pods, creates provisioner/node Ceph users with migration caps, writes migration-format Secrets where `key` replaces `userKey` and non-admin users become `adminId`, then creates an RBD StorageClass with migration-specific secret references and `migration=true`. Teardown restores the normal configmap and deletes migration Secrets.

State and persistence: mutates the shared Ceph-CSI ConfigMap, restarts CSI pods, creates Kubernetes Secrets, creates Ceph users, and creates/deletes a StorageClass. It relies on global RBD pool, namespace, secret names, and deployment metadata.

Dependencies and integration points: uses RBD helpers (`createRBDStorageClass`, `createRBDSecret`-style Secret templates, `rbdProvisionerCaps`, `rbdNodePluginCaps`), Ceph user helpers, configmap helpers, monitor hash helpers, and Kubernetes client-go. It is part of migration test setup rather than a standalone Ginkgo suite.

Risks: `composeIntreeMigVolID()` assumes `rbdImageName` contains `intreeVolPrefix`; missing prefix will panic on `imageUID[0]`. ConfigMap changes require pod recreation and can disrupt parallel tests. Secret deletion does not ignore NotFound. Ceph users created for migration are not explicitly deleted here, only their Secrets.

Test signals: expected migration volume IDs match CSI migration parser expectations, custom configmap cluster ID resolves monitors, RBD CSI pods restart successfully, migrated provisioning works with new secrets, and teardown restores normal config and removes migration Secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/namespace.go -->
# sources/control-plane/ceph-csi/e2e/namespace.go

Purpose: provides namespace lifecycle and template namespace-replacement helpers for e2e-deployed CSI components and auxiliary resources.

Important APIs/types/functions: `createNamespace(c, name)` creates a Namespace if needed and polls until it can be retrieved. `deleteNamespace(c, name)` deletes a Namespace if present and polls until it disappears. `replaceNamespaceInTemplate(filePath)` reads a YAML file and rewrites `namespace: default` or `namespace: "default"` to the current `cephCSINamespace`.

Control flow: creation uses client-go `Namespaces().Create()` and ignores AlreadyExists, then polls with retryable API error handling. Deletion ignores NotFound and polls until the API returns NotFound. Template replacement is a simple read and two `strings.ReplaceAll()` passes.

State and persistence: creates and deletes Kubernetes namespaces. Template replacement does not persist to disk; it returns modified YAML content for kubectl input.

Dependencies and integration points: uses Kubernetes CoreV1 Namespace APIs, wait polling, API error helpers, framework logging, and global `deployTimeout`, `poll`, and `cephCSINamespace`. Deployment, Vault, NFS, CephFS, and NVMe-oF resource deployers call these helpers.

Risks: namespace deletion can block on finalizers from leaked resources. Template replacement only handles exact namespace lines and may miss embedded names or replace too little for new templates. It does not preserve quotes when replacing `"default"`.

Test signals: namespace reaches gettable state before resources are applied, disappears after teardown, and templated resources land in the intended Ceph-CSI namespace.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/namespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nfs.go -->
# sources/control-plane/ceph-csi/e2e/nfs.go

Purpose: defines the ordered NFS CSI e2e suite and helper functions for deploying the NFS CSI plugin, creating a Ceph NFS server, and validating NFS-backed volumes built on CephFS subvolumes.

Important APIs/types/functions: `NFSDeployment` embeds `DriverInfo`. `deployNFSPlugin()`, `deleteNFSPlugin()`, `createNFSPool()`, and `createORDeleteNFSResources()` manage NFS CSI and Rook CephNFS resources. `createNFSStorageClass()` injects NFS cluster/server, CephFS, secret, pool, and clusterID parameters and sets the provisioner to `nfsDriverName`. `createNFSVolumeAttributesClass()` and `deleteNFSVolumeAttributesClass()` exercise Kubernetes VolumeAttributesClass. `unmountNFSVolume()` manually unmounts a pod volume from the nodeplugin. The Ginkgo `Describe("nfs")` owns setup, teardown, and specs.

Control flow: setup skips unless NFS testing is enabled and not upgrade/helm, chooses normal or operator deployment metadata, creates namespace if needed, creates `.nfs` pool and CephNFS resource, deploys CSI if requested, resets `subvolumegroup` to `csi`, writes configmap, creates CephFS-style provisioner/node users and Secrets, creates the subvolume group, and discovers the metadata pool. Teardown logs on failure, deletes config/Secrets/storageclass/subvolume group/plugin/namespace. Specs validate CSI readiness, SELinux mount options, RWOP, pool-backed binding, relocated server via VolumeAttributesClass on Kubernetes 1.34+, security flavors, restricted NFS clients, normal binding and normal-user access, multi-PVC lifecycle, data persistence, manual unmount deletion, service-account restrictions, read-only mounts, a currently skipped resize check, concurrent snapshot-to-PVC clones with checksum validation, concurrent PVC-to-PVC clones, and Ceph user cleanup.

State and persistence: creates NFS CSI resources, Rook CephNFS deployment, `.nfs` pool, CephFS subvolumes/snapshots/omap entries, Kubernetes StorageClasses/PVCs/PVs/Pods/VolumeSnapshots/VolumeAttributesClasses, and Ceph users. Backend counts are checked after create/delete phases.

Dependencies and integration points: uses CephFS helper functions because NFS exports are backed by CephFS subvolumes, plus NFS examples under `../examples/nfs/`, deployment YAML under `../deploy/nfs/kubernetes/`, snapshot helpers, resize/PVC helpers, client-go, and Ginkgo/Gomega.

Risks: NFS tests share global CephFS state (`subvolumegroup`, `fileSystemName`, `metadataPool`) and depend on CephFS users/caps. `createNFSPool()` intentionally does not delete `.nfs`, so external CephNFS config may persist. Some checksum mismatches are logged but only checksum calculation errors fail directly in clone loops. The resize test is disabled due to observed size mismatch. VolumeAttributesClass coverage depends on Kubernetes version.

Test signals: NFS CSI readiness, successful NFS mount and app binding, exports matching restricted clients, RWOP/read-only enforcement, CephFS subvolume/omap/snapshot counts returning to zero, checksum parity for snapshot/PVC clones, and clean user deletion are the core signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/node.go -->
# sources/control-plane/ceph-csi/e2e/node.go

Purpose: provides Kubernetes node label and node IP helper functions for topology, read-affinity, and node-targeted e2e behavior.

Important APIs/types/functions: `addLabelsToNodes(f, labels)` applies a label map to all nodes. `deleteNodeLabels(c, labelKeys)` removes labels from all nodes and verifies removal. `checkNodeHasLabel(c, labelKey, labelValue)` asserts every node has a label. `getKubeletIP(c)` returns the first node's `NodeInternalIP`.

Control flow: label helpers list all nodes through client-go, iterate over `nodes.Items`, and use Kubernetes test utils or framework node expectations to add/remove/verify labels. `getKubeletIP()` lists nodes, inspects the first node's status addresses, and returns the internal IP if present.

State and persistence: mutates labels on cluster Node objects. Label cleanup must run to avoid affecting later tests. IP lookup is read-only.

Dependencies and integration points: uses Kubernetes CoreV1 Node APIs, `k8s.io/kubernetes/test/utils`, e2e node expectations, and shared framework. Read-affinity/topology tests elsewhere rely on these helpers.

Risks: all nodes receive identical labels, which is adequate for simple tests but not for multi-zone differentiation. `getKubeletIP()` assumes at least one node and returns only the first node's internal IP. Label removal failures can pollute the cluster for later specs.

Test signals: node labels are visible through API expectations, labels are verified removed, and returned internal IP is usable for tests that need kubelet/node addressing.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof-deploy.go -->
# sources/control-plane/ceph-csi/e2e/nvmeof-deploy.go

Purpose: deploys and configures the NVMe-oF CSI plugin for e2e tests, including OpenShift SCC handling, configmap creation, StorageClass generation with gateway listener information, and Ceph credentials.

Important APIs/types/functions: path/name globals describe NVMe-oF deploy/example YAMLs and secret/user names. `createORDeleteNVMeoFResources(action)` applies SCCs when OpenShift and then CSI driver, config, RBAC, provisioner, and nodeplugin YAML. `deployNVMeoFPlugin(f, deployTimeout)` creates the ConfigMap, applies resources, and waits for CSI readiness. `deleteNVMeoFPlugin()` reverses those steps. `createNVMeoFStorageClass(f, name, scOptions, parameters, policy)` loads the example StorageClass and injects secrets, clusterID, subsystem NQN, gateway address/listeners, binding mode, mount options, and reclaim policy. `deleteNVMeofStorageClass()` and `createNVMeoFCredentials()` manage storageclass and Ceph user Secret lifecycle.

Control flow: resource deployment builds a `ResourceDeployer` slice, optionally prepending SCC YAML with namespace replacement for OpenShift. StorageClass creation discovers cluster ID, gets gateway pod host/IP, writes `nvmeofGatewayAddress` and JSON `listeners`, creates a unique subsystem NQN from the framework namespace, applies caller parameter overrides with empty-value deletion, then polls StorageClass creation.

State and persistence: creates Ceph-CSI ConfigMap, NVMe-oF CSI Kubernetes resources, Ceph users, Kubernetes Secrets, and StorageClasses. The StorageClass persists gateway IP and listener JSON, so gateway pod recreation can stale it.

Dependencies and integration points: uses deployment resource abstractions, configmap helpers, `getNVMeofGateway()`, Ceph user/RBD secret helpers, RBD caps, Kubernetes storage APIs, and Gomega expectations. The NVMe-oF Ginkgo suite calls these during setup/teardown.

Risks: gateway pod IP is captured at StorageClass creation and may change if the gateway restarts. `deleteNVMeofStorageClass()` clears errors only when `IsNotFound` is true; other delete errors fail. NVMe-oF credentials reuse broad RBD caps with empty pool/namespace strings. OpenShift SCC string replacement assumes `:default:` markers in templates.

Test signals: CSI deployment and daemonset readiness, StorageClass creation with correct listener JSON, successful provisioning through the gateway, and cleanup of StorageClass/configmap/resources are the main signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof-deploy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof-gateway.go -->
# sources/control-plane/ceph-csi/e2e/nvmeof-gateway.go

Purpose: deploys the temporary NVMe-oF gateway used by the NVMe-oF e2e suite and exposes the gateway pod identity/IP for StorageClass configuration.

Important APIs/types/functions: constants point to gateway YAML files under `e2e/nvmeof/`. `createORDeleteGateway(action)` applies optional OpenShift SCC plus ServiceAccount, ConfigMap, and Deployment in `rookNamespace`. `deployGateway(f, deployTimeout)` creates the backing pool, applies resources, waits for the gateway Deployment and pod, and dumps container logs if startup fails. `deleteGateway(f)` removes resources and deletes the pool. `getNVMeofGateway(c)` returns the single gateway pod name and pod IP.

Control flow: deployment first creates the `nvmeofPool`, applies templates, waits for Deployment availability, finds the pod by `app=ceph-nvmeof-gateway`, and waits for Running. On pod wait failure, it fetches logs from `generate-minimal-ceph-conf` and `nvmeof-gateway` before asserting failure. Deletion removes YAML resources then deletes the pool.

State and persistence: creates a Ceph pool, Kubernetes ServiceAccount, ConfigMap, Deployment, optional SCC, and gateway pod in the Rook namespace. The gateway registers itself with Ceph through its init container.

Dependencies and integration points: uses generic resource deployers, pool helpers, pod/deployment wait helpers, Kubernetes pod logs, global `rookNamespace`, `isOpenShift`, and `nvmeofPool`. `createNVMeoFStorageClass()` consumes the gateway pod IP returned here.

Risks: the helper expects exactly one gateway pod. There is no Kubernetes Service abstraction here, so tests depend on the pod IP staying valid. Pool deletion after gateway removal can fail if backend objects remain. SCC namespace replacement assumes the YAML contains `:rook-ceph:`.

Test signals: pool creation, gateway Deployment availability, pod Running, usable gateway IP in StorageClass, and successful pool deletion during teardown.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof-gateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof.go -->
# sources/control-plane/ceph-csi/e2e/nvmeof.go

Purpose: defines the NVMe-oF CSI e2e suite, covering basic provisioning/deletion, filesystem and block resize, service-account restriction, and node-side GroupLock concurrency behavior.

Important APIs/types/functions: constant `nvmeofPool` names the RBD pool used by the gateway. The Ginkgo `Describe("nvmeof")` gates on `testNVMeoF`, skips helm/operator deployments, sets a privileged framework, and uses `deployGateway()`, `createNVMeoFCredentials()`, `deployNVMeoFPlugin()`, and `createNVMeoFStorageClass()` in setup. Specs call `createPVCAndvalidatePV()`, `validateRBDImageCount()`, `validateOmapCount()`, `validateServiceAccountVolumeRestriction()`, `resizePVCAndValidateSize()`, `createConcurrentPods()`, `deleteConcurrentPods()`, and `mixedCreateDeletePodsOnly()`.

Control flow: `BeforeEach(... OncePerOrdered)` checks Ceph version and skips below Tentacle/v20, deploys the gateway, creates namespace if needed, creates Ceph credentials, deploys the CSI plugin, and creates a per-suite StorageClass targeting `nvmeofPool`. `AfterEach(... OncePerOrdered)` logs CSI and gateway pods on failure, dumps namespace info, deletes plugin, gateway, and StorageClass. The ordered context creates and deletes a PVC, then validates service-account restriction and backend cleanup; resizes filesystem and raw-block PVCs; creates three PVCs then concurrent pods and concurrent deletions to test node GroupLock; and runs a larger mixed create/delete workload with 15 PVCs in batches of five.

State and persistence: creates gateway/pool, CSI resources, StorageClass, PVC/PV/Pod objects, RBD images, omap entries, and service-account metadata. Each spec validates backend image and omap counts return to zero.

Dependencies and integration points: depends on Ceph version helpers, RBD validation helpers, NVMe-oF deployment/gateway helpers, shared PVC/pod concurrency helpers, Ginkgo/Gomega, Kubernetes framework, and pod-security admission.

Risks: suite requires Ceph v20/Tentacle and a working gateway image; otherwise it skips. It only supports simple YAML deployment, not helm/operator. StorageClass gateway IP can stale if gateway restarts. GroupLock tests focus on node-stage/unstage pod operations and deliberately avoid controller concurrency, so they do not cover all lock interactions.

Test signals: successful skip on unsupported Ceph, CSI readiness, backend image/omap counts matching PVC lifecycle, successful service-account restriction, resize validation for filesystem and block, no errors/deadlocks in concurrent pod create/delete flows, and zero backend artifacts after cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/config.yaml -->
# sources/control-plane/ceph-csi/e2e/nvmeof/config.yaml

Purpose: defines the ConfigMap consumed by the temporary NVMe-oF gateway deployment. Its `config` key is a full `ceph-nvmeof.conf` template with Kubernetes placeholders for pod name, ANA group, and pod IP.

Important APIs/types/functions: the Kubernetes resource is a `v1 ConfigMap` named `ceph-nvmeof-config` labeled `app=ceph-nvmeof-gateway`. The embedded configuration includes sections `[gateway]`, `[gateway-logs]`, `[discovery]`, `[ceph]`, `[mtls]`, `[spdk]`, and `[monitor]`.

Control flow: `deployment.yaml` mounts this ConfigMap at `/config`; the init container runs `sed` to replace `@@POD_NAME@@`, `@@ANA_GROUP@@`, and `@@POD_IP@@`, producing `/etc/ceph/nvmeof.conf`. The gateway container then starts with `-c /etc/ceph/nvmeof.conf`.

State and persistence: stores gateway runtime configuration in Kubernetes. The config points the gateway at `nvmeofpool`, disables auth, disables strict listener IP verification, enables state update notifications, sets debug logging, sets discovery to `0.0.0.0:8009`, and configures SPDK memory/tgt path/timeouts.

Dependencies and integration points: mounted by the gateway Deployment, paired with Ceph monitor/keyring data from Rook Secrets, and coordinated with the pool and listener values injected into NVMe-oF CSI StorageClasses.

Risks: many values are test-static (`nvmeofpool`, admin Ceph ID, auth disabled, fixed ports, `verify_listener_ip=False`). Config comments note TODOs for dynamic name/group/address and service behavior. Drift between this config and StorageClass listener/gateway parameters can break provisioning.

Test signals: init container successfully renders the config, `ceph nvme-gw create/show` succeeds, the gateway starts, and CSI can create NVMe-oF-backed volumes through the configured listener.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/deployment.yaml -->
# sources/control-plane/ceph-csi/e2e/nvmeof/deployment.yaml

Purpose: deploys the temporary `ceph-nvmeof-gateway` workload used by e2e tests to expose RBD images over NVMe-oF.

Important APIs/types/functions: defines an `apps/v1 Deployment` with one replica, label `app=ceph-nvmeof-gateway`, main container `nvmeof-gateway` using `quay.io/ceph/nvmeof:1.5`, and init container `generate-minimal-ceph-conf` using `quay.io/ceph/ceph:v19`. It exposes TCP ports 4420, 5500, 5499, and 8009 and uses service account `ceph-nvmeof-gateway`.

Control flow: the init container reads monitor host from `rook-ceph-config`, writes `/etc/ceph/ceph.conf`, copies the admin keyring, renders `/etc/ceph/nvmeof.conf` from the ConfigMap template, and registers the gateway with `ceph nvme-gw create ${POD_NAME} nvmeofpool ${ANA_GROUP}` followed by `show`. The main container starts the gateway with the rendered config.

State and persistence: uses an `emptyDir` for generated `/etc/ceph`, a Secret volume for `rook-ceph-admin-keyring`, and a projected ConfigMap volume for gateway config. It registers gateway state in Ceph for `nvmeofpool`.

Dependencies and integration points: depends on Rook Secrets/ConfigMap, the `ceph-nvmeof-config` ConfigMap, the `ceph-nvmeof-gateway` ServiceAccount, and privileged container permissions. The e2e gateway helper waits on this Deployment and uses the resulting pod IP.

Risks: both init and main containers run privileged; admin keyring is mounted into the pod. Image tags are fixed and can drift from cluster Ceph version. There is no Service, so pod IP volatility matters. The init container hard-codes `nvmeofpool` and depends on `ceph nvme-gw` CLI availability.

Test signals: Deployment available, pod running, init logs showing rendered config and successful `ceph nvme-gw show`, open listener ports, and successful CSI provisioning through the gateway.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/scc.yaml -->
# sources/control-plane/ceph-csi/e2e/nvmeof/scc.yaml

Purpose: grants OpenShift SecurityContextConstraints needed by the temporary NVMe-oF gateway service account.

Important APIs/types/functions: defines a `security.openshift.io/v1 SecurityContextConstraints` named `ceph-nvmeof` allowing privileged containers, host networking, host ports, `SYS_ADMIN`, `RunAsAny`, `seLinuxContext RunAsAny`, broad volume types, and user `system:serviceaccount:rook-ceph:ceph-nvmeof-gateway`.

Control flow: `createORDeleteGateway()` applies this resource only when `isOpenShift` is true and rewrites the service-account namespace marker if `rookNamespace` differs.

State and persistence: persists a cluster-scoped SCC granting elevated privileges to the gateway SA until gateway teardown deletes it.

Dependencies and integration points: tied to `serviceaccount.yaml` and `deployment.yaml`; OpenShift clusters require it for privileged SPDK/NVMe-oF gateway operation.

Risks: it grants powerful privileges and host networking/ports. The comment says "ssc" but resource is SCC. Namespace/user replacement must stay aligned with the service account namespace.

Test signals: on OpenShift, gateway pod admission succeeds instead of failing SCC validation, and teardown removes the SCC.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/scc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/serviceaccount.yaml -->
# sources/control-plane/ceph-csi/e2e/nvmeof/serviceaccount.yaml

Purpose: defines the service account used by the temporary NVMe-oF gateway Deployment.

Important APIs/types/functions: a single `v1 ServiceAccount` named `ceph-nvmeof-gateway`.

Control flow: `createORDeleteGateway()` applies this YAML in `rookNamespace` before the gateway ConfigMap and Deployment. The Deployment references it through both `serviceAccount` and `serviceAccountName`.

State and persistence: creates a namespaced Kubernetes ServiceAccount for the gateway pod. It is deleted during gateway teardown.

Dependencies and integration points: paired with OpenShift SCC user binding and the gateway Deployment. It controls the identity under which the privileged gateway pod is admitted.

Risks: no RBAC is defined in this file; the pod relies mainly on mounted Rook Secrets and SCC privileges. Name changes must be synchronized with `deployment.yaml` and `scc.yaml`.

Test signals: gateway pod can start with this service account, and OpenShift SCC binding matches `system:serviceaccount:<rookNamespace>:ceph-nvmeof-gateway`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/nvmeof/serviceaccount.yaml -->
