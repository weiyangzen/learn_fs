# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/FederationProtocolPBTranslator.java

Purpose: Shared helper for PB protocol implementations that manages the mutable builder/proto lifecycle and base64 protobuf deserialization.

Important APIs/types/functions: generic over protobuf message `P`, builder `B`, and proto-or-builder `T`; methods include constructor, `setProto`, `getBuilder`, `getProtoOrBuilder`, `build`, and `readInstance`.

Control flow: `setProto` validates the incoming `Message` type and stores it as the current proto. `getBuilder` lazily creates a builder from either the default instance or current proto and marks the wrapper as builder-backed. `build` materializes the builder into a proto. `getProtoOrBuilder` returns the builder when dirty or the built proto otherwise. `readInstance` base64-decodes text and reflectively invokes `parseFrom(byte[])` on the proto class.

State/persistence behavior: holds transient in-memory protobuf state only. It is the consistency layer that lets PBImpl objects alternate between immutable parsed protos and mutable builders before serialization.

Dependencies/integration: used by every `store.protocol.impl.pb` class and depends on Hadoop's shaded protobuf `GeneratedMessageV3`, commons-codec base64, and reflection.

Risks: reflection failures surface as `IOException`; an incorrect proto class passed to `setProto` is rejected at runtime; builder/proto dirty-state mistakes would lose field updates; base64 parse compatibility depends on protobuf schema evolution.

Test signals: translator tests should cover empty builder creation, seeded proto mutation, type rejection, base64 parse errors, dirty build behavior, and representative PBImpl round trips.
