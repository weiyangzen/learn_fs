# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/AlluxioMasterRestServiceHandler.java

## Purpose
`AlluxioMasterRestServiceHandler` is the JAX-RS REST and web-UI data handler for the master process. It serves general master info, overview, browse, logs, configuration, workers, masters, mount table, metrics, and log-level updates.

## Important APIs, types, and functions
Endpoints include `GET /master/info`, `webui_init`, `webui_overview`, `webui_browse`, `webui_data`, `webui_logs`, `webui_config`, `webui_workers`, `webui_masters`, `webui_mounttable`, `webui_metrics`, and `POST /master/logLevel`. Internal helpers compute capacity, configuration, metrics, mount points, tier capacity, and UFS capacity. `isMounted(String)` filters per-UFS metrics to currently mounted UFS URIs.

## Control flow
The constructor retrieves `AlluxioMasterProcess`, `BlockMaster`, `FileSystemMaster`, `MetaMaster`, and a filesystem client from servlet context. Endpoints wrap work in `RestUtils.call`. Overview composes cluster capacity, config check status, storage tiers, root UFS capacity, journal warnings, checkpoint warnings, Raft role, leader id, and system status gauges. Browse resolves paths, handles file preview and directory listing with pagination. Logs list allowed log filenames or read a 5 KB window from a selected log file. Metrics combines gauges/counters, cache-hit estimates, per-UFS metrics filtered by mounts, time-series metrics, and journal disk metrics.

## State and persistence behavior
The handler does not persist state. It reads live master state, metrics, configuration, filesystem metadata, and log files. `logLevel` mutates runtime logging level. Browse and data endpoints may set `AuthenticatedClientUser` to the server user when security is enabled and no user is present.

## Dependencies and integration points
It depends on master process services, block/file/meta masters, file-system client APIs, metrics registry, web UI wire objects, configuration, security utilities, path utilities, and JAX-RS/Swagger annotations. It is mounted by `MasterWebServer`.

## Risks
Many metrics are assumed present and cast to specific types; missing gauges/counters can cause runtime failures. Browse/data pagination validates parse and arithmetic but still uses list materialization, which can be expensive. Log reading protects against arbitrary paths by taking only `new File(requestFile).getName()`, but log-level changes are powerful runtime operations. Some security code sets authenticated user without obvious cleanup in these endpoint lambdas.

## Test signals
Tests should cover each endpoint response shape, disabled `WEB_FILE_INFO_ENABLED`, browse file and directory modes, pagination errors, log filename sanitization, missing metrics behavior, mounted-UFS metric filtering, journal warning population, security user context handling, and log-level mutation.
