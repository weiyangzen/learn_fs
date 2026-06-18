# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapResponse.java

Purpose: helper for writing accepted portmap responses with typed result payloads.

Important APIs/types/functions: `voidReply`, `intReply`, `booleanReply`, and `pmapList`.

Control flow: each method writes a successful `RpcAcceptedReply` with `VerifierNone`, then appends the requested payload. `pmapList` writes a linked-list style sequence of boolean-present markers plus serialized mappings, terminated by false.

State and persistence: stateless utility; no persistence.

Dependencies and integration: used by `RpcProgramPortmap` procedures to build XDR responses.

Risks: always emits success; callers must choose other reply paths for procedure unavailable or errors. `pmapList` order follows array order from the caller, which for concurrent map values is not deterministic.

Test signals: `TestPortmap` and XDR tests cover reply encoding and list termination.
