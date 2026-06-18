# sources/cloud-native/containerd/api/services/mounts/v1/mounts.proto

## Purpose

This proto file defines the Mounts service contract for managing named mount activations in containerd.

## Important APIs, Types, and Functions

The `Mounts` service has unary RPCs `Activate`, `Deactivate`, `Info`, and `Update`, plus server-streaming `List`. `ActivateRequest` contains `name`, repeated `containerd.types.Mount`, labels, and `temporary`. `ActivateResponse`, `InfoResponse`, `UpdateRequest`, `UpdateResponse`, and `ListMessage` all carry `containerd.types.ActivationInfo` where appropriate. `UpdateRequest` includes a `FieldMask`.

## Control Flow

Clients activate a named set of mount instructions, inspect activation info, update selected activation metadata, list activation info records as a stream, and deactivate by name. `List` streams one `ListMessage` per activation matching optional filters.

## State and Persistence Behavior

The schema models named activation state. It does not specify the backing store or lifecycle policy. `temporary` differentiates activations that service logic may clean up differently. Labels and update masks provide mutable metadata. Mount details are delegated to the shared `types/mount.proto` contract.

## Dependencies and Integration Points

Imports are `google.protobuf.Empty`, `FieldMask`, and `types/mount.proto`. Generated Go package is `github.com/containerd/containerd/api/services/mounts/v1;mounts`. Integrations include mount lifecycle managers, activation metadata, gRPC/ttrpc streaming clients, and filter processing.

## Risks and Test Signals

Risks include resource leaks on failed deactivation, inconsistent treatment of temporary mounts, stream cancellation handling, filter mismatches, and update masks that overwrite unintended metadata. Tests should cover activation/deactivation lifecycle, info lookups, update masks, streaming list with cancellation, filters, and cleanup of temporary activations.
