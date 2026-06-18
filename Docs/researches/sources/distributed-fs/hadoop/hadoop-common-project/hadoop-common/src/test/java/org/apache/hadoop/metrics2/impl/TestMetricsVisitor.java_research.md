# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsVisitor.java

## Purpose

`TestMetricsVisitor` validates dispatch from concrete `AbstractMetric` types to the correct `MetricsVisitor.counter()` or `MetricsVisitor.gauge()` overloads.

## Important APIs, Types, And Functions

The test uses `MetricsVisitor`, `AbstractMetric.visit(visitor)`, `MetricsLists.builder()`, `Interns.info()`, Mockito `ArgumentCaptor<MetricsInfo>`, and verification of int, long, float, and double values.

## Control Flow

The test builds a metric list with int/long counters and int/long/float/double gauges, visits each metric with a mock visitor, then verifies each expected visitor method was called with the correct metric info and value.

## State And Persistence Behavior

State is only the generated metric list and Mockito captured arguments. There is no persistent or global state.

## Dependencies And Integration Points

It integrates metric implementation classes, visitor interface dispatch, interned metric metadata, and the metrics list helper. Downstream sinks and serializers rely on the same visitor dispatch.

## Risks And Test Signals

Risks include numeric overload mismatches, counters treated as gauges, and lost metric descriptions. Signals are per-overload Mockito verifications and captured `MetricsInfo` name/description checks.
