# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFCRpcServer.java

Purpose: Hosts the protobuf RPC server for `ZKFCProtocol`, exposing graceful failover and cede-active operations for a local `ZKFailoverController`.

Important APIs and types: `ZKFCRpcServer implements ZKFCProtocol`, constructor, `start()`, `getAddress()`, `stopAndJoin()`, `cedeActive()`, and `gracefulFailover()`. It creates an RPC server with three handlers.

Control flow: Constructor sets `ProtobufRpcEngine2` for `ZKFCProtocolPB`, wraps this server with `ZKFCProtocolServerSideTranslatorPB`, creates a reflective protobuf blocking service, builds an Hadoop RPC server bound to the requested address, and optionally refreshes service ACLs. RPC method implementations first call `zkfc.checkRpcAdminAccess()`, then delegate to `zkfc.cedeActive()` or `zkfc.gracefulFailoverToYou()`.

State and persistence: Holds a reference to the `ZKFailoverController` and an RPC `Server`. It persists no own state.

Dependencies and integration points: Used by `ZKFailoverController.initRPC()` and admin/peer ZKFC clients. Depends on protobuf generated `ZKFCProtocolService`, `ZKFCProtocolPB`, server-side translator, Hadoop RPC and service authorization.

Risks: Missing policy with service authorization enabled is fatal. Binding to the wrong address exposes or hides failover control. Handler count is fixed and small; long failover calls can occupy handlers.

Test signals: `TestZKFailoverController` and RPC server tests should cover bind address, ACL enforcement, admin access denial, cede delegation, graceful failover delegation, and clean stop/join.
