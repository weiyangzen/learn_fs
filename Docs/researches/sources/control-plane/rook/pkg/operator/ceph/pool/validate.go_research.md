# sources/control-plane/rook/pkg/operator/ceph/pool/validate.go

Purpose: validates `CephBlockPool` and `PoolSpec` objects before reconcile applies Ceph-side pool configuration.

Important APIs/types/functions: `validatePool`, exported `ValidatePoolSpec`, `validateDeviceClasses`, and `validateDeviceClassOSDs`.

Control flow: `validatePool` checks name/namespace, delegates base CR validation to `cephv1.ValidateCephBlockPool`, then validates the embedded pool spec. `ValidatePoolSpec` validates hybrid storage device classes, rejects simultaneous replicated and erasure-coded settings, rejects identical failure/subfailure domains, enforces stretch-cluster restrictions, lazily reads the CRUSH map when failure domain or CRUSH root is specified, validates requested failure domain/root/subdomain names, validates replica size and `ReplicasPerFailureDomain`, validates compression mode in `Parameters`, and validates mirroring mode and snapshot schedule combinations. Snapshot schedules without mirroring only warn.

State and persistence behavior: no persistent writes. It reads Ceph cluster state for CRUSH map and device-class OSD membership when specs require live validation. It logs deprecated compression mode and snapshot schedule warnings.

Dependencies/integration: depends on Ceph API spec helpers like `IsReplicated`, `IsErasureCoded`, `IsHybridStoragePool`, and `SnapshotSchedulesEnabled`, plus `cephclient.GetCrushMap` and `cephclient.GetDeviceClassOSDs`.

Risks: validation can fail due to temporary Ceph command errors, not only invalid specs. The error string for allowed mirroring modes says image and pool even though code also accepts `init-only`. Deprecated `CompressionMode` is only warned, while `Parameters["compression_mode"]` is enforced. Stretch-cluster rules are hard-coded to replicated size 4 and no erasure coding.

Test signals: `validate_test.go` covers missing fields, invalid replication/EC combinations, replica safety, compression modes, replica-per-failure-domain constraints, CRUSH domain/root lookup, mirroring modes/schedules, subfailure domain conflicts, and hybrid storage device-class OSD presence.
