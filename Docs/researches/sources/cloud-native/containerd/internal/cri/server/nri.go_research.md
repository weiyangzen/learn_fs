
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri.go -->
# sources/cloud-native/containerd/internal/cri/server/nri.go

## Purpose

This file adapts `criService` to the internal NRI implementation interface by exposing CRI configuration, stores, metadata extension keys, and sandbox metadata access.

## Important APIs, Types, and Functions

It defines `criImplementation` with methods `Config`, `SandboxStore`, `ContainerStore`, `ContainerMetadataExtensionKey`, and `SandboxMetadataStore`.

## Control Flow

Every method is a direct accessor over the embedded `*criService`. `Config` returns the address of the service config. Store accessors return sandbox/container stores and the containerd sandbox metadata store. The metadata extension key returns the CRI labels constant for container metadata.

## State and Persistence Behavior

The adapter does not mutate state itself. It hands NRI access to live service stores and config, so callers can read or mutate through those returned objects depending on their APIs.

## Dependencies and Integration Points

Dependencies include containerd sandbox store interfaces, CRI config, CRI labels, and CRI container/sandbox stores. This adapter is used by NRI integration code to interact with CRI-managed state without depending directly on the full `criService` type.

## Risks and Edge Cases

Returning a pointer to `criService.config` exposes mutable configuration to interface consumers. Store access must respect the stores' concurrency contracts. Interface expansion requires platform-specific methods such as the Linux file's resource-update and stop-container hooks.

## Test Signals

Useful tests would assert that accessors return the exact service stores/config and correct metadata extension key, and that NRI callers can use the adapter without data races.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri.go -->
