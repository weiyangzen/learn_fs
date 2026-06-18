# sources/cloud-native/containerd/core/mount/manager/buckets.go

Purpose: documents the bbolt schema for the mount manager package and defines shared bucket/key constants used by manager persistence code.

Important APIs and data: package-level bucket keys for IDs, mounts, leases, active/system mounts, type/source/target/options, mounted time, mountpoint, labels, and GC back-reference labels.

Control flow: no functions. The schema comment describes `v1/<namespace>/mounts/<mount name>` records, active/system ordered subbuckets, leases, and an unused unmount queue.

State and persistence: this file is the authoritative local schema map for mount manager bbolt persistence. It records fields such as created/updated time, lease, active mount order, mount type/source/target/options, active mountpoint, and labels.

Dependencies and integration: used by other files in `core/mount/manager` to read/write metadata and by GC-related code through back-reference label constants.

Risks: schema comments and byte constants must stay synchronized with actual manager implementation. Unused or legacy fields in the schema can confuse migration and cleanup work.

Test signals: no direct tests in subset.
