# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/impl/MountTableStoreImpl.java

Purpose: Implements the `MountTableStore` API for creating, updating, removing, listing, and refreshing federation mount table entries.

Important APIs/types/functions: key methods are `addMountTableEntry`, `addMountTableEntries`, `updateMountTableEntry`, `removeMountTableEntry`, `getMountTableEntries`, `refreshMountTableEntries`, and unsupported `getDestination`. Helper permission checks use `RouterAdminServer.getPermissionChecker`, `RouterPermissionChecker`, `FsAction`, and parent-path traversal.

Control flow: add and update validate `MountTable` entries, enforce write/execute permissions on parent or target entries, write through the driver with the correct duplicate/update flags, and notify all routers to refresh caches on success. Bulk add validates and checks every requested entry before one `putAll`. Remove resolves the exact existing entry, checks write permission, removes it, and refreshes caches on success. Listing sorts cached records by source path, filters to entries under the requested path, removes entries the caller cannot read, and overlays quota usage from the quota manager when present.

State/persistence behavior: durable state is driver-backed `MountTable` records; this class also uses cached records and may augment returned records with current quota consumption. Successful mutations trigger router-wide cache updates.

Dependencies/integration: integrates with router admin security, quota cache, DFS path parent checks, protocol request/response objects, `StateStoreOperationResult`, and `MountTable` validation/comparators.

Risks: permission traversal assumes slash-separated non-empty paths and can be sensitive at root; bulk add is all-or-nothing only at validation/permission stage, while driver `putAll` can partially fail; quota overlay mutates returned cached record objects; `getDestination` deliberately throws because destination resolution belongs to RouterRpcServer.

Test signals: permission-denied filtering, parent permission recursion, duplicate add/update/remove outcomes, bulk failed key propagation, cache refresh notification, quota overlay by storage type, and root/empty path cases are critical.
