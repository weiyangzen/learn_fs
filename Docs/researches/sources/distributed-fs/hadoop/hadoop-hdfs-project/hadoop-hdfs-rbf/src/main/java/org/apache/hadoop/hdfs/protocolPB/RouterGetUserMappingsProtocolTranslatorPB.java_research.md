# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolTranslatorPB.java

Purpose: client-side Router translator for `GetUserMappingsProtocol`, preserving normal protobuf behavior while using async IPC when the Hadoop IPC client is in asynchronous mode.

Important APIs and types: stores `GetUserMappingsProtocolPB rpcProxy` and overrides `getGroupsForUser(String)`.

Control flow: sync mode delegates to the standard client-side translator. Async mode builds `GetGroupsForUserRequestProto`, invokes `rpcProxy.getGroupsForUser(null, request)` via `asyncIpcClient`, and converts the response group list into a `String[]`.

State and persistence: no persisted state; the only field is the PB proxy. Runtime state is the requested user and response group list.

Dependencies and integration points: pairs with the Router server-side user-mapping translator and Hadoop tools protocol PB classes. It depends on `Client.isAsynchronousMode()` and `AsyncRpcProtocolPBUtil.asyncIpcClient` matching the async IPC contract.

Risks: group order and duplicates are passed through exactly as returned. Empty responses must produce an empty array. Tests should exercise sync parity and async group lookup with users that have zero, one, and multiple groups.
