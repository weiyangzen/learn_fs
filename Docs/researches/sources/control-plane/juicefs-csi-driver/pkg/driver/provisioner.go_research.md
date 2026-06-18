# sources/control-plane/juicefs-csi-driver/pkg/driver/provisioner.go

Purpose: implements the external dynamic provisioner side of the CSI driver, translating PVC/StorageClass options into PVs and managing delete/restore/quota side effects.

Important APIs and types: `provisionerService` owns the JuiceFS provider, Kubernetes client, leader-election settings, snapshot client, provision metrics, quota pool, and volume locks. `newProvisionerService` creates the provider, snapshot client when REST config exists, metrics, and locks. `Run` starts `sig-storage-lib-external-provisioner` with driver name, leader election, lease duration, namespace, and configured worker threadiness. `Provision`, `RestoreDataSource`, and `Delete` implement the provisioner interface.

Control flow: `Provision` rejects PVC selectors, resolves StorageClass parameters and mount options through `resource.ObjectMeta`, chooses `subPath` from `pathPattern` or PV name, rejects read-only dynamic volumes without a path pattern, builds CSI PV attributes and secret refs, optionally adds secret finalizers, optionally enqueues controller-side quota setting, and triggers snapshot restore when `PVC.Spec.DataSource` references a ready `VolumeSnapshot`. `RestoreDataSource` validates snapshot/content binding, parses snapshot handles, resolves secrets, and calls `juicefs.RestoreSnapshot`. `Delete` honors reclaim policy, uses volume locks, checks whether other PVs share the same subpath, loads publish secrets, calls `JfsDeleteVol`, and removes secret finalizers when safe.

State and persistence behavior: persists Kubernetes PV specs, secret finalizers, background quota work, snapshot restore jobs through JuiceFS, and deletion side effects in the filesystem/backend. It also uses process-local Prometheus counters, dispatch pools, and locks.

Dependencies and integration points: integrates Kubernetes core APIs, external provisioner library, CSI snapshot clientset, JuiceFS provider, global config, resource helpers for object metadata/subpath/finalizer checks, quota feature detection, and StorageClass/PVC conventions.

Risks and test signals: quota setting is asynchronous, so provisioning can succeed even if quota later fails. If snapshot client creation fails, restore requests return a PV as finished without restoring data, which is logged but may surprise callers. The file is not directly covered by a dedicated listed test file; behavior is partially exercised indirectly through driver construction and controller/juicefs mocks.
