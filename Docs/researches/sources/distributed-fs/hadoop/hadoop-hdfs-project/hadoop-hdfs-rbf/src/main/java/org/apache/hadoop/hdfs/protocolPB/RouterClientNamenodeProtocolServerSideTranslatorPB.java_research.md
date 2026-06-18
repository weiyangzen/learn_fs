# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterClientNamenodeProtocolServerSideTranslatorPB.java

## Purpose
Async server-side protobuf translator that exposes the HDFS `ClientNamenodeProtocol` over an RBF `RouterRpcServer`. It subclasses the standard NameNode server-side translator but overrides methods to call the router asynchronously through `AsyncRpcProtocolPBUtil.asyncRouterServer`.

## Important APIs, Types, and Functions
The constructor accepts a `ClientProtocol`, calls the superclass constructor, and casts it to `RouterRpcServer`. The class overrides most client-facing HDFS operations: block location/defaults, create/append/addBlock/complete, metadata changes, listing, leases, datanode and filesystem stats, safe mode, upgrades, snapshots, cache directives/pools, ACLs, encryption zones, xattrs, storage policies, edit-log queries, erasure coding, quota usage, open-file listing, msync, satisfy-storage-policy, HA state, slow datanode reports, and enclosing-root lookup. Conversion is delegated to `PBHelperClient` and many void methods return superclass-provided `VOID_*` response constants.

## Control Flow
Every overridden method starts `asyncRouterServer(requestLambda, responseLambda)` and returns `null`, relying on Hadoop protobuf RPC deferred response callbacks. Request lambdas read fields from the incoming proto, convert optional fields and repeated lists to native types, and call the corresponding `RouterRpcServer` method. Response lambdas build the expected response proto, handling nullable native results for file info, listings, snapshot listings, encryption zones, storage policies, delegation tokens, and similar optional values.

## State and Persistence Behavior
The translator stores only the router server reference. All filesystem state changes are delegated to `RouterRpcServer`, including namespace mutation, block allocation, leases, snapshots, cache metadata, ACL/xattr/storage-policy changes, encryption-zone operations, erasure-coding policy changes, quotas, and router-visible HA/safemode operations. Per-call async state lives in `CompletableFuture`s and deferred protobuf callbacks managed by `asyncRouterServer`.

## Dependencies and Integration Points
This class is a high-volume integration point among generated HDFS protobuf request/response types, `RouterRpcServer`, `ClientProtocol`, `PBHelperClient`, Hadoop security token protos, HA protos, erasure-coding/encryption/xattr/ACL protos, and async router utilities. It defines the wire behavior that HDFS clients observe when connected to a Router instead of a NameNode.

## Risks and Test Signals
Because almost every method returns `null` immediately, correctness depends on deferred response registration and completion. Optional proto fields require careful defaults, such as create permissions with masked/unmasked modes, append flags defaulting to `APPEND`, `complete` file IDs defaulting to `GRANDFATHER_INODE_ID`, optional snapshot names, optional storage types, and optional null responses. Useful tests compare router client behavior against direct NameNode protocol behavior and cover deferred responses/errors, batched listing exceptions, HA state enum mapping, erasure-coding responses, and high-risk create/append/addBlock/complete paths.
