# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/fsopts/fsopts.go

Purpose: Builds filesystem options for the snapshotter daemon and FUSE manager from runtime configuration.

Important APIs: `Config`, `ConfigFsOpts`, and `getMetadataStore`. Config fields enable IPFS, choose metadata store type, and inject a bbolt opener.

Control flow: `ConfigFsOpts` starts with metrics log level, optionally registers an IPFS resolve handler for the `ipfs` scheme, resolves a metadata store, and returns `fs.Option` values. `getMetadataStore` returns the in-memory metadata reader by default or constructs a DB-backed store that reuses a bbolt DB at `<rootDir>/metadata.db`.

State and persistence: No state retained here. DB mode persists metadata in the configured root directory via the supplied `OpenBoltDB`.

Dependencies and integration: Used by `containerd-stargz-grpc/main.go` and `stargz-fuse-manager/main.go`. Connects `fs`, `metadata/memory`, `cmd/.../db`, bbolt, and IPFS resolver integration.

Risks: DB mode requires `OpenBoltDB`; missing opener is a configuration error. Unknown metadata store values are rejected. The function does not close the opened DB; lifecycle is owned by process-level service code.

Test signals: No direct test in this subset; behavior is exercised through daemon configuration/integration.
