# sources/cloud-native/containerd/api/services/sandbox/v1/sandbox.proto

## Purpose

This proto defines containerd's v1 sandbox services. It separates durable sandbox metadata from runtime sandbox instance control so containerd can support shared lifecycle/resource environments such as Kubernetes pause-container groups or VM-backed container sandboxes without baking a runtime implementation into the core API.

## Important APIs, Types, and Functions

`service Store` provides metadata CRUD: `Create`, `Update`, `Delete`, `List`, and `Get`. Store requests use `containerd.types.Sandbox`; list accepts containerd-style filter strings; update accepts field names for partial mutation. `service Controller` manages runtime instances: `Create`, `Start`, `Platform`, `Stop`, `Wait`, `Status`, `Shutdown`, `Metrics`, and `Update`. Runtime requests use `sandbox_id` plus a `sandboxer` selector, with create accepting rootfs mounts, opaque `Any` options, a network namespace path, annotations, and the sandbox metadata object. Start/status responses expose pid, timestamps, labels/info, endpoint address, version, and opaque spec/extra data.

## Control Flow

Expected lifecycle is metadata create/update/list/get through `Store`, then runtime `Controller.Create`, `Start`, `Status`, `Wait`, `Stop` or `Shutdown`, with optional `Metrics`, `Platform`, and `Update`. The API is unary; wait is also unary and returns after sandbox exit.

## State and Persistence Behavior

Store objects are explicitly metadata only and contain enough information to create a future runtime instance, not live state. Live state is returned by controller calls and includes pid, state text, timestamps, endpoint address, version, and metrics. Runtime-specific configuration and status extensions are delegated through `Any`.

## Dependencies and Integration Points

The proto imports containerd type protos for sandbox, mount, platform, and metrics, plus protobuf `Any` and `Timestamp`. It is the source for Go protobuf, gRPC, and ttrpc bindings.

## Risks

The contract is extension-oriented, so mismatched `Any` payload schemas or ambiguous `sandboxer` routing can cause runtime-specific failures. Status `state` and info maps are weakly typed. Controller updates rely on callers and implementations agreeing on field-path names.

## Test Signals

Tests should cover store CRUD filters, lifecycle transitions, sandboxer selection, `Any` option compatibility, address/version propagation, metrics availability, and partial update behavior.
