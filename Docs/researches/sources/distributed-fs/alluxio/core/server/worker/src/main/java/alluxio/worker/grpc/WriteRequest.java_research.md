# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequest.java

## Purpose
`WriteRequest` is the base immutable internal representation of a gRPC write command. It captures common fields used by all write variants: target ID, pin-on-create flag, and a generated worker session ID.

## Important APIs, Types, and Functions
The constructor reads `command.id` and `command.pinOnCreate`, then creates a fresh session ID with `IdUtils.createSessionId()`. Accessors expose `getId()`, `getPinOnCreate()`, and `getSessionId()`. `toString()` delegates to a subclass-extensible `toStringHelper()`.

## Control Flow, State, and Persistence
The generated session ID scopes temporary worker resources such as temp blocks. The object performs no persistence itself but is passed into handlers that create, commit, abort, or clean up resources.

## Dependencies and Integration Points
It integrates with gRPC write command schema, `IdUtils`, and subclasses `BlockWriteRequest` and `UfsFileWriteRequest`.

## Risks and Test Signals
Risks include one session ID per request object, which makes first-message construction timing important, and lack of base validation for command type or required fields. Tests should check session uniqueness and pin/id propagation.
