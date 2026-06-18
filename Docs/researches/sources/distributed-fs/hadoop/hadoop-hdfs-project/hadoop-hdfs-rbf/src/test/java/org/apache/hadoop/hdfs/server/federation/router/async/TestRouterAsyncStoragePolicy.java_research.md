# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncStoragePolicy.java

Purpose: verifies async router storage policy operations against the shared async protocol fixture.

Important APIs/types/functions: `RouterAsyncStoragePolicy`, `BlockStoragePolicy`, `FSDataOutputStream`, `Path`, and `syncReturn`. Setup creates the async storage policy module from the async router RPC server and writes `/testdir/testAsyncStoragePolicy.file`.

Control flow: the test retrieves the namenode's storage policy array directly, calls async `getStoragePolicies()`, and asserts array equality. It then reads the current policy for the test file, calls async `setStoragePolicy(testfilePath, "COLD")`, reads the policy again, verifies it changed, and checks the returned policy name is `COLD`. The path under test routes through the base fixture's mock `/` mapping to `ns0`.

State and persistence behavior: storage policy metadata is stored on the namenode for the test file and removed when the base fixture deletes `/testdir`. Integration points include router async storage-policy wrappers, NN storage policy protocol, path resolution, and async result conversion. Risks include hard-coded default policy availability and storage policy support varying with cluster configuration. Test signals are full policy-array equality, changed file policy, and exact `COLD` policy name.
