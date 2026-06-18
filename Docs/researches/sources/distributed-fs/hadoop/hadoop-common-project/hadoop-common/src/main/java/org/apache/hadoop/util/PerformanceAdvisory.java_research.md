# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PerformanceAdvisory.java

## Purpose

`PerformanceAdvisory` is a central logger holder for non-fatal performance advisories.

## Important APIs, Types, And Functions

The class exposes a single public static `Logger LOG` named for `org.apache.hadoop.util.PerformanceAdvisory`.

## Control Flow, State, And Persistence

There is no method control flow. Runtime state is the static SLF4J logger; persistence is whatever logging backend writes.

## Dependencies And Integration Points

It depends on SLF4J. Other Hadoop code can log performance warnings to this category so operators can route or filter advisory messages separately from functional errors.

## Risks And Test Signals

Because it is just a shared logger, misuse can blur performance hints with correctness warnings. Tests rarely need this class directly; integration signals are correct logger category names and expected log emission from callers.
