<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/volume_lock.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/volume_lock.go

Purpose: Implements in-memory per-volume operation locking so duplicate CSI operations on the same logical key can return `Aborted` instead of racing.

Important APIs/types/functions: `volumeLocks` wraps a `sets.String` and `sync.Mutex`. `newVolumeLocks` initializes the set. `TryAcquire` atomically checks/inserts a volume ID key and returns false when already present. `Release` removes the key. `volumeOperationAlreadyExistsFmt` standardizes the node/controller error text.

Control flow: Callers acquire before a critical operation and defer release. In this subset, node staging/unstaging uses a key composed of `volumeID-targetPath`.

State and persistence behavior: State is process-local only and lost on driver restart. It protects concurrency inside one driver process but not across replicas or restarts.

Dependencies and integration points: Depends on Kubernetes `sets.String`. Integrated by node server paths and likely controller paths elsewhere in the package.

Risks: Locks require callers to consistently use the same key scheme. Because state is in-memory, operations interrupted by process exit do not leave stale locks, but concurrent operations in different pods/processes are not coordinated.

Test signals: `nodeserver_test.go` exercises lock rejection for staging and unstaging by pre-acquiring the expected key.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/volume_lock.go -->
