<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/proto/FederationProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/proto/FederationProtocol.proto

## Purpose
Core protobuf schema for HDFS Router-based federation State Store records and protocol messages.

## APIs, Types, and Functions
Defines `HdfsServerFederationProtos` in package `hadoop.hdfs`, importing `hdfs.proto`. Major messages include membership stats, membership records, namespace info, mount table records, remote locations, router records, state-store version, heartbeat requests/responses, cache refresh, safe mode, disabled nameservice, and mount-table CRUD requests/responses.

## Control Flow, State, and Persistence
The schema is the serialization contract for persisted State Store records and transient federation/admin RPCs. Record messages carry timestamps and primary-key fields used by Java `BaseRecord` subclasses. Request/response messages wrap records or simple keys/status booleans for generated RPC translators.

## Dependencies and Integration
Used by all PB implementations in `store.protocol.impl.pb` and `store.records.impl.pb`, and imported by `RouterProtocol.proto`. Generated Java classes are referenced throughout Router admin, state-store, heartbeat, and resolver code.

## Risks and Test Signals
Proto2 optional defaults can hide missing fields as empty strings, zeroes, or false booleans. Field-number compatibility is critical for persisted records. Tests should include PB round trips, rolling-upgrade/backward-compatibility checks, State Store driver persistence, and admin RPC compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/proto/FederationProtocol.proto -->
