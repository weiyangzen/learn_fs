# sources/cloud-native/containerd/api/services/snapshots/v1/snapshots.proto

## Purpose

This proto defines containerd's v1 snapshot management service. It is the RPC contract for creating active snapshots, creating read-only views, committing snapshots, removing them, querying metadata and usage, listing snapshots, and requesting cleanup in a named snapshotter.

## Important APIs, Types, and Functions

`service Snapshots` exposes `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Stat`, `Update`, server-streaming `List`, `Usage`, and `Cleanup`. `PrepareSnapshotRequest` and `ViewSnapshotRequest` select `snapshotter`, `key`, optional `parent`, and labels. `CommitSnapshotRequest` commits an active key to a name with labels and parent. `Info` describes snapshots with `Kind` (`UNKNOWN`, `VIEW`, `ACTIVE`, `COMMITTED`), timestamps, and labels. `UpdateSnapshotRequest` uses `google.protobuf.FieldMask`; `ListSnapshotsRequest` uses containerd filter syntax; `UsageResponse` reports size and inodes.

## Control Flow

Typical flow is `Prepare` or `View` to obtain mounts, container or caller uses mounts, then `Commit` for active snapshots or `Remove` for disposable keys. Clients call `Stat`, `Update`, `List`, and `Usage` for metadata/maintenance, and `Cleanup` to ask the snapshotter to remove stale internal resources.

## State and Persistence Behavior

Snapshot state is held by the selected snapshotter. The proto distinguishes active, view, and committed snapshots, tracks parent linkage, and stores mutable labels/timestamps. The update mask limits mutation; name, parent, kind, and creation time are documented immutable.

## Dependencies and Integration Points

The schema imports containerd mount types and protobuf empty, field mask, and timestamp types. It is generated into Go protobuf, gRPC, and ttrpc bindings and integrates with snapshotter backends.

## Risks

Filter syntax is string-based and must match containerd filter rules. Label size constraints must be enforced by servers. Streaming `List` can return batches, so clients must drain until EOF. Empty update masks mutate all mutable fields.

## Test Signals

Tests should cover prepare/view/commit/remove lifecycle, parent metadata, immutable field rejection, update mask semantics, list filters, usage accuracy, cleanup idempotency, and labels at or above size limits.
