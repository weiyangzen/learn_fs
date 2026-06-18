# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ScheduleAsyncPersistenceContext.java

Purpose: wraps `ScheduleAsyncPersistencePOptions` for scheduling asynchronous persistence of an Alluxio file to UFS.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts. `getPersistenceWaitTime` exposes the wait time captured from the options builder.

Control flow: construction copies `optionsBuilder.getPersistenceWaitTime()` into `mPersistenceWaitTime`. `mergeFrom` merges request options over `FileSystemOptionsUtils.scheduleAsyncPersistenceDefaults`.

State and persistence behavior: the context itself is transient, but the wait time influences when persistence jobs should run. Actual persisted state changes occur in file metadata and persistence job tracking outside this wrapper.

Dependencies and integration points: depends on schedule-async-persistence protobufs, configuration defaults, and `OperationContext`. It integrates with file-master persistence scheduling.

Risks: like `RenameContext`, the derived wait time is captured at construction and can diverge if the builder is mutated later. The defaults comment references `LoadMetadataContext`, which is harmless but misleading documentation.

Test signals: tests should cover default merging, wait-time capture, scheduling behavior for non-default wait times, and no accidental divergence after builder mutation.
