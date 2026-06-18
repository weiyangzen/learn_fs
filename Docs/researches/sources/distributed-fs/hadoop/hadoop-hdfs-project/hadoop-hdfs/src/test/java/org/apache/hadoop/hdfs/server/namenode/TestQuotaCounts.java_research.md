# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaCounts.java

Purpose: Unit-tests the `QuotaCounts` value container used by NameNode quota logic for namespace, storage-space, and per-`StorageType` counters. It focuses on arithmetic and the special constant counter instances used for reset/default values.

Important APIs and functions: Tests construct counters with `new QuotaCounts.Builder()`, `nameSpace`, `storageSpace`, and `typeSpaces`, then exercise `addNameSpace`, `addStorageSpace`, `add`, `addTypeSpace`, `subtract`, `setTypeSpaces`, `setNameSpace`, `setStorageSpace`, and `negation`. Assertions inspect `getNameSpace`, `getStorageSpace`, `getTypeSpace`, and internal references `nsSsCounts` and `tsCounts`.

Control flow: The suite creates fresh counters, mutates them with positive and negative deltas, copies type counters from another instance, resets counters to constants, and verifies every `StorageType` value. The reset test validates that builder/setter paths reuse `QuotaCounts.QUOTA_RESET` and `QuotaCounts.STORAGE_TYPE_RESET`/`STORAGE_TYPE_DEFAULT` rather than allocating mutable counters for constant states.

State and persistence behavior: No persistent filesystem state exists. The tested state is in-memory `QuotaCounts` internals, including reference identity for immutable constant counters and mutable enum counter values after arithmetic.

Dependencies and integration points: Depends on `StorageType` enumeration and `HdfsConstants.QUOTA_RESET`. These counters are consumed by inode quota features, content summary, quota checks, and fsimage/edit-log serialization elsewhere.

Risks: Incorrect constant reuse can introduce accidental mutation of shared reset/default counters. Arithmetic sign errors affect quota rollback, snapshot accounting, and over-quota decisions. The tests do not cover overflow boundaries.

Test signals: Passing signals are exact namespace/storage-space values, exact per-storage-type values after add/subtract/negation, and `assertSame` identity checks for constant counter fast paths.
