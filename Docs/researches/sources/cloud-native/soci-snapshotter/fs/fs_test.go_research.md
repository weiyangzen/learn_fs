# sources/cloud-native/soci-snapshotter/fs/fs_test.go

Purpose: unit-tests the filesystem `Check` path that validates or refreshes a mounted lazy layer connection.

Important APIs and flow: `TestCheck` creates a `filesystem` with a single fake `breakableLayer` registered at mountpoint `test` and default source resolver wiring. It sets `success=true` and expects `fs.Check` to pass, then sets `success=false` and expects failure. `breakableLayer` implements the `layer.Layer` interface with simple success-controlled `Check` and `Refresh` methods plus stubbed mount/read APIs.

State and persistence: in-memory fake filesystem map only. No FUSE server, remote registry, content store, or mountpoint is touched.

Dependencies and integration: validates the `filesystem.Check` behavior against the `layer.Layer` interface contract. The fake `Info` reports `Size: 1` and default `FetchedSize: 0`, forcing the connectivity check path.

Risks and test signals: confirms the basic branch that skips fully fetched layers is not used and that layer check errors propagate. It does not cover retry across multiple sources, refresh success after initial failure, labels parsing, or behavior when no layer is registered.
