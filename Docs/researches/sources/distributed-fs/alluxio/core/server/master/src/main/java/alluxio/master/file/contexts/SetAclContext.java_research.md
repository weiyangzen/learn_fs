# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SetAclContext.java

Purpose: wraps `SetAclPOptions` for ACL mutation requests in the file master.

Important APIs and types: `create`, `mergeFrom`, and `defaults` follow the standard operation-context pattern. No extra fields are added beyond the protobuf options builder and base cancellation trackers.

Control flow: request options are merged over `FileSystemOptionsUtils.setAclDefaults(Configuration.global())` and passed to ACL mutation internals. Diagnostic `toString` renders the built protobuf options.

State and persistence behavior: no direct persistence in this class, but the options determine journaled ACL updates to inode metadata downstream.

Dependencies and integration points: depends on ACL protobuf options, configuration defaults, and `OperationContext`. It integrates with `DefaultFileSystemMaster` set-ACL paths and inode ACL structures.

Risks: thin wrapper; future ACL-specific internal state such as metadata-load or audit controls would need explicit additions. Mutable builder reuse remains unsafe.

Test signals: default merging, recursive ACL behavior, action-specific ACL mutations, and cancellation handling are the main coverage points.
