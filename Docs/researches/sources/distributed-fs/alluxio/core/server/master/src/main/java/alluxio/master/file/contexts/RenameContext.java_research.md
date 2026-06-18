# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/RenameContext.java

Purpose: wraps `RenamePOptions` for master rename operations and records internal operation time plus whether persistence should follow the rename.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts. `getOperationTimeMs`, `setOperationTimeMs`, `getPersist`, and `getOperationId` expose rename-specific state.

Control flow: construction captures current time and `optionsBuilder.getPersist()`. `mergeFrom` merges caller options over `FileSystemOptionsUtils.renameDefaults(Configuration.global(), false)`. Downstream rename code uses operation time for inode modification timestamps and `getPersist` to determine follow-up persistence behavior.

State and persistence behavior: transient context state influences journaled rename metadata. Operation time can become last modification time, and `mPersist` controls whether renamed content should be persisted to UFS after namespace mutation.

Dependencies and integration points: depends on rename protobufs, configuration defaults, and `OperationId`. It integrates with `DefaultFileSystemMaster` rename internals and operation-id tracking.

Risks: `mPersist` is captured at construction and will not reflect later direct mutations to the options builder. Tests should catch this if builders are mutated after context creation.

Test signals: default merging, persist flag capture, operation-time override, operation-id extraction, and rename timestamp behavior are the important signals.
