# sources/cloud-native/containerd/plugins/diff/windows/windows.go

## Purpose
Implements the standard Windows container layer diff plugin for applying and comparing WCOW layers.

## Important APIs, Types, And Functions
Registers the `windows` diff plugin. `windowsDiff.Apply` applies a tar layer to a Windows layer. `windowsDiff.Compare` writes layer diffs to the content store. `mountsToLayerAndParents` and `mountPairToLayerStack` validate Windows layer relationships. `readCounter` and `uniqueRef` support streaming and ingest.

## Control Flow
Apply validates a single `windows-layer` mount, enables backup/restore privileges, unwraps content processors to OCI tar, hashes/counts data, applies with Windows layer archive options and parent layers, drains trailing data, and returns a descriptor. Compare validates lower/upper stack relationship, enables backup privilege, writes a compressed or uncompressed Windows layer diff to a content writer, commits it, repairs missing uncompressed labels, and logs timing.

## State And Persistence
Apply mutates the target Windows layer directory. Compare persists content blobs and labels. It may alter process privileges for the daemon process.

## Dependencies And Integration Points
Windows-only. Uses go-winio privileges, archive Windows layer options, content store, mount parent metadata, compression, labels, and errdefs. The diff service tries this before LCOW on Windows.

## Risks
Process privilege changes are global and not ref-counted. Layer-stack validation must be strict to avoid invalid parent diffs. Non-Windows mount types intentionally return `ErrNotImplemented` to allow LCOW fallback.

## Test Signals
No direct tests in this subset. Windows integration tests are required for meaningful coverage.
