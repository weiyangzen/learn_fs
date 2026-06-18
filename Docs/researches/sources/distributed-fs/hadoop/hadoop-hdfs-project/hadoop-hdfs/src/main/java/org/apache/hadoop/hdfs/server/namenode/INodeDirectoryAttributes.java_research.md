# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectoryAttributes.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeDirectoryAttributes.java

Purpose: `INodeDirectoryAttributes` extends `INodeAttributes` with directory-specific quota metadata and comparison support. It provides snapshot-copy implementations for normal directories and quota-bearing directories.

Important APIs and types: interface methods are `getQuotaCounts` and `metadataEquals`. `SnapshotCopy` extends `INodeAttributes.SnapshotCopy`, always reports `isDirectory()`, returns reset quota counts of `-1` for namespace/storage/type quotas, and compares quota, permission long, ACL feature identity, and XAttr feature identity. `CopyWithQuota` extends `SnapshotCopy` and stores a `QuotaCounts` copy for namespace, storage-space, and storage-type quotas.

Control flow: normal snapshot copies capture directory metadata but report no quotas. `CopyWithQuota` constructors either build quota counts from explicit values and type quotas or copy them from a live quota-set `INodeDirectory` after a precondition check. `getQuotaCounts` returns a defensive `QuotaCounts` copy rather than the stored object.

State and persistence behavior: instances are snapshot/history attribute copies, not live mutable directories. Quota counts mirror persistent directory quota metadata captured at snapshot time. ACL features are de-duplicated by the superclass constructor; XAttr references are captured as supplied.

Dependencies and integration points: it integrates with directory snapshot diffs, `INodeDirectory`, `QuotaCounts`, `StorageType` counters, ACL/XAttr metadata, and permission status packing. `INodeDirectory.metadataEquals` mirrors the comparison logic for live directories.

Risks: metadata equality compares ACL and XAttr feature object identity, not deep content, relying on feature sharing/de-duplication invariants. Normal `SnapshotCopy` uses reset quotas, so callers needing quota history must choose `CopyWithQuota`. Stored quota is mutable internally but returned by copy, reducing external mutation risk.

Test signals: tests should cover snapshot copy from live directory, explicit quota copy, defensive quota returns, `metadataEquals` with equal/different quota/permission/features, precondition failure for non-quota directories, and `isDirectory` behavior.
