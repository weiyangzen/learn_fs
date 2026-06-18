# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterNamenodeProtocolTranslatorPB.java

Purpose: client-side Router translator for the HDFS `NamenodeProtocol`, adding async IPC while inheriting normal synchronous protobuf behavior.

Important APIs and types: extends `NamenodeProtocolTranslatorPB`, stores `NamenodeProtocolPB rpcProxy`, defines reusable empty request protos, and overrides name-node protocol calls for blocks, block keys, transaction IDs, checkpoints, edit manifests, registration, version requests, upgrade status, and SPS path retrieval.

Control flow: each method checks `Client.isAsynchronousMode()`. Sync mode calls the parent. Async mode builds the relevant request proto, invokes `rpcProxy` through `asyncIpcClient`, and converts the response with `PBHelper`/`PBHelperClient`. Optional responses are represented with `hasKeys()` and `hasSpsPath()`.

State and persistence: no local durable state. The translator carries only the RPC proxy and static immutable empty request protos. Protocol calls may mutate downstream NameNode state, for example rolling edit logs or ending checkpoints.

Dependencies and integration points: integrates the Router with HDFS server protocol protobufs, `ExportedBlockKeys`, `CheckpointSignature`, `NamenodeRegistration`, `NamespaceInfo`, `RemoteEditLogManifest`, and `NNStorage.NameNodeFile`. It must align with the server-side Router namenode translator.

Risks: async conversion must match the parent translator exactly, especially around nullable block keys and SPS paths. `nnf.toString()` must be accepted by the server-side `valueOf` conversion. Tests should verify async mode for each protocol family and that exceptions are propagated as `IOException`.
