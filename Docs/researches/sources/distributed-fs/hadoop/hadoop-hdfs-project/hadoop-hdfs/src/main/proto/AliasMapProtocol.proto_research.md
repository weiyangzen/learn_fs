# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/AliasMapProtocol.proto

## Purpose

`AliasMapProtocol.proto` defines the protobuf RPC contract for the HDFS alias map, which maps HDFS blocks to provided-storage locations. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `AliasMapProtocolProtos`, generic services, and imports `hdfs.proto`. Data messages include `KeyValueProto` (`BlockProto` key and `ProvidedStorageLocationProto` value), `WriteRequestProto`, `WriteResponseProto`, `ReadRequestProto`, `ReadResponseProto`, `ListRequestProto`, `ListResponseProto`, `BlockPoolRequestProto`, and `BlockPoolResponseProto`. The service `AliasMapProtocolService` exposes `write`, `read`, `list`, and `getBlockPoolId`.

## Control Flow

The protocol models a simple key/value service. Clients write a block-to-location pair, read by block key, list from an optional marker for pagination, and fetch the block pool ID. `nextMarker` in `ListResponseProto` is the continuation state for list traversal.

## State and Persistence Behavior

The proto itself has no state, but it describes persistent alias map entries used by provided storage. Implementations must persist `BlockProto -> ProvidedStorageLocationProto` mappings consistently with the namespace/block pool they serve.

## Dependencies and Integration Points

It depends on common HDFS block and provided-storage message definitions from `hdfs.proto`. Generated Java is consumed by alias map RPC translators, server implementations, and clients that resolve externally provided block storage locations.

## Risks and Edge Cases

Because this is a stable RPC contract, field numbers and required/optional semantics are compatibility-sensitive. `ReadResponseProto.value` is optional, so callers must distinguish not-found from an empty or missing location. Pagination depends on correct marker ordering and block-pool consistency.

## Test Signals

Tests should cover write/read round trips, not-found reads, list pagination with and without markers, block-pool ID validation, generated protobuf compatibility, and rolling-upgrade behavior when optional fields are absent.
