# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultStorageTier.java

Purpose: Concrete storage-tier container for configured storage directories, tier capacity aggregation, and lost-storage tracking.

Important APIs: `newStorageTier`, `initStorageTier`, `checkEnoughMemSpace`, getters for ordinal, alias, capacity, available bytes, directories, lost storage, and `removeStorageDir`.

Control flow: Initialization reads configured paths, quotas, and medium types, expands worker data directories, applies reserved bytes when multi-tier alignment is enabled, creates each `DefaultStorageDir`, records failures as lost storage, deletes temp directories, and validates single memory-tier tmpfs capacity on Linux.

State and persistence: Holds directory map and lost-storage path list in memory. It initializes and cleans real filesystem storage directories.

Dependencies and integration: Uses Alluxio configuration templates, storage tier association, path/file utilities, shell mount inspection, and OS utilities. Created by metadata manager during worker startup.

Risks and test signals: Misconfigured quota/medium lists reuse last configured value for extra paths. Initialization can delete temp directories and invalid storage contents. Tests should cover multi-dir config, initialization failure recording, reserved-byte injection, tmpfs size validation, and remove-storage-dir behavior.
