# sources/cloud-native/moby/daemon/server/router/container/inspect.go

## Purpose
`inspect.go` serializes container inspection responses while preserving old Docker API response shapes.

## Important APIs, Types, And Functions
`getContainersByName` calls `ContainerInspect` with size options, mutates response fields for older API versions, and uses `compat.Wrap` to inject removed legacy fields.

## Control Flow
The handler parses query fields, obtains inspection data plus a desired MAC address from the backend, then applies version gates. Before API 1.45 it appends short container ID and hostname aliases to user-defined network endpoints. Before API 1.48 it hides `ImageManifestDescriptor`. Before API 1.52 it injects bridge endpoint data into top-level `NetworkSettings`, restores legacy `Config.MacAddress`, and maps snapshotter `Storage.RootFS.Snapshot.Name` back into `GraphDriver`.

## State And Persistence
Only the response object is mutated. The daemon's stored container configuration is not persisted by this handler.

## Dependencies And Integration Points
The file depends on API container/storage types, `compat`, version helpers, `stringid`, `sliceutil`, and backend inspect options. It is part of the container router's GET `/containers/{name}/json` path.

## Risks
Because the code mutates the inspect object before writing it, accidental reuse of backend-owned objects could leak legacy-only fields. Version gates are dense and tied to public API compatibility.

## Test Signals
The neighboring container route compatibility tests cover related MAC migration logic; integration tests typically validate inspect response compatibility across API versions.
