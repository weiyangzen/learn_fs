# sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2.py

## Purpose
This generated protobuf module defines the instance-manager proxy engine API, which forwards engine operations such as volume control, snapshots, backups/restores, replica rebuilds, metrics, and remounts through a proxy service.

## Important APIs, types, and functions
- Core selector: `ProxyEngineRequest` carries engine address, engine name, volume name, backend-store driver, and data engine.
- Volume messages include version/get responses, expand requests, frontend start requests, snapshot requests/responses, unmap mark, max snapshot count/size setters.
- Snapshot messages include list response, `EngineSnapshotDiskInfo`, revert/purge/purge-status, clone/clone-status, remove, hash/hash-status, backup/backup-status.
- Restore messages include backup restore request/response/status and finish request.
- Replica messages include add/list/verify-rebuild/rebuild-status/remove/mode-update.
- Other messages include metrics get response and `RemountVolumeRequest`.
- Imports generated `ptypes.controller_pb2`, `ptypes.syncagent_pb2`, and shared `imrpc.common_pb2`.

## Control flow
The module performs generated protobuf import-time setup: registers the serialized `imrpc/proxy.proto` descriptor, builds message classes, map-entry descriptors, and serialized options. There is no handwritten logic.

## State and persistence behavior
It stores no external state, but message classes represent high-impact remote state transitions: volume expansion/frontend lifecycle, snapshot graph mutation, backup/restore task state, replica membership/modes, rebuild status, and metrics. Descriptor registration mutates the in-process protobuf registry.

## Dependencies and integration points
Depends on protobuf runtime, `empty_pb2`, Longhorn controller/sync-agent protobuf types, and shared `imrpc.common_pb2`. It is consumed by the generated proxy gRPC companion and any proxy clients that need to drive engine operations through instance-manager rather than connecting directly to controllers.

## Risks and edge cases
- The module is large and generated; manual edits are brittle and should be replaced by `.proto` regeneration.
- Some fields preserve compatibility concerns, including deprecated backend-store-driver usage and data-engine routing.
- Many request messages wrap ptypes controller requests; API drift in imported `ptypes` modules can break proxy serialization.
- Backup/restore status includes raw task errors and map statuses, so callers must handle partial per-replica failure states.

## Test signals
Signals include import success, construction/serialization of proxy requests, compatibility with `proxy_pb2_grpc` serializers, and higher-level tests that exercise snapshot, backup/restore, replica add/rebuild, expansion, metrics, and remount operations through proxy services.
