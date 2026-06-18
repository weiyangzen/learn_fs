# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/Parameters.java

## Purpose
`Parameters` is a request-scoped container for parsed query parameters created by `ParametersProvider`.

## Important APIs, Types, and Functions
The constructor accepts `Map<String, List<Param<?>>>`. `get(String name, Class<T> klass)` returns the first parsed value cast to the requested `Param` subclass. `getValues(String name, Class<T> klass)` returns all non-null values for multi-valued parameters.

## Control Flow
Lookup is by parameter name. Single-value lookup returns null for missing or empty lists. Multi-value lookup creates a new list, casts each `Param`, and skips null values.

## State and Persistence
It holds the request parameter map only. It does not persist or mutate external state after construction.

## Dependencies and Integration Points
HttpFS resource methods use `Parameters` to read typed values by concrete parameter class. It depends on Hadoop `Lists` for list construction.

## Risks
The `klass` argument is used only for unchecked casts; it does not validate that the stored parameter class matches. Missing parameters return null even if a default object was not registered. Multi-valued lookup silently drops null defaults, which may be correct for optional lists but important for callers.

## Test Signals
The broad operation matrix in `BaseTestHttpFSWith` covers single and multi-value retrieval through operations such as xattr names, ACL entries, concat sources, and snapshot parameters.
