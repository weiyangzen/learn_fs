# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolServerSideTranslatorPB.java

Purpose: server-side protobuf adapter for `GetUserMappingsProtocol` on the Router, adding async Router RPC support to the standard tools translator.

Important APIs and types: constructor accepts `GetUserMappingsProtocol`, passes it to the parent, casts it to `RouterRpcServer`, and caches `server.isAsync()`. The sole override is `getGroupsForUser(RpcController, GetGroupsForUserRequestProto)`.

Control flow: non-async mode delegates to `super.getGroupsForUser`. Async mode schedules `server.getGroupsForUser(request.getUser())` through `asyncRouterServer`, converts returned group strings into `GetGroupsForUserResponseProto`, and returns `null` because completion is handled asynchronously.

State and persistence: no durable state. It only retains the Router RPC server and async flag. Group data comes from Router security/group mapping services.

Dependencies and integration points: integrates Hadoop tools group lookup protobuf protocol with `RouterRpcServer` and `AsyncRpcProtocolPBUtil.asyncRouterServer`. It pairs with `RouterGetUserMappingsProtocolTranslatorPB`.

Risks: the cast to `RouterRpcServer` assumes the implementation object is exactly the Router server. Async response completion relies on returning `null`; callers must be on the async-capable server path. Tests should cover sync fallback, async response content, empty group lists, and exception propagation from group mapping.
