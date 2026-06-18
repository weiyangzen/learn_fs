<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/web/resources/NamenodeWebHdfsMethods.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/web/resources/NamenodeWebHdfsMethods.java

## Purpose

`NamenodeWebHdfsMethods` is the JAX-RS NameNode-side implementation of WebHDFS. It handles HTTP PUT/POST/GET/DELETE operations, executes metadata operations against `ClientProtocol`, redirects block-data operations to DataNodes, manages delegation-token query construction, and preserves remote-user context across servlet and IPC call-queue boundaries.

## Important APIs and types

- JAX-RS endpoints: `putRoot`/`put`, `postRoot`/`post`, `getRoot`/`get`, `deleteRoot`/`delete`.
- Operation dispatch switches on `PutOpParam.Op`, `PostOpParam.Op`, `GetOpParam.Op`, and `DeleteOpParam.Op`.
- `init` logs parameters, lazily reads `DFS_WEBHDFS_USE_IPC_CALLQ`, and clears response content type.
- `doAs` chooses direct `ugi.doAs` or `ExternalCall` queueing.
- `chooseDatanode`, `bestNode`, and `redirectURI` implement DataNode selection and redirect URI building.
- Token helpers: `createCredentials`, `generateDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`.
- Listing/trash helpers: `getListingStream`, `getDirectoryListing`, `getTrashRoot`, `getTrashRoots`, `getSnapshotRoot`, `getParent`.

## Control flow

The constructor extracts scheme, principal, trusted-proxy-aware remote address/port, and encryption-zone header support from the servlet request because external calls may run in a different thread. Endpoint methods parse URI/query parameters, call `init`, then execute the protected operation method under the request UGI.

PUT handles create redirects, mkdirs, symlink, rename, replication/owner/permission/time changes, delegation token renewal/cancel, ACL and xattr mutations, snapshot operations, storage policy operations, EC policy operations, and quota operations. POST handles append redirects, concat, truncate, and unsetting storage/EC policies. GET handles open/checksum redirects, block locations, file/link status, listing and batched listing, content summary, quota usage, delegation tokens, home directory, ACL/xattr reads, access checks, trash roots, storage and EC policy reads, server defaults caching, snapshot reports/listings, fs status, and EC codecs. DELETE handles delete and deleteSnapshot.

Redirects validate HDFS paths, choose an appropriate DataNode, include either user/doAs parameters or delegation tokens depending on security mode, include the NameNode address, and optionally return JSON `Location` when `noredirect=true`. For encrypted files with `supportEZ`, open redirects use `/.reserved/raw` and return encoded file-encryption metadata in a header.

## State and persistence behavior

The resource stores per-request-derived fields plus cached `useIpcCallq` and `supportEZ`. Persistent namespace changes happen through `ClientProtocol` RPCs: create/mkdir/rename/delete, ACL/xattr, snapshots, quotas, storage policies, EC policies, truncate, and token state. Servlet context caches `"serverDefaults"` JSON and exposes `"name.node"` and current configuration.

## Dependencies and integration points

This class is the bridge between WebHDFS clients, servlet/Jersey injection, Hadoop authentication/UGI, NameNode `ClientProtocol`/`NamenodeProtocols`, BlockManager DataNode placement, DataNode HTTP(S) info ports, JSON serialization via `JsonUtil`, delegation token secret management, encryption zones, trash, snapshots, EC, ACLs, xattrs, and audit/IPC call queue behavior.

## Risks and edge cases

- Redirect operations must preserve security parameters exactly; token kind switches between WEBHDFS and SWEBHDFS based on scheme.
- `chooseDatanode` must respect excluded nodes, offsets, decommissioned nodes, missing blocks, zero-length files, and fallback random selection.
- Streaming directory listings cannot change HTTP status after output begins, so the first batch is fetched before creating `StreamingOutput`.
- `validateOpParams` treats null or empty value strings as missing; parameter defaults must align with each operation's required fields.
- Cached server defaults can become stale if future server defaults become reloadable.
- `getSnapshotRoot` uses string prefix matching and must avoid false positives across similarly named directories.
- The resource has many query parameters and suppresses parameter-count checks in places; adding operations is easy to regress.

## Test signals

Strong signals come from `TestWebHDFS`, `TestWebHdfsDataLocality`, `TestWebHdfsCreatePermissions`, WebHDFS ACL/XAttr/token/auth/HA/URL/timeout tests, encryption-zone WebHDFS tests, trash tests, snapshot tests, storage-policy command tests, and audit-log tests. Key cases include `noredirect`, invalid paths, offset/length bounds, block-location JSON, EC policy APIs, SPS invocation, create permission masking, special-character URLs, proxy-user/delegation behavior, and DataNode locality/exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/web/resources/NamenodeWebHdfsMethods.java -->
