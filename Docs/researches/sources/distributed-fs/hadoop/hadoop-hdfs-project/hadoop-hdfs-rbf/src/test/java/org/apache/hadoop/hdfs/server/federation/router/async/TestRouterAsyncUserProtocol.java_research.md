# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncUserProtocol.java

Purpose: verifies async user/group mapping protocol support through the router.

Important APIs/types/functions: `RouterAsyncUserProtocol`, `GetUserMappingsProtocol`, `UserGroupInformation`, and `syncReturn`. It inherits router cluster, async RPC server, and `/testdir` fixture state from `RouterAsyncProtocolTestBase`.

Control flow: setup instantiates `RouterAsyncUserProtocol` from the async RPC server. The test creates a synthetic UGI user named `user` with groups `bar` and `group2`, calls async `getGroupsForUser("user")`, retrieves the `String[]` through `syncReturn`, and asserts exact array equality. This covers the async wrapper path for `GetUserMappingsProtocol` without involving CLI refresh commands.

State and persistence behavior: relies on process-level test UGI/group mapping state; no HDFS filesystem mutations are required beyond the inherited fixture. Integration points include router async protocol module, Hadoop security group mapping, and async result materialization. Risks are singleton UGI/group mapping and async context interactions. Test signal is exact group-array equality returned through the async router module.
