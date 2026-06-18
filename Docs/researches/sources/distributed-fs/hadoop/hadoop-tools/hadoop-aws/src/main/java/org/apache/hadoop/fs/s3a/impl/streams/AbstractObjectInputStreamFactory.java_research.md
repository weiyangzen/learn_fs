# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AbstractObjectInputStreamFactory.java

## Purpose
`AbstractObjectInputStreamFactory` provides shared service lifecycle binding and base capability reporting for S3A object input stream factories.

## Important APIs and Types
It extends `AbstractService` and implements `ObjectInputStreamFactory`. `bind(FactoryBindingParameters)` stores callbacks after checking the service is initialized. `hasCapability(String)` reports IO statistics, stream leak tracking, and stream-type capability support. `callbacks()` exposes bound factory callbacks to subclasses.

## Control Flow
During `S3AStoreImpl` initialization, concrete factories are initialized as services, then bound with callbacks. Capability queries normalize input to lower case and match base capabilities or `streamType().capability()`.

## State and Persistence
It stores binding parameters and callbacks in memory. No persistence.

## Dependencies and Integration Points
It depends on Hadoop service lifecycle, stream capability names, statistic names, and `FactoryBindingParameters`. Concrete subclasses include classic and analytics factories.

## Risks and Edge Cases
Binding before or after the initialized state fails. Subclasses depend on non-null callbacks after bind. Capability string case handling uses Hadoop lower-case utility.

## Test Signals
Tests should verify bind state checks, callback availability after bind, base capabilities, stream-type dynamic capability, and subclass override interactions.
