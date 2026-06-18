# sources/cloud-native/moby/daemon/reload.go

## Purpose
Implements daemon configuration reload with a transaction-like two-phase model. It updates live daemon settings such as debug, registry config, concurrency limits, labels, live restore, features, network diagnostics, NRI, and platform-specific runtime settings.

## Important APIs, Types, And Functions
`reloadTxn` records commit and rollback callbacks. `Daemon.Reload` orchestrates reload hooks. Hook functions include `reloadDebug`, `reloadMaxConcurrentDownloadsAndUploads`, `reloadMaxDownloadAttempts`, `reloadShutdownTimeout`, `reloadLabels`, `reloadRegistryConfig`, `reloadLiveRestore`, `reloadNetworkDiagnosticPort`, `reloadFeatures`, and `reloadNRI`. `marshalAttributeSlice` formats event attributes.

## Control Flow
`Reload` locks `configReload`, deep-copies current config using `copystructure`, builds `newCfg`, runs each hook against the copy, and aborts with rollback callbacks on the first error. On success it stores the new config, commits side effects, and logs a daemon reload event with attributes. Hooks apply "only if value set" semantics for many fields and register side effects such as image service config updates, registry service replacement, diagnostic start/stop, and NRI reload commit.

## State And Persistence
Live config is atomically swapped through `daemon.configStore.Store(newCfg)` only after all prepare hooks succeed. Commit callbacks then mutate auxiliary services. The `init` function registers a custom `copystructure` copier for `netip.Addr` so DNS/host gateway addresses survive reload copying.

## Dependencies And Integration Points
Integrates with daemon config parsing, registry service `ReplaceConfig`, image service, network controller diagnostics, NRI, event logging, and platform hooks in `reload_unix.go`/`reload_windows.go`.

## Risks And Edge Cases
The intended rollback design is important for fallible hooks; as written, `OnRollback` appends callbacks to `tx.onCommit` rather than `tx.onRollback`, so rollback callbacks would not run through `Rollback`. Commit errors are returned after config is already stored and reload event is logged. Copying relies on `copystructure`, including the custom `netip.Addr` copier to avoid zero-value addresses.

## Test Signals
`reload_test.go` covers labels, mirrors, insecure registries, preserving unrelated settings, network diagnostic toggling, DNS address preservation, and the custom `netip.Addr` copier.
