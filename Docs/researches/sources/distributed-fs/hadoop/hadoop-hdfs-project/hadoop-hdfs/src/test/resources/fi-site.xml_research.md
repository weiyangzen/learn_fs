# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/fi-site.xml

## Purpose

`fi-site.xml` is the HDFS test fault-injection site configuration. The complete 33-line file was read. It provides a default test-resource override that disables all `fi.*` injected faults unless individual tests explicitly raise a fault probability.

## Important APIs, Types, and Functions

The important configuration key is `fi.*` with value `0.00`. Hadoop `Configuration` and test fault-injection utilities consume this wildcard-style property as the default probability for named injected faults. The file uses the standard Hadoop `<configuration><property><name><value><description>` XML format and references `configuration.xsl` for rendering.

## Control Flow

When test configuration resources are loaded, this file contributes `fi.*=0.00`. Fault-injection-aware tests can then layer more specific `fi.<fault-name>` properties on top. With only this file loaded, injected fault decisions should be false because the configured probability is zero.

## State and Persistence Behavior

The file has no runtime persistence beyond in-memory Hadoop configuration state. Its value affects deterministic test execution by making fault injection opt-in rather than default-on.

## Dependencies and Integration Points

It integrates with HDFS tests that enable fault injection through configuration resources, especially tests that need a known baseline before enabling data-transfer, pipeline, or NameNode/DataNode faults. It depends on Hadoop's XML configuration parser and property overlay semantics.

## Risks and Edge Cases

Risks include tests unexpectedly inheriting nonzero fault probabilities, wildcard matching semantics changing, malformed XML preventing configuration load, or a later resource overriding `fi.*` and introducing nondeterminism. The property describes a floating-point probability bounded from 0 to 1.00.

## Test Signals

Signals are successful resource parsing and fault-injection tests behaving normally unless they explicitly configure a specific fault. A broad failure pattern would be random injected faults in unrelated HDFS tests.
