# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServicePlugin.java

## Purpose
`ServicePlugin` defines a private lifecycle extension point for Hadoop services such as NameNode and DataNode to load plugins that expose additional functionality, often through custom RPC protocols.

## Important APIs, Types, And Functions
The interface extends `Closeable` and declares `start(Object service)` and `stop()`. `close()` is inherited and left to implementations.

## Control Flow
The service instantiates plugins, starts them after the service itself starts, and stops them before the service shuts down. This file only defines the callback order contract; it does not enforce it.

## State And Persistence
The interface owns no state. Plugin implementations may manage resources, network servers, or persisted state.

## Dependencies And Integration Points
It depends on `Closeable` and Hadoop annotations. It integrates with service plugin loading mechanisms in HDFS and other daemon code.

## Risks
The service parameter is typed as `Object`, so implementations must cast carefully. The relationship between `stop` and `close` is not defined here. Exceptions and timeout handling are owned by plugin managers, not the interface.

## Test Signals
Tests should focus on service-side plugin managers: construction, lifecycle order, service object type, exception handling, stop/close invocation, and cleanup before daemon shutdown.
