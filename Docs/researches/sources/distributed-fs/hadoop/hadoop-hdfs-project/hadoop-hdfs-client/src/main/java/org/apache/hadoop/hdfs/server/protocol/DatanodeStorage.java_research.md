# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorage.java

Purpose: `DatanodeStorage` describes a single storage volume/resource on a DataNode, including stable storage ID, state, and HDFS `StorageType`.

Important APIs/types/functions: `State` values are `NORMAL`, `READ_ONLY_SHARED`, and `FAILED`. Constructors default to normal/default storage or accept all fields. `generateUuid()` creates `DS-<uuid>` IDs. `isValidStorageId()` validates that format. Equality and hash code are based only on `storageID`.

Control flow: DataNodes construct storage records for reports; NameNode-side code compares and indexes them by storage ID.

State and persistence behavior: immutable final fields. Storage IDs are expected to persist across DataNode restarts in higher-level storage metadata, though this class only carries the value.

Dependencies and integration points: depends on `StorageType` and Java `UUID`. Used by `StorageReport`, block placement, storage policy, and DataNode storage registration/reporting.

Risks and test signals: equality ignores state and type, so two records with the same ID but different state/type compare equal. `equals` assumes non-null storage IDs. Tests should cover UUID generation/validation, equality semantics, and read-only-shared behavior in consumers.
