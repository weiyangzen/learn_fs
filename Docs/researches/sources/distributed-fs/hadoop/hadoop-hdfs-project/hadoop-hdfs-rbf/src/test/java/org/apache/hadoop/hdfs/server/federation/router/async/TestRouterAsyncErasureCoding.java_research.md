# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncErasureCoding.java

Purpose: exercises `AsyncErasureCoding` router wrappers for policy assignment, policy/codecs retrieval, adding a new EC policy, and topology verification.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterAsyncRpcClient`, `AsyncErasureCoding`, `StripedFileTestUtil`, `ErasureCodingPolicy`, `ErasureCodingPolicyInfo`, `AddErasureCodingPolicyResponse`, `ECTopologyVerifierResult`, `ECSchema`, `HdfsFileStatus`, `MockResolver`, and `syncReturn`. The cluster has one HA nameservice, three DNs, and rack placement to support EC checks.

Control flow: setup creates `/testdir/testAsyncErasureCoding.file`, wires a spy RPC server to an async client, and maps `/` to `ns0`. The test sets the default EC policy on `/testdir`, fetches it back, compares all policy and codec listings with direct NN client results, adds an `RS-12-4-1024k` policy, verifies policy count increases, and checks topology support for both supported and unsupported policy sets.

State and persistence behavior: EC policy state is persisted in the namenode and file/directory state is cleaned per test. Dependencies include HDFS EC configuration, datanode/rack topology, async RPC, and direct NN client comparison. Risks include EC policy global state across tests, topology assumptions tied to DN count, and async context ordering. Test signals include policy names, full policy arrays, codec maps, add-policy success, and topology support booleans.
