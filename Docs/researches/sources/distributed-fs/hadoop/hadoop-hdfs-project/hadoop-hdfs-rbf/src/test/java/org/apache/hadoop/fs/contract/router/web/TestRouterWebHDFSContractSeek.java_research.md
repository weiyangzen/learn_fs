# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractSeek.java

This class runs `AbstractContractSeekTest` through Router WebHDFS, but disables three inherited seek edge cases.

Setup and teardown use `RouterWebHDFSContract`; `createContract` returns the WebHDFS contract. `testNegativeSeek`, `testSeekReadClosedFile`, and `testSeekPastEndOfFileThenReseekAndRead` only print "Not supported", indicating WebHDFS or the Router WebHDFS client does not support those generic seek scenarios in this context.

State is the WebHDFS mini cluster and inherited test files. Dependencies include JUnit and Hadoop seek contract tests. Integration points are WebHDFS `OPEN` reads, datanode redirects, and Router path resolution.

Risks include weakened coverage for seek boundary/error behavior and silent passing because disabled tests print instead of asserting a skip assumption. The positive signal is basic seek/read compatibility where inherited supported cases still run through Router WebHDFS.
