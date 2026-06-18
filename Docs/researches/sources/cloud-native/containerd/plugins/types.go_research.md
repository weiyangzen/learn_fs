<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/types.go -->
# sources/cloud-native/containerd/plugins/types.go

## Purpose
Defines containerd's internal plugin type strings, common plugin IDs, property keys, and export keys.

## Important APIs, Types, And Functions
Constants include plugin types for internal, runtime v1/v2, service, GRPC, TTRPC, snapshotter, diff, metadata, content, GC, events, leases, streaming, tracing, metrics, NRI, transfer, sandbox, image verifier, warning, CRI, shim, HTTP, server, mount manager, and mount handler. Also defines `RuntimeRuncV2`, `RuntimeRunhcsV1`, `DeprecationsPlugin`, root/state/GRPC/TTRPC property keys, and `SnapshotterRootDir`.

## Control Flow
No runtime logic; constants are imported by plugin registrations throughout containerd.

## State And Persistence
No state. String values become part of plugin identity, configuration, metadata, and compatibility contracts.

## Dependencies And Integration Points
Depends only on `github.com/containerd/plugin`. Used by snapshotter, streaming, transfer, and many other plugin packages.

## Risks And Edge Cases
Changing any string breaks plugin registration, config lookup, exported metadata, or external assumptions. The package comment warns external plugins to copy these types rather than import this internal package.

## Test Signals
No file-local tests. Stability is enforced by widespread compile-time use and runtime plugin registration behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/types.go -->
