# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/SourceWrappedStatistics.java

Purpose: simple adapter that wraps an `IOStatistics` instance as an `IOStatisticsSource`.

Important APIs, types, and functions: constructor and `getIOStatistics()`.

Control flow: callers pass an existing statistics object; the wrapper returns the same object whenever requested.

State and persistence: stores a final statistics reference. Any persistence or mutability is owned by the wrapped instance.

Dependencies and integration points: implements `IOStatisticsSource`; created by `IOStatisticsBinding.wrap()`.

Risks and test signals: the wrapper does not snapshot, so consumers see live changes. Tests should cover identity preservation, null input policy, and interaction with `IOStatisticsSupport.retrieveIOStatistics()`.
