# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAFsck.java

## Purpose
`TestHAFsck` verifies that the `DFSck` command works against an HA nameservice before and after failover, and when one standby NameNode is stopped. It runs the same scenario for configured failover and request-hedging proxy providers.

## Important APIs, Types, And Functions
The parameterized class takes a proxy-provider class name from `data`: `ConfiguredFailoverProxyProvider` or `RequestHedgingProxyProvider`. The main test is `testHaFsck`, with helper `runFsck`. It uses a `MiniDFSNNTopology` with explicit HTTP ports, `HATestUtil.setFailoverConfigurations`, `FileSystem`, `DFSck`, and `ToolRunner`.

## Control Flow
The test starts a two-NameNode cluster, transitions NN0 active, configures HA failover, creates `/test1` and `/test2`, and runs fsck. It then fails over to NN1 and runs fsck again. Finally it stops the old standby and runs fsck a third time, proving the command can still find the active.

## State And Persistence
The persistent namespace state is two test directories. Runtime state includes active/standby roles, HTTP endpoint configuration, and the selected client proxy provider.

## Dependencies And Integration Points
This test covers integration among `DFSck`, HA logical URI configuration, NameNode HTTP ports, client failover providers, and active NameNode discovery.

## Risks
Fsck uses both RPC and HTTP-oriented NameNode information, so HA configuration bugs can surface differently than normal `FileSystem` calls. Request hedging can mask or expose standby failures depending on provider behavior.

## Test Signals
`runFsck` expects exit code 0 and output containing both `/test1` and `/test2` in all three phases.
