# sources/cloud-native/moby/daemon/daemon_test.go

## Purpose
Provides cross-platform unit coverage for daemon helpers: container lookup, valid name patterns, loading old DNS config, image/user config merge, isolation and port validation, network error typing, ULA derivation, and symlinked directory resolution.

## Important APIs, Types, And Functions
- `TestGetContainer` validates lookup precedence between full IDs, partial IDs, full names, ambiguous prefixes, and missing values.
- `initDaemonWithVolumeStore` creates a minimal daemon with a volume service.
- `TestContainerInitDNS` loads old JSON metadata and ensures DNS slices are initialized.
- `TestMerge` verifies image config merge semantics for ports, env, and volumes.
- `TestValidateContainerIsolation`, `TestInvalidContainerPort0`, and `TestFindNetworkErrorType` validate API-facing errors.
- `TestDeriveULABaseNetwork` checks deterministic RFC4193-style ULA prefix derivation.
- Symlink tests validate `resolveSymlinkedDirectory`.

## Control Flow
Tests construct minimal container stores and view DBs, reserve names, call daemon helpers, and assert exact results or error categories. Filesystem tests create temporary config files or symlinks and then invoke loader/path resolution code.

## State And Persistence
Temporary directories hold container metadata and symlink targets. In-memory stores simulate daemon state. Root-required DNS loading test may mutate file ownership and skips without root.

## Dependencies And Integration Points
Exercises container memory store, container view DB, volume service, network/libnetwork errors, config merge logic from image metadata, and host filesystem symlink behavior.

## Risks And Edge Cases
Some tests skip or need porting on Windows. The old JSON fixture covers migration shape for one legacy container but cannot cover all historical metadata variants.

## Test Signals
Failures flag user-visible regressions in `docker inspect`/lookup behavior, name validation, config inheritance, invalid API error typing, network router expectations, or root directory canonicalization.
