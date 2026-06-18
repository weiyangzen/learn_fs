# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsInputStream.java

Purpose: `BufferedInputStream` subclass that preserves access to the wrapped stream's `IOStatistics` and stream capabilities.

Important APIs and types: constructors with default/custom buffer size, `getIOStatistics()`, and `hasCapability()`.

Control flow: buffering behavior is inherited. `getIOStatistics()` calls `IOStatisticsSupport.retrieveIOStatistics(in)`. `hasCapability()` delegates to wrapped stream when it implements `StreamCapabilities`, otherwise returns false.

State and persistence: in-memory buffer inherited from `BufferedInputStream`; no durable state or filesystem mutation.

Dependencies and integration: implements `IOStatisticsSource` and `StreamCapabilities`; intended for wrappers around filesystem input streams where statistics should remain discoverable.

Risks: statistics are retrieved from the wrapped stream, not accumulated by the buffer. Capabilities may be affected by buffering semantics even though delegated. Closed-stream behavior follows underlying/inherited stream behavior.

Test signals: cover default/custom buffer construction, statistics delegation for source and non-source streams, capability delegation true/false, read behavior still buffered, and close behavior.
