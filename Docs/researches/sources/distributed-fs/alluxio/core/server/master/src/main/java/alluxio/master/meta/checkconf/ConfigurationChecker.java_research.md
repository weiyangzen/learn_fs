# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationChecker.java

## Purpose
`ConfigurationChecker` compares server-side configuration reported by masters and workers, classifies inconsistencies as warnings or errors according to each `PropertyKey` consistency level, and exposes a cached `ConfigCheckReport`.

## Important APIs and Types
- Holds master and worker `ConfigurationStore` instances.
- Maintains `ConfigCheckReport mConfigCheckReport` and volatile dirty flag.
- Registers change listeners on both stores to set the dirty flag.
- `getConfigCheckReport()` lazily regenerates when dirty.
- `regenerateReport()` builds maps of `PropertyKey -> Optional<value> -> node addresses`.
- `logConfigReport()` logs status-specific summaries, limiting output volume.

## Control Flow
When stores change, the dirty flag is set. On `getConfigCheckReport`, the method clears the dirty flag before regeneration so concurrent changes during regeneration cause a later refresh. Regeneration merges live master and worker configs, skips keys with `ConsistencyCheckLevel.IGNORE`, treats keys with multiple distinct values as inconsistent, maps `Scope.ALL` to `Scope.SERVER`, and chooses status `FAILED`, `WARN`, or `PASSED`.

## State and Persistence
The checker keeps an in-memory cached report. Configuration inputs come from `ConfigurationStore`; no journal persistence is performed here.

## Dependencies and Integration Points
Depends on `PropertyKey`, `Scope`, `ConfigStatus`, `ConfigCheckReport`, and `InconsistentProperty`. It feeds web UI and `fsadmin doctor` style diagnostics through the meta master.

## Risks and Edge Cases
- `logConfigReport` compares against the previous report status before replacing it; transitions are logged, but unchanged bad states are not repeatedly logged.
- Address strings use host:rpcPort, so duplicate addresses would collapse at store level.
- Unknown/unregistered keys can still participate if their `PropertyKey` consistency level is not ignore.
- All public methods are synchronized; report generation can block concurrent readers.

## Test Signals
Tests should cover passed/warn/failed status derivation, ignore-level filtering, `Scope.ALL` remapping, dirty flag lazy regeneration, limited logging, and live-node filtering through stores.
