# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkItem.java

## Purpose

`DiskBalancerWorkItem.java` is a JSON-serializable progress and limit record for a disk balancer copy step. It tracks how much data and how many blocks have been copied, elapsed time, error state, and balancing limits such as tolerated disk errors, tolerance percent, and bandwidth.

## Important APIs, Types, and Functions

The class is annotated `@JsonInclude(JsonInclude.Include.NON_DEFAULT)` and uses static Jackson `ObjectMapper`/`ObjectReader`. It has an empty constructor for JSON, a constructor accepting `bytesToCopy` and `bytesCopied`, static `parseJson(String)`, `toJson()`, getters/setters for all fields, and increment helpers `incErrorCount`, `incCopiedSoFar`, and `incBlocksCopied`.

## Control Flow

`parseJson` checks the input JSON is non-null and deserializes it with the typed reader. Runtime update flow is expected to mutate counters as work proceeds: increment copied bytes/blocks/errors, set elapsed seconds and error message, then serialize status to JSON for reporting or persistence. `toJson` writes the current object through Jackson.

## State and Persistence Behavior

All fields are mutable bean properties. JSON serialization omits default-valued fields, so absent fields deserialize back to Java defaults. This compact JSON is the persistence/interchange format used by disk balancer status paths. The elapsed time is explicitly stored instead of derived from client time to avoid client/server clock skew.

## Dependencies and Integration Points

Dependencies include Jackson annotations/databind, Hadoop `Preconditions`, and audience/stability annotations. It integrates with DataNode disk balancer planning/execution/status code that reports work-item progress and enforces bandwidth/error/tolerance limits.

## Risks and Edge Cases

There is no validation for negative counters, decreasing copied bytes, overflow, or nonsensical bandwidth/tolerance values. Static mapper instances are shared and should remain thread-safe for normal Jackson read/write usage. Omitting default fields means consumers must distinguish absent from explicit zero only by contract, not JSON shape.

## Test Signals

Tests should cover JSON parse/write round trips, omission of default fields, null JSON rejection, counter increment behavior, elapsed-time field preservation, error message/count updates, and compatibility when older JSON lacks newer fields.
