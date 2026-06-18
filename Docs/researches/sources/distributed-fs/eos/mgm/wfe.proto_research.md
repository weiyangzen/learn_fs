# sources/distributed-fs/eos/mgm/wfe.proto

## Purpose
Defines the legacy protobuf schema for EOS workflow notifications, including workflow metadata, client identity, file/directory metadata, and transport URL.

## Important APIs, types, and functions
Messages are `id`, `checksum`, `clock`, `md`, `security`, `client`, `service`, `workflow`, and `notification`. `md` captures ids, timestamps, ownership, size, checksum, mode, logical path, and xattrs. `workflow` captures event, queue, workflow name, virtual path, service instance, and timestamp.

## Control flow
The schema is a data contract rather than executable code. Producers populate `notification` messages with workflow, client, file, and directory context; consumers read the same fields to act on workflow events.

## State and persistence behavior
Serialized protobuf messages are transient workflow payloads. No storage is defined here, but field numbers are part of the compatibility contract.

## Dependencies and integration points
Uses proto3 and package `eos.wfe`. It relates to WFE notification/proto flows, although `WFE.cc` also uses CTA and RPC protobuf types from other generated schemas.

## Risks and test signals
Message and field names are lowercase, which can be awkward for generated APIs but is wire-compatible. Tests should cover JSON/binary serialization compatibility, xattr map preservation, timestamp precision, and old/new consumer tolerance when fields are absent.
