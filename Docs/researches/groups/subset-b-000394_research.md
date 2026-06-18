# subset-b-000394 research

Grouped research report for the requested JuiceFS CSI controller, dashboard, dashboard service, and CSI controller files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pod_driver_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/controller/pod_driver_test.go

## Purpose
This test file validates the `PodDriver` mount-pod reconciliation behavior used by the node-side reconciler. It covers pod status classification, ready-pod mount recovery, deleted-pod cleanup and recreation, and error-pod cleanup paths.

## Important APIs, Types, And Functions
The top-level `TestPodDriver_getPodStatus` table checks the private `getPodStatus` classifier against ready, pending, deleted, failed, unknown, crash-loop, and resource-error pods. The Ginkgo `Describe("pod handler")` suite exercises `podReadyHandler`, `podDeletedHandler`, and `podErrorHandler`. Helper fixtures include `readyPod`, `deletedPod`, `errorPod1`, `resourceErrPod`, `pendingPod`, `runningPod`, `copyPod`, and `genMountInfos`.

## Control Flow
The suite constructs a fake Kubernetes client and `mount.SafeFormatAndMount`, patches OS/mount/client functions with `gomonkey`, and then drives handler scenarios. Ready-pod tests simulate source and target `os.Stat` states, mountinfo parsing, ENOTCONN recovery, mount failures, bad mount commands, missing annotations, target path format issues, and subpath roots. Delete-pod tests simulate unmount commands, finalizer removal, absent annotations, recreated mount pods, resource-error skips, and lazy unmount fallback. Error-pod tests simulate resource exhaustion, missing source paths, finalizer patch failures, and paths that are no longer mount points.

## State And Persistence
State is in fake Kubernetes objects, pod finalizers/annotations, patched filesystem probes, and the process-global monkey patches. `passfd.InitTestFds` sets test file descriptors for FUSE abort paths. No persistent state is written except cleanup of a local `tmp` directory in `AfterEach`.

## Dependencies And Integration Points
The tests integrate with `pkg/controller/pod_driver.go`, `pkg/controller/mountinfo.go`, `pkg/util`, `pkg/k8sclient`, and mock file-info types under `pkg/driver/mocks`. They depend on Kubernetes fake clients, `k8s.io/utils/mount`, `ginkgo/gomega`, and `gomonkey`.

## Risks
Monkey patch ordering is fragile because several scenarios use sequential `os.Stat` outputs; production changes that add or remove probes can make tests fail without a behavior regression. The tests cover private functions in the same package, so they are strong regression signals but also tightly coupled to implementation details. Several paths expect nil errors for defensive no-op cases, which should be preserved intentionally.

## Test Signals
This is the main test signal for mount-pod lifecycle recovery. Passing tests indicate that status classification, mount recovery from stale FUSE/ENOTCONN paths, deletion finalizer handling, lazy unmount fallback, and resource-error cleanup remain compatible with the reconciler.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pod_driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pv_controller.go -->
# sources/control-plane/juicefs-csi-driver/pkg/controller/pv_controller.go

## Purpose
`PVController` watches JuiceFS CSI persistent volumes to discover `NodePublishSecretRef` secrets and trigger initialization of enterprise `initconfig` data for those secrets.

## Important APIs, Types, And Functions
The file defines the package-global `watchedSecrets sync.Map`, `PVController`, `NewPVController`, `Reconcile`, `shouldPVInQueue`, and `SetupWithManager`. `Reconcile` stores `namespace/name` secret keys and calls `refreshSecretInitConfig`.

## Control Flow
On reconcile, the controller fetches the PV by name, ignores not-found errors, checks for a CSI source with a node publish secret, stores that secret in `watchedSecrets`, and refreshes the secret init config. Queue predicates accept only JuiceFS CSI PVs with `NodePublishSecretRef` whose secret is not already watched. During setup, it lists all PVs once and pre-populates `watchedSecrets`, then registers create/update watches for PVs.

## State And Persistence
`watchedSecrets` is in-memory process state shared with `SecretController`. The persistent side effect is indirect: `refreshSecretInitConfig` may update Kubernetes Secret data and annotations. A controller restart rebuilds the watch set from current PVs.

## Dependencies And Integration Points
It depends on controller-runtime watches/predicates, `k8sclient.K8sClient`, corev1 PVs, and `config.DriverName`. It is coupled to `secret_controller.go` through `watchedSecrets` and `refreshSecretInitConfig`.

## Risks
Because updates are skipped once a secret is watched, a PV changing to a different secret may not refresh unless the predicate admits the new key. The process-global map has no deletion path for unused secrets, so long-running controllers can retain stale keys. Setup does not call `refreshSecretInitConfig` for pre-existing PVs because it only stores keys, so refresh behavior depends on later secret reconciles or PV events.

## Test Signals
There is no direct test in this subset. Useful coverage would assert predicate behavior, initial PV scan behavior, and interaction with `SecretController` for first-time and changed secret references.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pv_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/reconciler.go -->
# sources/control-plane/juicefs-csi-driver/pkg/controller/reconciler.go

## Purpose
This file starts and runs the node-side mount-pod reconciler that periodically inspects kubelet pod state and repairs JuiceFS mount pods on the node.

## Important APIs, Types, And Functions
It defines retry constants, `PodReconciler`, `StartReconciler`, `PodStatus`, and `doReconcile`. `StartReconciler` builds a kubelet client and Kubernetes client; `doReconcile` owns the infinite reconciliation loop.

## Control Flow
`StartReconciler` parses `config.KubeletPort`, creates a kubelet client for `config.HostIp`, verifies access, creates a Kubernetes client, and starts `doReconcile` in a goroutine. `doReconcile` loops forever: it creates a timeout context, fetches node-running pods from kubelet, creates a `PodDriver`, installs current mountinfo, filters mount pods in the CSI namespace by JuiceFS pod-type label, skips unchanged pod statuses until their `nextSyncAt`, honors the immediate-reconcile annotation, applies a shared backoff for API rate-limit errors, and runs `podDriver.Run` concurrently through an errgroup.

## State And Persistence
Runtime state is `lastPodStatus`, guarded by a mutex, plus a `flowcontrol.BackOff` keyed as `"mountpod"` for all pods. Persistence is limited to Kubernetes pod annotation mutation: the immediate reconciler annotation is removed after a reconcile attempt. The mountinfo table is rebuilt each loop.

## Dependencies And Integration Points
It depends on `k8sclient.KubeletClient`, `PodDriver`, `newMountInfoTable`, controller config values, `common.ImmediateReconcilerKey`, and `resource.DelPodAnnotation`. It is the scheduler around the handler behavior tested in `pod_driver_test.go`.

## Risks
The loop has no stop channel other than process exit, and it intentionally ignores `errgroup.Wait` errors after logging inside workers. The shared backoff ID can throttle all mount pods after one rate-limit error. The goroutine closes over the loop variable `pod`; because `pod` is declared with `:=` inside the loop body in modern Go this is usually safe, but it remains a sensitive pattern to review with compiler version assumptions.

## Test Signals
The direct reconciler loop is not tested here. Indirect confidence comes from `pod_driver_test.go`; additional tests would need fake kubelet clients and controllable time/backoff to validate skip, immediate-reconcile, and rate-limit behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/reconciler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/secret_controller.go -->
# sources/control-plane/juicefs-csi-driver/pkg/controller/secret_controller.go

## Purpose
`SecretController` watches PV-referenced JuiceFS secrets, cleans legacy orphan mount-pod secrets, and maintains enterprise `initconfig` content inside Kubernetes Secret data.

## Important APIs, Types, And Functions
Key functions are `checkAndCleanOrphanSecret`, `refreshSecretInitConfig`, `SecretController.Reconcile`, `shouldSecretInQueue`, and `SetupWithManager`. Important annotations are `juicefs/last-update-at` and `juicefs/secret-fields-hash`.

## Control Flow
`checkAndCleanOrphanSecret` filters to legacy CSI namespace secrets named `juicefs-*-secret`, skips newly created or labeled secrets, requires JuiceFS token/meta fields and `check_mount.sh`, and deletes the secret if the corresponding mount pod no longer exists. `refreshSecretInitConfig` loads the secret, skips CE/metaurl or incomplete secrets, builds JuiceFS settings, hashes auth-sensitive fields, throttles refreshes when unchanged and recently updated, prepares temporary config files for ceph/gs credential mounts, runs `jfs.AuthFs`, reads the generated client config, and updates Secret `StringData` plus annotations. `Reconcile` fetches the secret, performs orphan cleanup, refreshes init config, and requeues after `config.SecretReconcilerInterval`.

## State And Persistence
Persistent state is the Kubernetes Secret data and annotations, especially `initconfig`, update time, and field hash. Temporary filesystem state is created under `os.TempDir()` and, for ceph/gs config secrets, potentially at backend-specific mount paths, then cleaned by defers. Queue eligibility depends on the in-memory `watchedSecrets` map populated by `PVController`.

## Dependencies And Integration Points
The controller integrates with JuiceFS auth/settings generation, `config.KeysCompatible`, Kubernetes secrets, PV controller state, and controller-runtime secret watches. It also interacts with storage-backend config secrets for ceph and Google storage credentials.

## Risks
This path writes local credential files to configured mount paths and must clean them reliably; existing files are treated as errors to avoid overwrites. Failed forced auth removes stale `initconfig` from local maps before updating the Secret, which can affect mounts that rely on it. The queue depends on PV discovery, so a secret created before its PV is observed is ignored until watched. The update writes `StringData` from all current secret data, so binary or large secret values should be considered carefully.

## Test Signals
No direct tests are in this subset. High-value tests would cover hash/throttle behavior, CE/metaurl skips, auth-failure deletion of `initconfig`, ceph/gs config file cleanup, and orphan secret deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/secret_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/api.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/api.go

## Purpose
This file defines the dashboard API object, wires Kubernetes clients and service implementations, and registers all REST and websocket routes.

## Important APIs, Types, And Functions
`API` stores namespace, manager mode, cached/controller clients, a typed `k8sclient`, REST config, and service interfaces for pods, PVs, PVCs, secrets, jobs, and events. `NewAPI` constructs services, `Handle` registers routes, and `getVersion` returns driver version data.

## Control Flow
`NewAPI` creates a `k8sclient` from the REST config and chooses cached or uncached services based on `enableManager`. `Handle` attaches top-level list/config/version routes, scoped pod/PV/PVC/storageclass groups with middleware, batch upgrade routes, cache-group routes, and websocket endpoints for logs, exec, debug, warmup, stats, smooth upgrade, and access logs.

## State And Persistence
The `API` object holds process-local service references and client handles. It does not persist data directly; handlers persist through Kubernetes resources such as ConfigMaps, Jobs, node labels, Secrets, and Pods.

## Dependencies And Integration Points
It integrates Gin routing, controller-runtime clients, Kubernetes REST config, driver versioning, and the dashboard service packages. Route groups are the central integration surface for `pod.go`, `pv.go`, `cm.go`, `batch.go`, and `cache_group.go`.

## Risks
`NewAPI` returns nil if client construction fails, so callers must check before routing. The route surface exposes powerful pod exec and cluster mutation endpoints; deployment authentication/authorization must be enforced outside these handlers. Cached mode changes pagination semantics from continue tokens to current/page-size pages.

## Test Signals
No route registration tests are in this subset. Useful tests would assert route presence, nil-client behavior, and cached/uncached service selection.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/batch.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/batch.go

## Purpose
`batch.go` implements dashboard endpoints and helpers for smooth upgrade batch jobs that upgrade mount pods through a Kubernetes Job and ConfigMap-backed batch plan.

## Important APIs, Types, And Functions
Important types are `ListJobResult`, `UpgradeJob`, `PodDiff`, and `ListDiffPodResult`. Key functions include `createUpgradeJob`, `listUpgradeJobs`, `getUpgradeJob`, `updateUpgradeJob`, `deleteUpgradeJob`, `getUpgradeJobLog`, `watchUpgradeJobLog`, `NewUpgradeJob`, `genPodDiffs`, `GenPodDiffs`, `GenUpgradeJobName`, `GenUpgradeConfig`, `getAllUpgradeConfig`, `getPodOfUpgradeJob`, `CanDoAction`, and `doActionInUpgradeJob`.

## Control Flow
Job creation validates smooth upgrade is enabled, binds request body filters, selects upgrade-eligible mount pods, computes config diffs, creates a batch ConfigMap, creates a dashboard Job, then sets the ConfigMap owner reference to the Job. Listing joins Jobs from `JobService` with loaded batch configs. Get-job loads the Job/config, lists current batch pods, recomputes diffs, and paginates them. Update-job validates action state transitions and sends POSIX signals to PID 1 in the job pod through Kubernetes exec. Log endpoints either return current pod logs or stream them to a websocket after waiting for the job pod to leave Pending.

## State And Persistence
Persistent state is the batch upgrade ConfigMap, the Kubernetes Job, its pod, and Job-owned ConfigMap references. Runtime state includes computed diff maps for PVs/PVCs/secrets/nodes. `NewUpgradeJob` uses `DASHBOARD_IMAGE` and optionally `JUICEFS_CSI_DASHBOARD_SA`.

## Dependencies And Integration Points
This file integrates pod, PV, PVC, secret, and job services; `config.BatchConfig`; `config.GetDiffWithNode`; Kubernetes batch/core APIs; SPDY remotecommand; websocket log piping; and dashboard utilities for pod classification and log streaming.

## Risks
Several paths assume labels and config references exist on Jobs. `getUpgradeJobLog` lists the job pod but calls `GetLogs(jobName, ...)`, which relies on pod name matching job name and can break if Kubernetes creates a suffixed pod name. Actions send signals to PID 1 in the upgrade container, so image entrypoint behavior is part of the API contract. Diff generation returns errors when any pod setting cannot be reconstructed, which can block job creation.

## Test Signals
No direct tests are included. Test coverage should focus on `CanDoAction`, `GenPodDiffs` map joins, generated Job spec, and log/action behavior against fake or envtest Kubernetes clients.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/batch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/cache_group.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/cache_group.go

## Purpose
This file exposes CRUD and worker-management endpoints for JuiceFS CacheGroup custom resources and their worker pods.

## Important APIs, Types, And Functions
Key handlers are `listCacheGroups`, `createCacheGroup`, `deleteCacheGroup`, `updateCacheGroup`, `getCacheGroup`, `listCacheGroupWorkers`, `addWorker`, `removeWorker`, and `getCacheWorkerBytes`. `validateCg` enforces the required secret reference and worker node selector.

## Control Flow
CRUD handlers read route params or JSON bodies, validate referenced secrets and worker selector fields, then use the manager client to create/update/delete CacheGroup resources. Worker listing fetches the CacheGroup, selects pods with cache-group worker labels, sorts by creation time, applies name/node filters while paginating, and returns items plus total. `addWorker` and `removeWorker` mutate node labels according to the CacheGroup worker selector; cache-byte lookup calls the operator utility against a worker pod.

## State And Persistence
Persistent state is CacheGroup CRs, Node labels used to schedule workers, and worker pod state created by the cache-group operator. Handler-local state is only request filtering and pagination data.

## Dependencies And Integration Points
It depends on `juicefs-cache-group-operator` API/common/utils packages, controller-runtime clients, Kubernetes pods/nodes/secrets, and Gin. It is an extension integration point between the CSI dashboard and the cache-group operator.

## Risks
`updateCacheGroup` validates the existing object rather than the submitted body, so invalid updates can bypass part of validation. Node label mutation directly changes cluster scheduling signals and can remove labels that other workloads may share. Worker pagination applies filters after start offset while total reports unfiltered worker count, which can surprise UI pagination.

## Test Signals
No tests are present. Useful tests would cover validation, update-body validation, node label add/remove idempotency, and worker list pagination/filter totals.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/cache_group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/cm.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/cm.go

## Purpose
`cm.go` provides dashboard endpoints for reading/updating the CSI global ConfigMap and computing whether mount pods differ from current configuration.

## Important APIs, Types, And Functions
Handlers are `getCSIConfig`, `putCSIConfig`, and `getCSIConfigDiff`. Utility functions are `DiffConfig` and `DiffConfigWithNode`.

## Control Flow
`getCSIConfig` fetches the global config ConfigMap from the system namespace. `putCSIConfig` binds and validates a ConfigMap named `config.GetGlobalConfigName`, unmarshals `config.yaml`, updates it, then annotates CSI node pods with `juicefs/update-time` to trigger reload behavior. `getCSIConfigDiff` lists upgrade candidate pods filtered by node/uniqueId, computes diffs, paginates `PodDiff` results, and returns them. `DiffConfigWithNode` reconstructs a setting, renews it, and compares the computed hash to the pod hash label.

## State And Persistence
Persistent state includes the global ConfigMap and CSI node pod annotations. Diff operations are read-only and derive state from Pods, PVs, PVCs, Secrets, and Nodes.

## Dependencies And Integration Points
It depends on `config.Config` parsing, `config.RevertSettingWithNode`, `config.JfsSetting.ReNew`, pod/PV/PVC/secret services through `genPodDiffs`, and Kubernetes core APIs.

## Risks
Updating config directly affects all CSI nodes and mount-pod reconciliation. The reload trigger mutates all matching CSI node pods and fails the request on the first update error. Diff correctness depends on reconstructing old and new settings with the same inputs used by the mount controller.

## Test Signals
No direct tests are present. Useful coverage would validate ConfigMap name/config parsing, CSI node annotation mutation, and hash-diff behavior for changed and unchanged settings.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/cm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/controller.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/controller.go

## Purpose
This file starts controller-runtime cache-backed dashboard service reconcilers when dashboard manager mode is enabled.

## Important APIs, Types, And Functions
The only exported behavior is `API.StartManager`. It type-asserts the API services to `CachePodService`, `CachePVService`, `CachePVCService`, `CacheSecretService`, and `CacheJobService`.

## Control Flow
`StartManager` registers each cache service with the supplied manager through its `SetupWithManager` method. If any service is not a cache implementation, it returns an explanatory error. After all watches are installed, it calls `mgr.Start(ctx)`.

## State And Persistence
State is the controller-runtime manager cache and each cache service's in-memory time-ordered indexes. No Kubernetes object is directly mutated by this file; reconcilers may mutate indexes as watches fire.

## Dependencies And Integration Points
It integrates `API.NewAPI` service selection with controller-runtime manager lifecycle. It is the bridge that makes cached list endpoints work.

## Risks
`StartManager` is only valid when `enableManager` produced cache services; otherwise it fails at runtime. Since `mgr.Start` blocks until context cancellation, callers must run it in an appropriate goroutine or lifecycle lane.

## Test Signals
No tests are present. Tests should check failure when services are uncached and successful setup with fake manager/controller registrations.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/pod.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/pod.go

## Purpose
`pod.go` implements pod-focused dashboard HTTP handlers: listing app/system/CSI pods, fetching pod details, logs/events/node relations, mount/app-pod relationships, debug bundle downloads, websocket terminal operations, and smooth single-pod upgrade.

## Important APIs, Types, And Functions
Key handlers include `listAppPod`, `listSysPod`, `listCSINodePod`, `getPodMiddileware`, `getPodHandler`, `getPodLatestImage`, `getPodEvents`, `getPodNode`, `getPodLogs`, `listMountPodsOfAppPod`, `listAppPodsOfMountPod`, websocket wrappers for pod service methods, `downloadDebugFile`, `downloadDebugInfo`, and `smoothUpgrade`.

## Control Flow
Middleware fetches the requested pod from the cache and admits app pods, system pods, or PVC-using app pods. Pod detail desensitizes non-system pods. Log handlers validate container names and either return raw logs or delegate websocket streaming. Relationship handlers call `PodService` methods. `downloadDebugInfo` builds a temporary `/tmp/<namespace>/<pod>/info` directory, downloads CSI node and mount-pod logs/YAML, PV/PVC/global config YAML when available, zips the directory, and returns it. `smoothUpgrade` opens a websocket, checks upgrade is enabled, finds the mount pod and its CSI node, then execs `juicefs-csi-driver upgrade <mountpod>` in the CSI node plugin container.

## State And Persistence
Most operations are read-only. Debug bundle generation writes temporary files under `/tmp` and removes the info directory afterward. Smooth upgrade mutates cluster runtime state indirectly through an exec command in a CSI node pod.

## Dependencies And Integration Points
It depends on `PodService`, `EventService`, PV service lookup, `resource.DownloadPodLog`, `resource.ExecInPod`, `config.GenSettingAttrWithMountPod`, global config loading, and dashboard utility functions for pod classification and safe path names.

## Risks
`getCSINode` returns `&pods[0]` without checking length, so callers can panic if no CSI node pod is found; some callers wrap it indirectly but not all. `downloadDebugInfo` appears to call `GetPersistentVolume` when it intends to fetch a PVC after finding a PV, which may prevent PVC YAML capture. Exec/log/debug endpoints are privileged and need external auth controls. Temporary directory permissions use broad mode `0777`.

## Test Signals
No direct tests are present. Useful coverage should include middleware admission, desensitization, missing CSI node handling, debug bundle file composition, and smooth-upgrade command generation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/pod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/pv.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/pv.go

## Purpose
`pv.go` implements PV, PVC, and StorageClass dashboard endpoints and resource relationship helpers.

## Important APIs, Types, And Functions
It defines `PVCWithMountPod`, `ListPVPodResult`, `ListPVCPodResult`, `ListSCResult`, and its sort methods. Handlers include list/get middleware for PV/PVC/SC, list PVC selector results, unique ID lookup, event endpoints, mount-pod relation endpoints, and PVs of a StorageClass. Helpers include `getPV`, `getPVC`, and `getStorageClass`.

## Control Flow
List handlers delegate to PV/PVC services or list StorageClasses from the cache, filter by driver/name, sort by creation time, and paginate. Middleware fetches and validates resources, rejecting non-JuiceFS PVs/storageclasses. `listPVCWithSelectorHandler` loads either posted config or current global config, lists mount pods, groups them by unique ID, then resolves each configured PVC selector by exact name, storage class, or label selector. Event handlers call `EventService`. Mount-pod relation endpoints list pods matching `LabelSelectorOfMount`.

## State And Persistence
The handlers are mostly read-only. State is derived from cached Kubernetes PVs, PVCs, StorageClasses, Pods, events, and config. No persistent mutation occurs in this file.

## Dependencies And Integration Points
It depends on PV/PVC/Pod/Event services, `config.DriverName`, `config.LoadFromConfigMap`, `config.MountPodPatch`, dashboard utilities, and controller-runtime cache reads.

## Risks
Exact-name PVC selector uses `CoreV1().PersistentVolumeClaims("").Get`, which is unusual for a namespaced resource and may not work as intended. `getPVC` ignores request context by using `context.Background`. StorageClass sorting uses `Total` as the slice length, so `Total` must always match `len(SCs)` before sorting. Unique-ID behavior changes for share-mount mode by sampling the first CSI node pod.

## Test Signals
No direct tests are present except `utils_test.go` exercising `ListSCResult` via reverse sort. Additional tests should cover PVC selector modes, middleware validation, and pagination bounds.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/pv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/events/events.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/events/events.go

## Purpose
This service lists Kubernetes events associated with dashboard resources by involved object UID.

## Important APIs, Types, And Functions
It defines `EventService`, `eventService`, `NewEventService`, `EventResource`, constants for Pod/PVC/PV/Job/StorageClass, and `ListEvents`.

## Control Flow
`ListEvents` calls the typed Kubernetes CoreV1 Events client for the supplied namespace and filters with field selector `involvedObject.uid=<uid>`. The resource kind is passed in `ListOptions.TypeMeta`, but the effective filter is the UID.

## State And Persistence
The service is read-only and keeps only a `k8sclient.K8sClient` pointer.

## Dependencies And Integration Points
It is used by pod and PV/PVC handlers to show event timelines. It depends on Kubernetes legacy core/v1 Events and field selectors.

## Risks
Events are namespace-scoped except PV events may be cluster-ish in presentation; callers pass empty namespace for PVs. TypeMeta in list options does not filter events, so UID uniqueness is the real selector. Clusters using events.k8s.io/v1 only through aggregation may need compatibility consideration.

## Test Signals
No tests are present. A fake-client test could verify namespace and field selector usage.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/events/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/cache_job_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/cache_job_service.go

## Purpose
`CacheJobService` provides cached, time-ordered listing for dashboard smooth-upgrade Jobs and maintains an index through controller-runtime watches.

## Important APIs, Types, And Functions
It defines `CacheJobService`, `ListAllBatchJobs`, `Reconcile`, and `SetupWithManager`, plus a package logger.

## Control Flow
`ListAllBatchJobs` parses page, order, and name filters, iterates `jobIndexes`, fetches each Job from the cache, filters with `utils.IsUpgradeJob`, and returns a paginated result. `Reconcile` fetches the Job, removes missing entries, ignores deleting objects, and indexes upgrade jobs by creation time. `SetupWithManager` watches all Job create/update/delete events; delete events remove upgrade jobs directly from the index.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[batchv1.Job]`. Kubernetes Job objects persist outside this service.

## Dependencies And Integration Points
It wraps `jobService`, shares result types from `service.go`, uses `dashboard/utils.TimeOrderedIndexes`, and is registered by `API.StartManager`.

## Risks
Create/update predicates return true for all jobs, so the reconciler sees unrelated jobs and filters later. The `descend` query only treats literal `descend` as descending, while other cached services default differently. Existing jobs before watch startup rely on manager cache/reconcile events to populate the index.

## Test Signals
No direct tests are present. Tests should cover ordering, filtering, delete removal, and query default consistency.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/cache_job_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/job_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/job_service.go

## Purpose
This is the uncached JobService implementation for listing smooth-upgrade batch Jobs directly through a controller-runtime client.

## Important APIs, Types, And Functions
It defines `jobService` and `ListAllBatchJobs`.

## Control Flow
The method parses `pageSize` with a default of 10, reads a Kubernetes continue token, and optionally handles an exact `name` lookup in the system namespace. Without a name filter, it lists Jobs in the system namespace with labels identifying JuiceFS upgrade jobs and returns the list plus Kubernetes continue token.

## State And Persistence
The service is stateless apart from its client and system namespace. It reads Kubernetes Job state but does not mutate it.

## Dependencies And Integration Points
It is selected by `NewJobService` when manager caching is disabled and is consumed by `batch.go` list endpoints.

## Risks
Name filtering is exact, not substring-based like cached mode, which creates different API behavior between modes. The returned `Total` is not populated in uncached mode. Pagination uses Kubernetes continue tokens rather than page numbers.

## Test Signals
No tests are present. Tests should verify label selectors, exact-name behavior, and empty/not-found behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/job_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/service.go

## Purpose
This file defines the JobService interface, list result DTO, and factory for cached vs uncached job services.

## Important APIs, Types, And Functions
It defines `ListJobResult`, `JobService`, and `NewJobService`.

## Control Flow
`NewJobService` creates a base `jobService` with the configured namespace. If `enableManager` is true, it wraps it in `CacheJobService` with a new time-ordered Job index; otherwise it returns the base service.

## State And Persistence
Factory-created state is either a plain client/namespace pair or an additional in-memory index. Persistent Job data remains in Kubernetes.

## Dependencies And Integration Points
It depends on Gin context signatures, batch/v1 Jobs, controller-runtime clients, `config.Namespace`, and dashboard index utilities. The factory is used by `API.NewAPI`.

## Risks
The same interface hides different pagination/filter semantics between cached and uncached implementations. Consumers must not assume `Total` is always populated.

## Test Signals
No tests are present. A small factory test could verify implementation type by `enableManager`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/cache_pod_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/cache_pod_service.go

## Purpose
`CachePodService` provides cached, enriched listing for app and system pods and maintains pod indexes for dashboard manager mode.

## Important APIs, Types, And Functions
It defines `CachePodService`, filter helpers for PV/mount pod/CSI node filters, `ListAppPods`, `ListSysPods`, `ListBatchPods`, `Reconcile`, and `SetupWithManager`.

## Control Flow
`ListAppPods` iterates app pod indexes in requested order, filters by name/namespace and app/PVC-using classification, enriches each pod with PVCs, PVs, mount pods, CSI node, and node, applies relation filters and sort fields, then paginates. `ListSysPods` does similar for system pods with node/CSI-node enrichment. `ListBatchPods` loads pods by batch config names. `Reconcile` fetches the pod, removes missing/deleting entries, classifies app vs system pods, tracks CSI node pod names by node, and indexes by creation time. Setup installs a field index on `spec.nodeName` and watches all pod events.

## State And Persistence
In-memory state includes `csiNodeIndex`, app and system `TimeOrderedIndexes`, and unused pair fields. Persistent pod state is read from Kubernetes and not mutated by this service.

## Dependencies And Integration Points
It builds on `podService` helpers, `dashboard/utils` pod classifiers and index type, controller-runtime manager/cache, and config global `CSIPod` initialization.

## Risks
`filterCSINodeOfPod` dereferences `pod.CsiNode.Name` when a filter is set and `CsiNode` is nil, risking panic after a failed CSI-node lookup. Delete handling for not-found uses an empty `pod` object to check `utils.IsCsiNode`, so CSI-node index cleanup may miss deleted pods. Enrichment calls can be expensive because each listed pod triggers additional Kubernetes reads.

## Test Signals
No direct tests are present. Tests should cover nil CSI node filtering, index updates/deletes, pagination after relation filters, and startup classification for app pods that only use JuiceFS PVCs.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/cache_pod_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/pod_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/pod_service.go

## Purpose
This file implements the uncached pod service and shared pod relationship helpers used by both cached and uncached dashboard modes.

## Important APIs, Types, And Functions
It defines `podService` and methods for listing PVCs/PVs of a pod, mount pods of app pods, CSI node pods, pod node, app/system pods, node mount pods, all mount pods, app pods of a mount pod, batch pods, and upgrade-eligible pods.

## Control Flow
PVC/PV helper methods walk pod volumes and bound PVCs. Mount-pod relation methods select mount pods by labels and node, then compare mount-pod annotation targets against app pod UIDs through `utils.GetTargetUID`. App pod listing first searches mount-mode app pods by `common.UniqueId` label and falls back to injected sidecar label. System pod listing uses pod-type label expressions. Upgrade listing selects mount pods by label, optional unique ID and node, then calls `resource.FilterPodsToUpgrade`.

## State And Persistence
The service is stateless aside from Kubernetes clients/config. It reads Kubernetes pods, PVCs, PVs, and nodes, but does not mutate them.

## Dependencies And Integration Points
It depends on controller-runtime client list/get operations, Kubernetes label and field selectors, dashboard utilities, `config.Namespace`, and `resource.FilterPodsToUpgrade`.

## Risks
Uncached app listing only falls back to sidecar pods when no mount-mode app pods are found at all, so mixed clusters may omit sidecar app pods. Several list methods return all selected Kubernetes objects without filtering to JuiceFS PVs after relation expansion. `getCSINode` requires at least one CSI node pod and returns an error otherwise.

## Test Signals
No tests are present. Useful tests would cover mixed app-pod modes, annotation UID parsing, node field selector behavior, and upgrade pod filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/pod_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/service.go

## Purpose
This file defines dashboard pod DTOs, the `PodService` interface, and the factory that chooses cached or uncached implementations.

## Important APIs, Types, And Functions
It defines `PodExtra`, `ListAppPodResult`, `ListSysPodResult`, a service-local `PodDiff`, `PodService`, and `NewPodService`.

## Control Flow
`NewPodService` builds a base `podService`. In manager mode it returns `CachePodService` with indexes and CSI-node map. Outside manager mode it tries to list a CSI node pod immediately and stores the first pod spec in `config.CSIPod`, then returns the base service.

## State And Persistence
Factory-created state is client/config handles and, in cached mode, in-memory indexes. `config.CSIPod` is process-global state initialized from observed CSI node pods. No Kubernetes mutation occurs.

## Dependencies And Integration Points
The interface is consumed by dashboard handlers in `pod.go`, `pv.go`, `cm.go`, and `batch.go`. It depends on Kubernetes API types, Gin, REST config, dashboard utilities, and `k8sclient`.

## Risks
The interface has a parameter typo `ontainer` for `ExecPod`, harmless for compilation but confusing. Cached and uncached services differ in pagination and enrichment behavior. Initialization logs and falls back silently if no CSI node pod is available in uncached mode.

## Test Signals
No direct tests are present. Tests should verify factory selection and `config.CSIPod` initialization behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/terminal.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/terminal.go

## Purpose
`terminal.go` implements websocket-backed pod log streaming, shell exec, mount access log viewing, JuiceFS debug/warmup/stats commands, and debug file download.

## Important APIs, Types, And Functions
Methods include `WatchPodLogs`, `ExecPod`, `WatchMountPodAccessLog`, `DebugPod`, `WarmupPod`, `StatsPod`, and `DownloadDebugFile`.

## Control Flow
Each websocket method upgrades the request, creates a cancellable context and terminal/log pipe, fetches the target pod when mount path resolution is needed, determines sidecar vs mount-pod mount paths, then calls `resource.ExecInPod` or Kubernetes log streaming. Warmup builds a `juicefs warmup` command from query params and adds enterprise-only retry flags for non-CE pods. Debug runs `juicefs debug` into `/debug`; stats runs `juicefs stats`; download streams the latest `/debug/*.zip` from the container.

## State And Persistence
Runtime state is websocket sessions and remote processes inside target pods. `DebugPod` creates files inside the pod at `/debug`; `DownloadDebugFile` reads those files. No local persistent state is created here.

## Dependencies And Integration Points
It depends on `resource.NewTerminalSession`, `resource.ExecInPod`, `resource.DownloadPodFile`, `utils.NewLogPipe`, `util.GetMountPathOfPod`, `util.GetMountPathOfSidecar`, `util.GetJfsInternalFileName`, and Kubernetes pod/log APIs.

## Risks
Query parameters are passed directly as command arguments; they are not shell-interpolated except access-log `cat`, but validation would still improve UX and safety. The access-log command concatenates a path into `sh -c`, relying on trusted mount paths/internal names. These operations require high Kubernetes privileges and should be protected by external authorization.

## Test Signals
No tests are present. Valuable tests would validate command construction for sidecar/non-sidecar pods, CE vs non-CE warmup flags, and error handling for missing mount paths.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/terminal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/cache_pvc_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/cache_pvc_service.go

## Purpose
`CachePVCService` provides cached, time-ordered listing and lookup helpers for JuiceFS-bound PVCs.

## Important APIs, Types, And Functions
It defines `CachePVCService`, `ListPVCs`, `ListAllPVCs`, `ListPVCsByStorageClass`, `ListPVCsBasicInfo`, `Reconcile`, and `SetupWithManager`.

## Control Flow
List methods iterate the PVC index, fetch PVCs, apply namespace/name/PV/storageclass filters, and paginate or project basic info. `Reconcile` fetches a PVC, removes missing entries, ignores deleting/unbound PVCs, fetches the bound PV, verifies it is a JuiceFS CSI PV, and adds the PVC to the time index. Setup watches PVC create events for pending/bound PVCs, update events for pending-to-bound transitions, and delete events that remove index entries.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[PersistentVolumeClaim]`. Kubernetes PVC/PV state is read-only.

## Dependencies And Integration Points
It wraps `pvcService`, uses `dashboard/utils.TimeOrderedIndexes`, controller-runtime watches, and `config.DriverName`.

## Risks
DeletionTimestamp handling returns without removing the index, relying on delete events or not-found reconcile to clean up. Update predicate ignores bound PVC updates after initial binding, so storageclass/name changes are not reindexed unless a create/delete path occurs. Cached `ListAllPVCs` ignores its `pvs` argument and returns every indexed PVC, which is fine only if the index is perfectly scoped.

## Test Signals
No direct tests are present. Tests should cover pending-to-bound indexing, deletion cleanup, and cached vs uncached `ListAllPVCs` equivalence.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/cache_pvc_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/pvc_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/pvc_service.go

## Purpose
This is the uncached PVC service for listing JuiceFS-bound PVCs and exposing PVC basic information.

## Important APIs, Types, And Functions
It defines `pvcService`, asserts it implements `PVCService`, and implements `listPVCs`, `ListPVCs`, `ListAllPVCs`, `ListPVCsByStorageClass`, and `ListPVCsBasicInfo`.

## Control Flow
`ListPVCs` first lists all JuiceFS PVs with claim refs into a PV-name map, then recursively pages PVCs until it has enough PVCs whose `Spec.VolumeName` appears in that map. `ListAllPVCs` lists all PVCs and matches them by namespace/name against claim refs from supplied JuiceFS PVs. StorageClass and basic-info methods list all PVCs and filter/project as needed.

## State And Persistence
The service is stateless and read-only.

## Dependencies And Integration Points
It depends on controller-runtime list operations, corev1 PV/PVC types, and `config.DriverName`. It is used when dashboard manager caching is disabled and by `NewPVCService`.

## Risks
`ListPVCsByStorageClass` does not restrict results to JuiceFS PVs, so selector endpoints may include non-JuiceFS PVCs for a matching storage class. Recursive paging only recurses when at least one matching PVC was found on the current page; if a page has zero matches but a continue token, later matches can be skipped. Uncached and cached list semantics differ.

## Test Signals
No direct tests are present. Tests should target paging gaps, JuiceFS filtering, and storage-class filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/pvc_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/service.go

## Purpose
This file defines PVC dashboard DTOs, the `PVCService` interface, and the cached/uncached factory.

## Important APIs, Types, And Functions
It defines `ListPVCResult`, `ListPVCWithPodResult`, `PVCWithPod`, `PVCBasicInfo`, `ListPVCBasicResult`, `PVCService`, and `NewPVCService`.

## Control Flow
`NewPVCService` creates a base `pvcService`; manager mode wraps it in `CachePVCService` with a time-ordered PVC index.

## State And Persistence
Only service object state is created. PVC data persists in Kubernetes and is not mutated by this file.

## Dependencies And Integration Points
It is consumed by PV/config/batch handlers and depends on Gin contexts, corev1 types, controller-runtime client, and dashboard index utilities.

## Risks
The interface hides cached/uncached differences in pagination and filtering. Some DTOs such as `ListPVCWithPodResult` are defined here but not used in the visible handlers, so schema drift is possible.

## Test Signals
No tests are present. Factory behavior and DTO JSON shape are straightforward candidates.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/cache_pv_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/cache_pv_service.go

## Purpose
`CachePVService` provides cached, time-ordered listing and lookup for JuiceFS PersistentVolumes.

## Important APIs, Types, And Functions
It defines `CachePVService`, `ListPVs`, `GetPVByUniqueId`, `ListAllPVs`, `Reconcile`, and `SetupWithManager`.

## Control Flow
`ListPVs` parses current/page size/order and name/PVC/SC filters, iterates the PV index, fetches PVs, filters them, and slices the page. `GetPVByUniqueId` scans indexed PVs for matching CSI volume handle. `Reconcile` fetches PVs, removes missing/deleting objects, indexes current PVs by creation time, and logs claim-ref PVC fetch failures. Setup watches JuiceFS CSI PV create and delete events; update events are ignored.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[PersistentVolume]`. Kubernetes PV state is read-only here.

## Dependencies And Integration Points
It wraps `pvService`, uses controller-runtime watches, `config.DriverName`, dashboard index utilities, and is registered by `API.StartManager`.

## Risks
Ignoring update events means claimRef, storageclass, or volume-handle changes are not reflected until delete/recreate or another reconcile. `GetPVByUniqueId` assumes every indexed PV has non-nil `Spec.CSI`, relying on watch filtering. `Reconcile` fetches the claim PVC but does not use it, so errors only log and return nil.

## Test Signals
No direct tests are present. Tests should verify create/delete indexing, update omission behavior, and filtering/pagination.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/cache_pv_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/pv_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/pv_service.go

## Purpose
This is the uncached PV service for listing all JuiceFS CSI persistent volumes and looking them up by unique ID.

## Important APIs, Types, And Functions
It defines `pvService` and implements `listPVs`, `ListPVs`, `GetPVByUniqueId`, and `ListAllPVs`.

## Control Flow
`listPVs` lists PV pages with Kubernetes limit/continue, filters to `Spec.CSI.Driver == config.DriverName`, and recursively fetches additional pages until it fills the requested count or exhausts the continue token. `ListPVs` parses page size and continue token. `GetPVByUniqueId` scans all PVs for CSI volume handle equality. `ListAllPVs` lists all PVs and filters to JuiceFS.

## State And Persistence
The service is stateless and read-only.

## Dependencies And Integration Points
It depends on controller-runtime client, Gin query parameters, corev1 PVs, and `config.DriverName`.

## Risks
Like the PVC service, recursive paging only continues when the current page has at least one matching PV; pages with zero JuiceFS PVs and a continue token can stop the scan early. `GetPVByUniqueId` returns an empty PV object instead of nil when not found, which callers must handle carefully.

## Test Signals
No direct tests are present. Tests should cover paging with nonmatching pages and not-found return shape.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/pv_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/service.go

## Purpose
This file defines PV dashboard DTOs, the `PVService` interface, and the factory for cached vs uncached implementations.

## Important APIs, Types, And Functions
It defines `ListPVPodResult`, `PVService`, and `NewPVService`.

## Control Flow
`NewPVService` creates a base `pvService`; when manager mode is enabled, it wraps it in `CachePVService` with a time-ordered PV index.

## State And Persistence
Factory state is either a plain client service or an indexed cached service. No Kubernetes resources are mutated.

## Dependencies And Integration Points
It is used by `API.NewAPI`, `pv.go`, `pod.go`, and `batch.go`. It depends on corev1 PV types, Gin, controller-runtime client, and dashboard index utilities.

## Risks
The result type includes both `Total` and Kubernetes `Continue`, but cached and uncached modes populate different fields. Consumers should treat these as mode-dependent.

## Test Signals
No tests are present. Factory and JSON result behavior are low-cost test targets.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/cache_secret_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/cache_secret_service.go

## Purpose
`CacheSecretService` maintains a cached index of JuiceFS-related Secrets for dashboard diff generation.

## Important APIs, Types, And Functions
It defines `CacheSecretService`, `ListAllSecrets`, `Reconcile`, and `SetupWithManager`.

## Control Flow
`ListAllSecrets` iterates the secret index and fetches each secret. `Reconcile` fetches a secret, removes missing entries, ignores deleting objects, and indexes secrets that are either CSI-generated JuiceFS secrets or custom secrets containing token/metaurl fields. Setup watches all secret create/update/delete events and removes relevant secrets from the index on delete.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[Secret]`. Secret data persists in Kubernetes and is only read by this service.

## Dependencies And Integration Points
It wraps `secretService`, uses dashboard secret classifiers in `utils/index.go`, controller-runtime manager watches, and feeds `batch.go` diff generation.

## Risks
Create/update predicates enqueue every Secret, which may be noisy in large clusters. A secret that stops matching JuiceFS criteria on update is not explicitly removed unless not-found/delete occurs, because `Reconcile` only adds matching secrets and otherwise leaves prior index entries.

## Test Signals
No direct tests are present. Tests should cover add/delete and update-from-matching-to-nonmatching behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/cache_secret_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/secret_service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/secret_service.go

## Purpose
This is the uncached secret service for listing JuiceFS-related Kubernetes Secrets.

## Important APIs, Types, And Functions
It defines `secretService` and `ListAllSecrets`.

## Control Flow
`ListAllSecrets` lists all Secrets visible to the client, filters to generated JuiceFS secrets or custom JuiceFS credential secrets using dashboard utility predicates, and returns the filtered slice.

## State And Persistence
The service is stateless and read-only.

## Dependencies And Integration Points
It depends on controller-runtime client, corev1 Secrets, and `utils.IsJuiceSecret`/`IsJuiceCustSecret`. It feeds diff generation in `batch.go`.

## Risks
Listing all secrets can be expensive and may require broad RBAC. The local variable `seccretList` is misspelled but harmless. Filtering by `token`/`metaurl` fields can include user secrets not intended for dashboard diffing if RBAC permits them.

## Test Signals
No tests are present. Tests should verify both generated-label and custom-secret filters.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/secret_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/service.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/service.go

## Purpose
This file defines the `SecretService` interface and cached/uncached factory.

## Important APIs, Types, And Functions
It defines `SecretService` and `NewSecretService`.

## Control Flow
`NewSecretService` creates a base `secretService`; manager mode wraps it in `CacheSecretService` with a time-ordered secret index.

## State And Persistence
Factory state is a client pointer and optional in-memory index. Kubernetes Secrets are not mutated here.

## Dependencies And Integration Points
It is used by `API.NewAPI` and diff generation through the interface. It depends on controller-runtime client, corev1 Secret types, and dashboard index utilities.

## Risks
As with other services, cached and uncached behavior can differ if the index is stale or incomplete.

## Test Signals
No tests are present. Factory selection is the primary unit-level signal.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/secrets/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils.go

## Purpose
This package-level utility file provides sorting adapters, mount-pod label selectors, job owner references, secret-name parsing, PVC selector checks, YAML/debug file writing, zipping, and safe-ish path component normalization for dashboard handlers.

## Important APIs, Types, And Functions
It defines `ReverseSort`, `Reverse`, `LabelSelectorOfMount`, `isShareMount`, `SetJobAsConfigMapOwner`, `getUniqueIdFromSecretName`, `IsPVCSelectorEmpty`, `DownloadYaml`, `ZipDir`, and `StripDir`.

## Control Flow
Sorting wraps another `sort.Interface` with inverted `Less`. Mount selectors match `common.PodUniqueIdLabelKey` against PV volume handle and optionally storage class. Download helpers restrict target paths to `/tmp`, marshal YAML, and write through buffered IO. `ZipDir` walks a source directory and writes a deflated zip to a `/tmp` target. `StripDir` replaces path separators and `..` with dashes.

## State And Persistence
`DownloadYaml` and `ZipDir` write local files under `/tmp`; other helpers are stateless. `SetJobAsConfigMapOwner` mutates the provided ConfigMap object in memory before the caller updates Kubernetes.

## Dependencies And Integration Points
Used by PV/pod/batch handlers for sorting, relationship lookup, debug bundle generation, and upgrade ConfigMap ownership. It depends on Kubernetes core/batch/meta types and `sigs.k8s.io/yaml`.

## Risks
The `/tmp` prefix check uses string prefix rather than cleaned path boundary, so paths like `/tmpx` would pass even though they are outside `/tmp` semantically. `isShareMount` assumes at least one container. `ZipDir` can include the root directory entry as `./` and follows `filepath.Walk` behavior without symlink-specific controls.

## Test Signals
`utils_test.go` covers reverse sorting, empty PVC selector detection for an empty struct, and `StripDir` replacement behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index.go

## Purpose
This subpackage file provides a generic creation-time ordered index for cached dashboard services and predicates for JuiceFS secrets and upgrade jobs.

## Important APIs, Types, And Functions
It defines `k8sResource`, `TimeOrderedIndexes[T]`, `NewTimeIndexes`, `Iterate`, `Length`, `AddIndex`, `RemoveIndex`, `Debug`, `IsJuiceCustSecret`, `IsJuiceSecret`, and `IsUpgradeJob`.

## Control Flow
`AddIndex` locks the list, computes a namespaced name, scans backward through existing entries, removes stale entries whose resources can no longer be fetched, deduplicates by UID, inserts after the first older resource when the new resource is newer, or pushes to the front. `Iterate` returns a channel produced by a goroutine that holds an RLock while walking front-to-back or back-to-front until context cancellation.

## State And Persistence
State is an in-memory doubly linked list protected by an RWMutex. It stores namespaced names, not resource objects, and revalidates objects through caller-provided getters.

## Dependencies And Integration Points
The index is used by cached pod, PV, PVC, Job, and Secret services. Predicate helpers encode dashboard-specific resource classification using JuiceFS labels and secret data.

## Risks
`Iterate` sends on an unbuffered channel while holding an RLock; if a consumer stops early without canceling context, the goroutine can block and hold the lock. `AddIndex` deduplicates by UID, so a deleted/recreated resource with same namespace/name and different UID can leave both until stale cleanup observes the old object as missing. Secret custom detection treats either token or metaurl data as enough.

## Test Signals
`index_test.go` verifies ordered insertion, duplicate suppression, and stale-entry removal when re-adding a resource.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index_test.go

## Purpose
This test file validates insertion, ordering, duplicate suppression, and stale-entry cleanup for `TimeOrderedIndexes`.

## Important APIs, Types, And Functions
It defines `TestIndexAdd` and `TestIndexAddNoDuplicateWhenStaleEntryRemoved`, using corev1 Pod fixtures and simple metadata/resource getter callbacks.

## Control Flow
`TestIndexAdd` adds newer and older pods, asserts chronological order, then re-adds the same pod twice and verifies length/order are unchanged. `TestIndexAddNoDuplicateWhenStaleEntryRemoved` creates an index with two pods, changes the getter so one existing entry returns nil, re-adds the remaining pod, and asserts the stale entry is removed without duplicating the live pod.

## State And Persistence
State is an in-memory index and local pod fixtures. No external state is used.

## Dependencies And Integration Points
The tests cover the utility used by all cached dashboard services. They depend on Kubernetes metadata types and Go reflection equality.

## Risks
The tests do not cover `Iterate` cancellation, reverse iteration, `RemoveIndex`, or recreated same-name/different-UID behavior. They also do not exercise concurrent access.

## Test Signals
Passing tests give focused confidence that cached service indexes remain creation-time ordered and can clean stale entries during add operations.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/utils.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/utils.go

## Purpose
This dashboard utility subpackage contains pod classifiers, mount label selectors, PVC/target ID helpers, websocket log piping, and app-pod desensitization.

## Important APIs, Types, And Functions
Key functions are `IsAppPod`, `IsMountPod`, `IsSysPod`, `IsCsiNode`, `IsAppPodShouldList`, `LabelSelectorOfMount`, `GetUniqueOfPVC`, `GetTargetUID`, `NewLogPipe`, `LogPipe.Write`, `LogPipe.Read`, `DesensitizeAppPod`, and `desensitizeContainer`.

## Control Flow
Classifiers inspect labels for JuiceFS app, mount, system, and CSI-node pods. `IsAppPodShouldList` follows pod PVC volumes to PVCs/PVs and admits pods using JuiceFS CSI PVs or unbound PVCs. `GetTargetUID` parses kubelet CSI mount paths from annotation values. `NewLogPipe` starts a goroutine that reads websocket messages, closes the stream on disconnect, and responds to ping with pong. Desensitization copies selected pod metadata/status/spec fields and strips non-mount containers down to operational fields.

## State And Persistence
All helpers are stateless except `LogPipe`, which owns a websocket connection and stream for the lifetime of a request. No persistent state is written.

## Dependencies And Integration Points
These helpers are used across pod/PV handlers and cached services. They depend on Kubernetes core/meta/label types, controller-runtime client, `common` labels, and util helpers.

## Risks
`IsAppPodShouldList` returns false on the first PVC/PV get error, which can hide otherwise valid app pods. `LabelSelectorOfMount` duplicates package-level dashboard logic and can drift. Desensitization copies ObjectMeta wholesale, so labels/annotations remain visible even while container details are reduced.

## Test Signals
No tests are in this file directly. Related tests cover the package-level selector/sort utilities, not these subpackage classifiers or websocket behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils_test.go

## Purpose
This test file covers selected package-level dashboard utility behavior: reverse sorting, PVC selector emptiness, and directory string normalization.

## Important APIs, Types, And Functions
It defines `TestReverse`, `TestIsPVCSelectorEmpty`, and `TestStripDir`.

## Control Flow
`TestReverse` builds a `ListSCResult` with three storage classes and sorts it through `Reverse`, then asserts descending creation timestamps. `TestIsPVCSelectorEmpty` checks that an empty `config.PVCSelector` is treated as empty. `TestStripDir` verifies backslash, slash, and `..` replacement with dashes.

## State And Persistence
Tests use local in-memory fixtures only.

## Dependencies And Integration Points
The tests exercise helpers used by `pv.go`, `batch.go`, and debug bundle path construction. They depend on StorageClass metadata and config selector structs.

## Risks
Coverage is narrow: nil selector behavior, populated selector fields, safe `/tmp` path enforcement, zip creation, and owner-reference helpers are not tested.

## Test Signals
Passing tests indicate basic sort inversion and path component normalization still behave as expected.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/controller.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/controller.go

## Purpose
This file implements the CSI Controller service for JuiceFS: volume creation/deletion, capability validation, snapshots, and controller-side quota expansion.

## Important APIs, Types, And Functions
It defines supported `volumeCaps` and `controllerCaps`, `controllerService`, `newControllerService`, `setQuotaInController`, `CreateVolume`, `DeleteVolume`, `ControllerGetCapabilities`, `GetCapacity`, `ListVolumes`, `ValidateVolumeCapabilities`, `isValidVolumeCapabilities`, `CreateSnapshot`, `DeleteSnapshot`, `ListSnapshots`, `ControllerExpandVolume`, and unimplemented publish/get/modify methods.

## Control Flow
`CreateVolume` validates name/capabilities, rejects unsupported block/readonly dynamic modes, parses snapshot restore source when present, records requested capacity in an in-memory map, copies parameters into volume context, optionally starts asynchronous controller quota setting through a dispatch pool, and returns CSI volume context with `subPath` and `capacity`. Snapshot restore is invoked before quota setup when requested. `DeleteVolume` validates volume ID, ignores non-dynamic PVs or empty secrets, serializes deletes with `VolumeLocks`, calls `JfsDeleteVol`, and removes the in-memory volume record. `ValidateVolumeCapabilities` checks the in-memory volume map and confirms supported capabilities. Snapshot methods call JuiceFS create/delete snapshot operations and encode/decode snapshot handles. `ControllerExpandVolume` validates quota config and capacity range, resolves subpath, and calls `setQuotaInController`.

## State And Persistence
Process-local state includes `vols` capacity map, `volLocks`, and a quota worker pool. Persistent effects occur in the JuiceFS backend: creating/restoring/deleting subdirectories, setting quotas, and creating/deleting snapshots. CSI response volume context persists in Kubernetes PV metadata through the external provisioner.

## Dependencies And Integration Points
It depends on CSI protobuf APIs, gRPC status codes, JuiceFS provider interface, `k8sclient`, global config, utility functions for dynamic PV/snapshot/subdir parsing, resource volume locks, and dispatch pools. It is exposed through the driver server as the CSI Controller service.

## Risks
The `vols` map is process-local, so `ValidateVolumeCapabilities` can return NotFound after controller restart even for existing volumes. Controller quota setting in `CreateVolume` runs asynchronously and logs errors without failing volume creation. `CreateVolume` records capacity before later errors and does not always roll back the map on failure. Snapshot and restore operations rely on secrets and backend behavior without PV context loading. Several CSI capabilities are advertised while list/get/publish methods remain unimplemented, though advertised caps exclude those unimplemented paths.

## Test Signals
This subset does not include `controller_test.go`, but that file exists nearby. Key tests should cover capability validation, readonly rejection, async quota flagging, dynamic PV delete checks, process-local map behavior, snapshot handle parsing, and expansion quota calls.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/controller.go -->
