# sources/cloud-native/moby/daemon/cluster/convert/container.go

## Purpose
Converts Docker swarm container specs between Docker API types and swarmkit gRPC types, including DNS, privileges, mounts, secrets/configs, healthchecks, resources-adjacent fields, and platform isolation.

## Important APIs, Types, And Functions
Key functions include `containerSpecFromGRPC`, `containerToGRPC`, `initFromGRPC`, `initToGRPC`, secret/config reference converters, credential spec converters, healthcheck converters, `IsolationFromGRPC`, `isolationToGRPC`, ulimit converters, and tmpfs option JSON shims.

## Control Flow
Inbound conversion copies scalar fields, best-effort parses DNS IPs, expands privileges, converts mount option substructures, durations, and healthcheck. Outbound conversion validates config reference oneofs, credential spec exclusivity, enum values for mount type/propagation, and serializes tmpfs options into swarmkit's string field.

## State And Persistence
No local state. It preserves API-visible configuration crossing the Docker API/swarmkit raft boundary. Tmpfs options are persisted as JSON strings in swarmkit.

## Dependencies And Integration Points
Used by service/task conversion and executor container creation. Depends on Docker container/mount/swarm types, swarmkit API enums, netip, gogo wrappers, and logging for unsupported inbound targets.

## Risks And Test Signals
Invalid inbound IP strings become zero values because parsing errors are ignored after storage. Outbound validation prevents ambiguous config and credential specs. Tests cover tmpfs JSON conversion; service tests cover credential specs, config targets, isolation, and volume subpath.
