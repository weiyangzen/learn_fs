# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/AbstractIOStatisticsImpl.java

Purpose: tiny base class for IOStatistics implementations that standardizes `toString()` through the logging formatter.

Important APIs, types, and functions: implements `toString()` by calling `IOStatisticsLogging.ioStatisticsToString(this)`.

Control flow: subclasses provide the statistics maps; `toString()` delegates all rendering to the public logging utility.

State and persistence: no state. It only reads subclass state during stringification.

Dependencies and integration points: depends on `IOStatistics` and `IOStatisticsLogging`. Extended by empty and dynamic statistics implementations.

Risks and test signals: stringification can evaluate dynamic maps and may not be cheap. Tests should cover subclass `toString()` output for empty and dynamic implementations.
