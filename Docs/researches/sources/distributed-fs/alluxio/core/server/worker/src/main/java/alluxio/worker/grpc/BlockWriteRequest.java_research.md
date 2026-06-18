# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequest.java

## Purpose
`BlockWriteRequest` is the immutable internal representation of a block-oriented gRPC write command. It extends common `WriteRequest` state with tier, medium type, and optional UFS-block creation options.

## Important APIs, Types, and Functions
The constructor reads `tier`, `mediumType`, and `createUfsBlockOptions` from `request.getCommand()`. Accessors expose `getTier()`, `getMediumType()`, `getCreateUfsBlockOptions()`, and `hasCreateUfsBlockOptions()`. `toStringHelper()` adds tier and UFS options to the base request description.

## Control Flow, State, and Persistence
The object is immutable after construction and does not perform IO. Its `CreateUfsBlockOptions` field controls whether `UfsFallbackBlockWriteHandler` can write a block to under storage instead of local block storage.

## Dependencies and Integration Points
It depends on protobuf `Protocol.CreateUfsBlockOptions` and the gRPC write command schema. It is consumed by `BlockWriteRequestContext`, `BlockWriteHandler`, and `UfsFallbackBlockWriteHandler`.

## Risks and Test Signals
Risks are mostly validation gaps: the constructor trusts the command type and command fields. Tests should cover presence/absence of UFS options, medium/tier propagation, and handler behavior when fields are missing or inconsistent.
