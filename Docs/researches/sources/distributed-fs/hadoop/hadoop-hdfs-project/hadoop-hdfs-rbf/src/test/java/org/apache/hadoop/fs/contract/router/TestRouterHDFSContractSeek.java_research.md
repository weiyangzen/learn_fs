# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeek.java

This class runs `AbstractContractSeekTest` against a non-secure Router RPC filesystem. It validates inherited seek/read behavior through RBF.

Setup starts the normal Router cluster; teardown destroys it. The contract factory returns `RouterHDFSContract`. No inherited seek cases are disabled in the RPC variant.

State is the mini HDFS cluster and test files created by the seek contract suite. Dependencies include JUnit and Hadoop FS contract classes. Integration points are Router open/read forwarding, DFS input stream behavior, block locations, and active namenode routing.

Risks include random-router selection and lack of direct failover/observer-read coverage, but this class gives useful regression coverage for standard seek semantics through Router RPC. The test signal is non-secure seek compatibility.
