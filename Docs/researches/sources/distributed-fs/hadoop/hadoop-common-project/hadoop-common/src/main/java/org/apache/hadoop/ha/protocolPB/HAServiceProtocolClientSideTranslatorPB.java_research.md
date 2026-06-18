# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/HAServiceProtocolClientSideTranslatorPB.java

Purpose: Client-side protobuf RPC translator that implements `HAServiceProtocol` and forwards calls to an `HAServiceProtocolPB` proxy.

Important APIs and types: Constructors for address/config and address/config/socket-factory/timeout, `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, `transitionToObserver()`, `getServiceStatus()`, `close()`, `getUnderlyingProxyObject()`, and private conversion helpers for service state and request source.

Control flow: Constructors set the protocol engine to `ProtobufRpcEngine2` and create an RPC proxy. Calls build static or per-call protobuf request messages, invoke the PB proxy through `ShadedProtobufHelper.ipc()`, and convert protobuf status responses back into `HAServiceStatus`.

State and persistence: Holds only the RPC proxy. No persistent state; effects are remote service protocol operations.

Dependencies and integration points: Used by `HAServiceTarget` proxy factories. Depends on generated `HAServiceProtocolProtos`, Hadoop RPC, UGI, socket factories, shaded protobuf helpers, and `ProtocolTranslator`.

Risks: Conversion defaults unknown service-state protobufs to `INITIALIZING`, which may hide enum drift. Request source conversion throws on unknown Java enum values. Callers must `close()` or stop the underlying proxy to release resources.

Test signals: Protocol translator tests, admin/failover tests using PB proxies, observer transition tests, timeout/retry tests, and readiness reason round-trip tests validate this translator.
