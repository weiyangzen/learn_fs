## sources/cloud-native/soci-snapshotter/config/defaults.go

Purpose: centralizes default constants for root, service, filesystem, blob, HTTP retry, content store, pull mode, and parallel pull settings.

Important APIs/types/functions: constants such as `defaultMetricsNetwork`, `DefaultImageServiceAddress`, `Unbounded`, `defaultMaxConcurrency`, `DefaultContentStoreType`, `DefaultSOCIV1Enable`, `DefaultSOCIV2Enable`, and parallel limit defaults.

Control flow: no executable logic; parser files consume these constants to fill zero-value configuration.

State and persistence: none directly.

Dependencies and integration: used throughout config parser and tests.

Risks and test signals: comments note experimental GC edge cases for parallel-pull fallback. Defaults can diverge from sample config if not kept in sync; tests assert many constant-to-config relationships.
