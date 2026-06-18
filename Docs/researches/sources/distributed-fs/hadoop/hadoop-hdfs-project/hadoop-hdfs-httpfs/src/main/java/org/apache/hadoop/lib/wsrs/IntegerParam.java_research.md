# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/IntegerParam.java

## Purpose
`IntegerParam` is the base parser for integer query parameters in HttpFS REST resources.

## Important APIs, Types, and Functions
It extends `Param<Integer>`, implements `parse(String)` with `Integer.parseInt`, and reports the domain `"an integer"`.

## Control Flow
Default handling and exception wrapping are inherited from `Param`. Concrete subclasses define names and defaults, while this base class supplies conversion.

## State and Persistence
Only per-instance parsed value is stored.

## Dependencies and Integration Points
HttpFS parameter definitions use integer values for options such as list limits, snapshot diff indices, and numeric request modifiers.

## Risks
No range checks are applied here. Domain-specific minimums, maximums, or sentinel values must be validated by concrete parameter users or filesystem APIs.

## Test Signals
`BaseTestHttpFSWith` exercises integer-like parameters through snapshot diff listing index values and filesystem operation options.
