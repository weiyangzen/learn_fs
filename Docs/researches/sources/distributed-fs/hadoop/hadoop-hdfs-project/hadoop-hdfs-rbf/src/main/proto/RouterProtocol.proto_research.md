<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/proto/RouterProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/proto/RouterProtocol.proto

## Purpose
Protobuf RPC service definition for Router admin operations.

## APIs, Types, and Functions
Defines `RouterProtocolProtos` in `hadoop.hdfs.router` and imports `FederationProtocol.proto`. `RouterAdminProtocolService` exposes RPCs for add/update/remove/addAll/get mount table entries, safe mode enter/leave/get, nameservice disable/enable/list, mount table cache refresh, destination lookup, and superuser proxy group refresh.

## Control Flow, State, and Persistence
The service binds CLI/client manager calls to server-side Router admin handlers. Request/response messages are defined in `FederationProtocol.proto`; server handlers mutate State Store records, Router safe-mode state, disabled nameservice records, or in-memory caches depending on the RPC.

## Dependencies and Integration
Generated protocol classes are used by Router admin client-side and server-side translators. It integrates with `RouterAdmin`, `RouterAdminServer`, `MountTableManager`, `RouterStateManager`, and `NameserviceManager`.

## Risks and Test Signals
Adding or changing RPCs affects wire compatibility and translator implementations. Tests should cover client/server translator round trips and each admin operation through the protobuf service, not only direct Java manager calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/proto/RouterProtocol.proto -->
