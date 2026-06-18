## sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi_util.go

Purpose: performs the actual iSCSI attach/mount and unmount/disconnect workflow for node publish/unpublish.

`AttachDisk` validates connector presence, calls `Connect`, checks target mountpoint, creates the target directory, persists connector config to `/var/run/iscsi.csi.k8s.io/iscsi-<volumeID>.json`, builds ro/rw plus requested mount options, and calls `FormatAndMount`. `DetachDisk` resolves mount use count, skips when target path does not exist, reloads connector config, unmounts, disconnects only when count reaches zero, removes target path, and deletes the connector file.

State and persistence are host mount table, iSCSI sessions/devices, target directories, and connector JSON files. Dependencies are iscsilib, Kubernetes mount package, OS filesystem, gRPC status, and klog. Risks include persisted connector file remaining when mount fails after persistence, missing cleanup when connector file is absent, unmount-before-disconnect order assumptions, returning nil when device still in use, and sensitive connection data stored under `/var/run`. Test signal is runtime/sanity; no focused unit tests here.
