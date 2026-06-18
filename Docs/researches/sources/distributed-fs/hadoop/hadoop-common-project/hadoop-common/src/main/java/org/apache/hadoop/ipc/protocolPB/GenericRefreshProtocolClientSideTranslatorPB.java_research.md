<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolClientSideTranslatorPB.java

## Purpose
Client-side adapter translating the Java `GenericRefreshProtocol` API to the shaded protobuf `GenericRefreshProtocolPB` blocking stub.

## Important APIs, Types, And Functions
- Implements `ProtocolMetaInterface`, `GenericRefreshProtocol`, and `Closeable`.
- `refresh(String identifier, String[] args)` builds `GenericRefreshRequestProto`, invokes `rpcProxy.refresh`, and unpacks the response collection.
- `close()` stops the RPC proxy.
- `isMethodSupported(String methodName)` delegates to `RpcClientUtil`.

## Control Flow
The translator converts args to a list, builds the request, invokes the PB stub through `ShadedProtobufHelper.ipc` for exception normalization, then maps each `GenericRefreshResponseProto` to `RefreshResponse`, preserving optional user message, exit status, and sender name when present.

## State And Persistence
Holds only the proxied PB stub. No persistent state.

## Dependencies And Integration Points
Used by clients of the generic refresh admin mechanism. Integrates with Hadoop RPC proxy lifecycle, shaded protobuf protos, and method-support metadata.

## Risks And Edge Cases
`Arrays.asList(args)` requires non-null `args`; null arrays fail before RPC. Missing optional response fields map to message/sender null and return code -1. `close()` stops the shared proxy, so ownership must be clear.

## Test Signals
Translator tests should verify request packing, response unpacking with missing fields, exception conversion, method-support lookup, and proxy close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/GenericRefreshProtocolClientSideTranslatorPB.java -->
