# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigRecord.java

## Purpose
`ConfigRecord` is a small mutable data holder for one reported configuration property from a master or worker. It records the `PropertyKey`, source, and optional value.

## Important APIs and Types
- Fields: `PropertyKey mKey`, `String mSource`, `Optional<String> mValue`.
- Has a no-arg constructor for fluent population and a full constructor.
- Getters return key, source, and optional value.
- Fluent setters return `this` for stream mapping in `ConfigurationStore`.

## Control Flow
There is no complex control flow. `setValue` and the full constructor wrap nullable values with `Optional.ofNullable`.

## State and Persistence
State is in-memory and lives inside `ConfigurationStore`. It is not journaled here.

## Dependencies and Integration Points
Used by `ConfigurationStore` and `ConfigurationChecker` to compare effective server-side configuration values across nodes.

## Risks and Edge Cases
The no-arg constructor allows partially initialized records. Callers must set key/source/value before records are consumed by `ConfigurationChecker`.

## Test Signals
Tests should cover nullable value handling, fluent setter chaining, and getter correctness.
