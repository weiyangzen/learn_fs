# sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus.go

Purpose: periodically checks Ceph cluster health, updates `CephCluster.status`, manages selected Ceph health settings, records cluster version, and force-deletes stuck Rook pods on NotReady nodes during unhealthy states.

Important APIs/types/functions: `cephStatusChecker` stores Rook context, cluster info, interval, controller client, and external flag. `newCephStatusChecker()` constructs it with env/CR interval overrides. `checkCephStatus()` runs the monitoring loop. `checkStatus()` calls Ceph status and status update logic. `configureHealthSettings()` handles insecure global ID warnings. `updateCephStatus()` writes status and daemon versions. `toCustomResourceStatus()` converts Ceph CLI status into CR status. `updateClusterCephVersion()`, `cephStatusOnError()`, `forceDeleteStuckRookPodsOnNotReadyNodes()`, and `getRookPodsOnNode()` support auxiliary behavior.

Control flow: the checker immediately checks status, then loops until its internal context is canceled or monitoring map entry is removed. On Ceph command errors, it writes `HEALTH_ERR` with the error message unless the operator is still initializing. On non-OK health, it attempts stuck pod cleanup. Status conversion updates health, details, timestamps, capacity, previous health, and FSID. Version update is performed separately by the cluster controller.

State and persistence behavior: persistent state is `CephCluster.status.cephStatus` and `status.cephVersion`. Capacity is preserved when Ceph reports zero total bytes and prior capacity exists. `LastChanged` and `PreviousHealth` track health transitions. Force deletion mutates Kubernetes Pod state only for matching Rook pods that are stuck on NotReady nodes.

Dependencies and integration points: integrates with Ceph client command helpers (`StatusWithUser`, `GetAllCephDaemonVersions`), Rook status reporting, Kubernetes clients, cluster health routine tracking, version labeling, and k8sutil node/pod helpers.

Risks: periodic loop uses `time.After()` each iteration, which is simple but not externally jittered. `configureHealthSettings()` calls `config.DisableInsecureGlobalID()` based on health checks and ignores its return, so failure is not surfaced. Force-deleting pods during non-OK health is powerful and depends on label matching. `toCustomResourceStatus()` timestamps use current UTC time, making tests time-sensitive.

Test signals: `cephstatus_test.go` covers status conversion, checker interval construction, insecure global ID behavior, stuck pod force deletion, and Rook pod label filtering.
