<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Metrics2Util.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Metrics2Util.java

## Purpose
`Metrics2Util` contains small support types for metrics2 producers and sinks, currently a value pair and fixed-size top-N queue.

## Important APIs and Types
`NameValuePair` stores a metric name and long value, implements `Comparable`, and exposes getters. `TopN` extends `PriorityQueue<NameValuePair>`, keeps at most `n` largest values, and records the total value of all offered entries.

## Control Flow
`TopN.offer` always adds the offered value to the running total. If the queue is already at capacity, it compares the new value with the current smallest item. Values not greater than the smallest are rejected; larger values replace the smallest.

## State and Persistence
All state is in-memory: pair fields, queue contents, capacity `n`, and running total.

## Dependencies and Integration Points
The utility supports metrics that report top users, operations, or other ranked counts. It depends only on Java collections and Hadoop audience annotations.

## Risks and Test Signals
`NameValuePair.compareTo` casts a long difference to int, which can overflow and produce incorrect ordering for very large differences. Equality and hash code ignore the name and depend only on value. Tests should cover ordering, equal values with different names, total accumulation for rejected entries, capacity behavior, and overflow-sized values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Metrics2Util.java -->
