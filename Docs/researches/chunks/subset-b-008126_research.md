# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/db.json lines 1-9035

## Chunk Scope

This chunk covers the mock Recon web API database from the beginning of `db.json` through line 9035. It includes every top-level fixture from `clusterState` through the beginning of the standalone `DatanodesDecommissionInfo` response. The physical source file continues to line 9230 with the rest of `DatanodesDecommissionInfo`, `datanodesRemove`, `utilization`, and pending-deletion summaries, so this chunk should be merged with the following chunk before producing a final whole-file report.

## Purpose

`db.json` is not executable application code; it is the data backing the Recon UI mock API server. The web app's `package.json` runs `json-server --watch api/db.json --routes api/routes.json --middlewares api/pagination.js --port 9888`, so each top-level JSON key acts like a resource table or endpoint response. `api/routes.json` maps real-looking Recon paths such as `/api/v1/clusterState`, `/api/v1/datanodes`, `/api/v1/containers/unhealthy/MISSING*`, `/api/v1/namespace/usage?...`, `/api/v1/keys/open/summary`, and `/api/v1/datanodes/decommission/info` onto these top-level keys.

The fixtures provide broad UI coverage for Overview, Datanodes, Pipelines, Namespace, Containers, Volumes/Buckets, Heatmap, Open/Delete Pending Keys, Container Mismatch, Decommissioning, and Capacity views. They intentionally include normal records, empty responses, pagination cursors, large numeric identifiers, negative sentinel values, nulls, and count/data mismatches to exercise client rendering behavior.

## Important Data APIs and Shapes

The top-level resources visible in this chunk include:

- `clusterState`: summary counts for pipelines, datanodes, storage, containers, volumes, buckets, keys, deletion backlog, and SCM/OM service IDs.
- `datanodes`: `{ totalCount, datanodes }` with 19 datanode rows. Rows include host/UUID, health `state`, operational `opState`, heartbeat/setup timestamps, storage reports, pipeline summaries, container/open-container counts, leader counts, version, revision, and build date.
- `pipelines`: `{ totalCount, pipelines }` with 3 pipeline rows. Pipeline rows include id, status, leader, datanode network details and ports, election timing, replication type/factor, and container count.
- `missingContainers` and `keys`: older container/key listing fixtures. `keys` contains volume/bucket/key names, data sizes, versions, block maps keyed by version, and ISO creation/modification times.
- `fileSizeCounts` and `containerCount`: histogram-like arrays for utilization pages.
- Namespace browser fixtures `root`, `volume`, `bucket`, `dir`, `empty`, `key`, `clunky`, and `replica`: all use the same usage response shape with `status`, `path`, `size`, `sizeWithReplica`, `subPathCount`, `subPaths`, and `sizeDirectKey`.
- `metadata` and `quota`: namespace summary/quota responses. `metadata.objectInfo` mirrors Ozone object metadata, including ACLs, key location versions, replication config, bucket layout, owner, object IDs, and file/key attributes.
- `taskStatus`: Recon task status rows for container-key mapping, file-size counting, table count, namespace summary, OM delta/snapshot, container health, and pipeline sync tasks.
- Unhealthy container fixtures: `unhealthyContainers`, `unhealthyMissing`, `unhealthyUnderReplicated`, `unhealthyOverReplicated`, `unhealthyMisReplicated`, and `unhealthyReplicaMismatch`. These expose aggregate unhealthy counts, cursor fields, and container arrays with replica details.
- Object inventory and visualization fixtures: `volumes`, `buckets`, `bucketHeatmap`, `keyHeatmap`, and `heatmap`.
- Feature and overview summaries: `disabledFeatures`, `keysOpenSummary`, and `keysdeletePendingSummary`.
- Container mismatch fixtures: `omMismatch` and `scmMismatch`, each with `containerDiscrepancyInfo` rows, pipeline replication config, health flags, and `existsAt` markers.
- Open-key and pending-delete fixtures: `nonFSO`, `fso`, `keydeletePending`, `deleted`, and `dirdeletePending`.
- Decommission fixtures: `decommissioninfo` and the start of `DatanodesDecommissionInfo`. They use a capitalized `DatanodesDecommissionInfo` array property, matching current UI consumers.

## Control Flow and Serving Behavior

`db.json` itself has no functions or control flow. Runtime behavior is supplied by `json-server`, `routes.json`, and `pagination.js`.

`routes.json` first maps specific unhealthy-container subtype paths to subtype fixtures, then maps `/api/v1/*` to `/$1`, then adds more query-specific rewrites. This means route order matters: a specific query route such as `/keys/open?includeFso=false&includeNonFso=true&limit=*` resolves to `/nonFSO`, while generic API resources such as `/api/v1/datanodes` resolve to `/datanodes`.

For unhealthy subtype endpoints, `pagination.js` reads `db.json` on each matching request after `json-server` has already rewritten the path. It maps `/unhealthyMissing`, `/unhealthyUnderReplicated`, `/unhealthyOverReplicated`, `/unhealthyMisReplicated`, and `/unhealthyReplicaMismatch` back to the corresponding top-level key, filters `containers` by `containerID > minContainerId`, sorts ascending, slices to `limit`, and returns updated `firstKey` and `lastKey` values with the aggregate counts. The static `firstKey`/`lastKey` fields stored in `db.json` therefore serve as fallback/default fixture values, but middleware recomputes them for paged subtype requests.

## State and Persistence Behavior

The mock server's persistence is file-backed. `json-server --watch api/db.json` keeps the fixture file as the source of truth and may allow writes for non-GET requests depending on json-server behavior. The `datanodesRemove` fixture gives `/datanodes/remove` a response body containing `selectedRowKeys`, but the route is backed by static JSON rather than real Recon state mutation. Any edits to this file change local mock API state for all developers and tests that use the mock server.

Several fields encode backend state machines or long-running Recon state:

- Datanodes cover `state` values such as `HEALTHY` and `DEAD`, plus `opState` values such as `IN_SERVICE`, `DECOMMISSIONING`, `DECOMMISSIONED`, `ENTERING_MAINTENANCE`, and `IN_MAINTENANCE`.
- Unhealthy containers cover `MISSING`, `UNDER_REPLICATED`, `OVER_REPLICATED`, `MIS_REPLICATED`, and `REPLICA_MISMATCH`, with replica counts, deltas, BCS IDs, and optional checksum data.
- Open key fixtures distinguish non-FSO and FSO layouts; FSO keys use large negative object-ID path segments, while non-FSO uses readable S3-style paths.
- Delete-pending fixtures model grouped key deletion (`deletedKeyInfo` with `omKeyInfoList`), deleted container mismatch records, and deleted directories.
- Decommission fixtures expose datanode details, null metrics for summary rows, and detailed metrics/container categories for a single datanode view.

## Dependencies and Integration Points

Direct dependencies:

- `json-server` consumes this file as a mock database.
- `api/routes.json` defines endpoint-to-resource rewrites for nearly every top-level key.
- `api/pagination.js` depends on the unhealthy subtype keys and the `containers[*].containerID` field.

Observed UI consumers include:

- Overview pages reading `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, `/api/v1/keys/deletePending/summary`, and `/api/v1/datanodes/decommission/info`.
- Datanodes pages reading `/api/v1/datanodes`, `/api/v1/datanodes/decommission/info`, `/api/v1/datanodes/decommission/info/datanode?uuid=...`, and `/api/v1/datanodes/remove`.
- Pipelines and container tables consuming pipeline/datanode/replica shapes.
- Capacity pages consuming `/api/v1/storageDistribution` and `/api/v1/pendingDeletion?...` resources, partly outside this chunk.
- Heatmap and namespace pages consuming the namespace usage, metadata, quota, and read-access heatmap fixtures.

The JSON schema is implicit. TypeScript interfaces in the UI and MSW tests act as the practical contract, so field renames in this fixture can silently break local development even when no Java/Recon backend code changes.

## Risks and Edge Cases

- The chunk ends before the standalone `DatanodesDecommissionInfo` object closes. A chunk-local parser cannot validate only lines 1-9035 as complete JSON; whole-file validation is needed during merge.
- Field spelling and capitalization are contract-sensitive. The fixture uses `DatanodesDecommissionInfo` as both a top-level resource key and response property, and also includes inconsistent spellings such as `decomissioned` in pipeline datanode details versus `decommissioned` in decommission details.
- Count fields do not always match array sizes. For example `unhealthyContainers` reports `missingCount: 3`, `underReplicatedCount: 2`, `overReplicatedCount: 2`, and `misReplicatedCount: 2` while its array contains 10 mixed-state rows including `REPLICA_MISMATCH`. This is useful for UI testing but risky if client code assumes strict arithmetic consistency.
- Some fixture values are deliberately sentinel or unusual: `sizeWithReplica: -1`, pending block sizes of `-1`, null metrics, empty replica arrays for missing containers, huge negative object IDs, very large byte counts, and stringified object descriptions.
- Route matching is brittle because many `routes.json` entries include exact query-string patterns and inconsistent casing such as `sortSubpaths` versus `sortSubPaths`. Small client query changes may bypass the intended fixture.
- `pagination.js` rereads `db.json` per request. This is simple and accurate for watched local data, but malformed JSON or a transient partial edit causes middleware fallback with only a console error.
- The file mixes old and newer API shapes, including legacy top-level resources and v2 UI needs. Removing apparently duplicated sections can break older views, newer pages, or tests.

## Test Signals

Useful validation signals for this chunk:

- `jq` can parse the whole `db.json` file, confirming valid full-file JSON despite the chunk boundary.
- `jq 'keys'` shows all expected top-level resources, including the resources mapped in `routes.json`.
- Array/count checks show major collection sizes: `datanodes` 19, `pipelines` 3, `missingContainers` 2, `keys` 15, unhealthy subtype arrays 25/15/12/13/11, `volumes` 5, `buckets` 5, `omMismatch` 22, `scmMismatch` 50, `nonFSO` 10, `fso` 10, `keydeletePending` 12 groups, `deleted` 32 containers, `dirdeletePending` 5, and `decommissioninfo` 2 rows.
- Mock-server smoke tests should request representative mapped paths: `/api/v1/clusterState`, `/api/v1/datanodes`, `/api/v1/containers/unhealthy/MISSING?limit=5&minContainerId=0`, `/api/v1/namespace/usage?path=/&files=true&sortSubpaths=true`, `/api/v1/keys/open/summary`, `/api/v1/containers/mismatch?&missingIn=OM`, `/api/v1/keys/deletePending?limit=10`, and `/api/v1/datanodes/decommission/info`.
- UI tests around Datanodes, Overview, Pipelines, Containers, Capacity, and namespace browsing are the best regression indicators because they assert the implicit fixture contract more directly than JSON validation alone.
