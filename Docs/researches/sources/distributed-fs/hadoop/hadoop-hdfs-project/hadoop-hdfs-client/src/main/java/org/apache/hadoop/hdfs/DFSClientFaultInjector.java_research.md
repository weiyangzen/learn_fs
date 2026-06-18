# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSClientFaultInjector.java

## Purpose
`DFSClientFaultInjector` is a private, visible-for-testing singleton that provides no-op production hooks for injecting failures or delays into HDFS client read, write, lease, packet, and block-reader paths.

## Important APIs, Types, and Functions
The class exposes static `get()` and `set()` for replacing the singleton, plus a public static `AtomicLong exceptionNum` used by tests. Hook methods include `corruptPacket`, `uncorruptPacket`, `failPacket`, `startFetchFromDatanode`, `fetchFromDatanodeException`, `readFromDatanodeDelay`, `skipRollingRestartWait`, `sleepBeforeHedgedGet`, `delayWhenRenewLeaseTimeout`, `onCreateBlockReader`, `failCreateBlockReader`, and `failWhenReadWithStrategy`.

## Control Flow
Production execution calls these methods at predefined points and gets default no-op or `false` behavior. Tests replace the singleton with a subclass or Mockito mock, then force behavior such as invalid block-token failures, delayed hedged reads, packet corruption, block-reader creation failures, or lease-renewal timing changes. Because all hooks are methods on one global instance, a test must restore the old injector after use.

## State and Persistence
The only persistent state is process-local: the static singleton and `exceptionNum`. There is no synchronization around `set()`, so safe use assumes tests serialize or restore it carefully. No filesystem or NameNode state is stored here.

## Dependencies and Integration Points
Call sites include `DFSPacket` packet corruption/failure paths, `DFSInputStream` block-reader creation and datanode read paths, `DFSStripedInputStream` striped reader hooks, `BlockReaderFactory` read strategy hooks, and `LeaseRenewer` timeout delay hooks. The method signatures depend on `LocatedBlock` and `InvalidBlockTokenException` so tests can emulate data-transfer token failures precisely.

## Risks
The global mutable singleton is easy to leak across tests and can make concurrent tests interfere with each other. Adding a new production hook without a default no-op would make tests brittle. Hook methods that throw checked exceptions must preserve the exact production exception type expected by retry logic; otherwise tests can validate unrealistic paths.

## Test Signals
`TestPread`, `TestRead`, `TestDFSInputStream`, `TestDFSStripedInputStream`, `TestClientProtocolForPipelineRecovery`, `TestCrcCorruption`, `TestDFSClientRetries`, and `TestPipelineCloseRecoveryByteArrayLeak` all replace or mock this injector. Coverage signals should include restoration of the previous singleton in `finally` blocks and assertions that injected delays/failures drive the intended retry, hedged-read, or recovery branch.
