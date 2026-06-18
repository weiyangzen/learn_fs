# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/OpenFileParameters.java

## Purpose
Bean-style parameter carrier for openFileWithOptions implementations.

## Important APIs, Types, and Functions
withMandatoryKeys(), withOptionalKeys(), withOptions(), withBufferSize(), withStatus(); getters for all fields.

## Control Flow
Fluent setters require non-null key sets/options, assign fields, and return this. Status may be null.

## State and Persistence Behavior
Stores references to provided sets/config/status rather than defensive copies. No persistence.

## Dependencies and Integration Points
Used to pass FutureDataInputStreamBuilder state into filesystem open implementations.

## Risks and Test Signals
Risks are caller mutation of sets/config after handoff and unset fields. Tests should cover null rejection and reference semantics.
