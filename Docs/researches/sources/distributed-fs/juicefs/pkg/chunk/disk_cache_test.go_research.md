## sources/distributed-fs/juicefs/pkg/chunk/disk_cache_test.go

Purpose: tests disk cache store creation, metrics, scanning, checksum validation, staging accounting, path expansion, and platform-sensitive cache behavior.

Important tests and helpers: `toFloat64` reads Prometheus collectors. `testConf` creates unique temp cache dirs. Tests instantiate cache stores/managers, write cache pages, inspect metrics counters/gauges, stage and remove staging files, scan raw cache directories, validate checksum modes and corrupted data behavior, and exercise cache manager path/glob handling. Mocking libraries are imported for targeted filesystem/metric scenarios.

State and persistence: creates real temporary cache directory structures under raw/staging paths and writes cache files with optional checksums.

Dependencies and integration points: depends on Prometheus metric internals, `fastwalk`/filesystem layout, `utils.RandRead`, `testify/require`, GoConvey, and Mockey.

Risks and test signals: robust for disk-format regressions, but async cache flushes use sleeps. Tests involving corruption/checksum mode are important because disk cache correctness is otherwise silent until bad data is returned.
