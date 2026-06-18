# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/FreeContext.java

Purpose: wraps `FreePOptions` for master free operations, which evict file blocks from Alluxio storage without necessarily deleting namespace metadata.

Important APIs and types: `create`, `mergeFrom`, and `defaults` follow the common context pattern. `mergeFrom` uses `FileSystemOptionsUtils.freeDefaults(Configuration.global())`, and `toString` records the built protobuf options.

Control flow: the master free RPC can construct this context from user options and pass it to internal free logic. No extra state is introduced beyond the protobuf builder and base cancellation trackers.

State and persistence behavior: the context itself is transient. Its protobuf options govern recursive behavior, forced operation semantics, and any fields defined in `FreePOptions`; actual persistence effects occur in file-master block metadata updates and worker commands outside this wrapper.

Dependencies and integration points: depends on gRPC free options, global configuration defaults, and `OperationContext`. It integrates with file-master free paths and can carry call cancellation tracking.

Risks: this class is intentionally thin, so any future free-specific internal flag must be added deliberately. Mutable builder sharing remains a general risk.

Test signals: coverage should focus on default option merging and master free behavior under recursive or forced options rather than isolated wrapper logic.
