# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/protocol/TestReadOnly.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/protocol/TestReadOnly.java` is a JUnit test source read as a complete 107-line file. It tests `@ReadOnly` annotations on `ClientProtocol` methods.

## Important APIs, Types, and Functions

Test methods: `testReadOnly`. Supporting declarations include `TestReadOnly` and helper methods `for`, `checkIsReadOnly`, `if`, `assertEquals`, `IllegalArgumentException`. The test body enumerates all public `ClientProtocol` methods and checks expected read-only method names against annotation presence.

## Control Flow

JUnit constructs the test class, runs any setup hooks, then each test builds the required mock or fixture state, invokes the HDFS client/protocol API under test, and asserts expected values, exceptions, counters, ordering, or lifecycle cleanup. Some tests deliberately use repeated iterations, background threads, or sleeps to expose concurrency and daemon cleanup behavior.

## State and Persistence Behavior

The test state is local to JVM memory: mocks, static fixtures, counters, fake peers, thread snapshots, and configuration objects. It does not persist HDFS namespace state to disk. Where background daemons are involved, the tests explicitly close caches/clients or count matching threads to detect leaks.

## Dependencies and Integration Points

Direct dependency signals from imports: `ReadOnly`, `Test`, `Method`, `Arrays`, `HashSet`, `Set`, `assertEquals`. These tests integrate with HDFS client classes, protocol model classes, Mockito/JUnit assertions, Hadoop configuration utilities, and in some cases HA/failover or URL stream handler infrastructure.

## Risks and Edge Cases

The test guards retry/failover behavior that depends on read-only RPC classification. The most fragile areas are timing-based expiry/thread assertions, global JVM URL handler state, reflection-based API comparisons, and mocked DNS/proxy behavior that can drift from production setup.

## Test Signals

The file itself is the test signal for the related production code. Passing it indicates the covered API contract, equality/hash semantics, concurrency behavior, or compatibility annotation remains intact; failures should be treated as potential regressions in HDFS client compatibility.
