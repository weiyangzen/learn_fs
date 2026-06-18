# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/config.go

Purpose: defines manager daemon keyring generation and dashboard port selection helpers used by the mgr cluster orchestrator.

Important APIs and types: constants include `minPortWithoutPrivileges` and the `keyringTemplate` for `mgr.<id>` caps. `mgrConfig` holds Kubernetes resource name, Ceph daemon ID, and data path map. `dashboardInternalPort`, `dashboardPublicPort`, and `dashboardDefaultPort` map CR dashboard settings to service/container ports. `generateKeyring` creates or rotates mgr CephX keys and stores the keyring Secret.

Control flow: dashboard public port defaults to HTTP or HTTPS default when unset; internal port falls back to the default if the public port is `<=1024` so the pod does not bind a privileged port. `generateKeyring` gets the keyring secret store, generates `mgr.<daemonID>` with mon/mds/osd caps, optionally rotates it if `Cluster.shouldRotateCephxKeys` is true, deletes legacy per-mgr secret names from older Rook versions, formats the keyring, and persists it through the secret store.

State and persistence behavior: writes or updates keyring Secrets and returns the secret resource version for deployment annotations. It may delete legacy Kubernetes Secrets named like the mgr resource. It does not update CephCluster status itself; `mgr.go` updates status after iterating mgrs.

Dependencies and integration points: uses `config/keyring` secret store, `config.DataPathMap`, Kubernetes CoreV1 Secrets, API error helpers, and mgr cluster state. It is called from `Cluster.Start` before deployment creation so the deployment template can include the key identifier annotation.

Risks: key rotation and deployment rollout are coupled through the returned resource version; failure to propagate it could leave pods using stale keys. Deleting legacy secrets is best-effort and logged on non-not-found errors. Port mapping must stay consistent with service creation in `spec.go` and dashboard tests.

Test signals: no direct tests in this file, but `dashboard_test.go` validates low/default dashboard port behavior through service generation, and mgr key rotation is indirectly covered through mgr start paths elsewhere.
