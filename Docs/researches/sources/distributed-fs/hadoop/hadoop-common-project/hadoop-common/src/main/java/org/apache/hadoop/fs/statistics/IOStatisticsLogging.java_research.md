# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsLogging.java

Purpose: utility class for converting IOStatistics sources to robust log strings and logging them at configured levels without forcing expensive evaluation unless needed.

Important APIs, types, and functions: `ioStatisticsSourceToString()`, `ioStatisticsToString()`, `ioStatisticsToPrettyString()`, `demandStringifyIOStatisticsSource()`, `demandStringifyIOStatistics()`, `logIOStatisticsAtDebug()`, and `logIOStatisticsAtLevel()`. Private helpers render maps through `IOStatisticsBinding.entryToString()` and sorted `TreeMap` copies.

Control flow: source objects are converted through `IOStatisticsSupport.retrieveIOStatistics()`. Plain string output iterates all maps in source order; pretty output builds sorted maps and filters zero counters/gauges, unset min/max values, and empty means. Demand stringifiers defer evaluation to `toString()`, making them safe to pass to disabled log statements.

State and persistence: stateless except for a class logger. It reads live statistics maps on demand and does not persist data.

Dependencies and integration points: depends on SLF4J, Hadoop logging level constants, `IOStatisticsSupport`, `MeanStatistic`, and `IOStatisticsBinding`. It integrates with filesystem close/debug paths and optional configured logging of statistics.

Risks and test signals: `logIOStatisticsAtLevel(Logger log, String level, Object source)` accepts a logger but uses the class logger for info/warn/error branches, so tests should detect logger routing expectations. Tests should cover null sources, throwing sources, empty filtering, sorted pretty output, demand stringification, and unknown logging levels falling back to debug.
