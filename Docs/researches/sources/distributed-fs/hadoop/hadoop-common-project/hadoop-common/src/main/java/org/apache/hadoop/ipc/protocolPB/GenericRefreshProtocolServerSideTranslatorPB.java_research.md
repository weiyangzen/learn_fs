<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolServerSideTranslatorPB.java

## Purpose
Server-side adapter translating protobuf `GenericRefreshProtocolPB.refresh` calls to a Java `GenericRefreshProtocol` implementation.

## Important APIs, Types, And Functions
- Holds a `GenericRefreshProtocol impl`.
- `refresh(RpcController, GenericRefreshRequestProto)` validates identifier, converts args list to array, calls `impl.refresh`, and packs `RefreshResponse` results.
- IOExceptions are wrapped in shaded protobuf `ServiceException`.

## Control Flow
On each PB request, the translator extracts args, rejects requests missing `identifier`, delegates to the implementation, then creates a `GenericRefreshResponseCollectionProto` with one response proto per returned `RefreshResponse`, setting exit status, user message, and sender name.

## State And Persistence
Stateless aside from the delegate reference. Any durable effects are performed by the delegate refresh implementation.

## Dependencies And Integration Points
Used when exposing generic refresh services over Hadoop PB RPC. Depends on generated protos, shaded `ServiceException`, and `GenericRefreshProtocol`.

## Risks And Edge Cases
`setUserMessage` and `setSenderName` are called unconditionally; if `RefreshResponse` returns null for either, generated protobuf setters may reject null. Missing identifier is treated as `ServiceException` with a string rather than an `IOException` cause. Delegate exceptions are surfaced as remote IO failures through client helper conversion.

## Test Signals
Tests should cover missing identifier, arg conversion, response packing including null fields if possible, and IOException-to-ServiceException translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolServerSideTranslatorPB.java -->
