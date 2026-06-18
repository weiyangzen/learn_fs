# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/TraceAdmin.proto

## Purpose
`TraceAdmin.proto` defines the protobuf RPC contract for administering Hadoop tracing span receivers. It supports listing, adding, and removing receivers at runtime.

## Important APIs, types, and functions
Messages include empty `ListSpanReceiversRequestProto`, `SpanReceiverListInfo` with required `id` and `className`, `ListSpanReceiversResponseProto`, `ConfigPair`, `AddSpanReceiverRequestProto` with class name and config pairs, `AddSpanReceiverResponseProto` with receiver id, `RemoveSpanReceiverRequestProto` with id, and empty `RemoveSpanReceiverResponseProto`. The service `TraceAdminService` exposes `listSpanReceivers`, `addSpanReceiver`, and `removeSpanReceiver`.

## Control flow
An admin client lists existing receivers, requests construction of a receiver class with config key/value pairs, or removes a receiver by id. Server-side tracing code performs class loading and registry updates.

## State and persistence
The proto captures one admin operation. Runtime receiver registry state changes on add/remove. Persistence of receiver configuration, if any, is outside this schema.

## Dependencies and integration points
It generates `org.apache.hadoop.tracing.TraceAdminPB` and integrates with Hadoop tracing admin CLI, tracing subsystem, and RPC protocol translators.

## Risks and test signals
Risks include unsafe class loading from user-supplied class names, leaking configuration values, id collisions, removing active receivers, and authorization gaps. Test signals include trace admin protocol tests, add/remove/list lifecycle tests, invalid class/config handling, and admin authorization checks.
