# subset-b-008134 research

Grouped research report for the listed Apache Ozone Recon frontend and test files. Each section is source-tree aligned and wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/overview/overview.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/overview/overview.tsx

## Purpose
This React class component renders the Recon Overview dashboard. It aggregates cluster state, OM sync task status, open-key summary, pending-delete summary, and decommissioning datanode information into `OverviewCard` tiles, with an `AutoReloadPanel` controlling refresh and OM DB sync.

## Important APIs, types, and functions
`IClusterStateResponse` models `/api/v1/clusterState`; `IOverviewState` stores card values, loading state, timestamps, OM sync status, service IDs, and summary counters. `_loadData` is the main fetch routine and uses `PromiseAllSettledGetHelper` for `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, `/api/v1/keys/deletePending/summary`, and `/api/v1/datanodes/decommission/info`. `omSyncData` calls `/api/v1/triggerdbsync/om`. `componentDidMount` starts polling; `componentWillUnmount` stops polling and aborts pending requests.

## Control flow, state, and persistence
The component keeps all view state in React memory; there is no browser persistence. `_loadData` marks `loading`, cancels previous overview and OM sync requests, then evaluates settled responses. Rejected non-cancel responses produce per-request `showDataFetchError` messages; canceled responses are rethrown as `CanceledError`. Missing cluster state falls back to `N/A` values. Render derives error flags when summary fields are `undefined`, builds health/error UI for datanodes and containers, formats capacity with `filesize.partial`, and routes cards to Recon subpages.

## Dependencies and integration points
The component depends on Ant Design layout/tooltips/icons, `moment`, `filesize`, `OverviewCard`, `AutoReloadPanel`, `AutoReloadHelper`, and Recon axios helpers. It integrates with backend endpoints that are also tested in this subset, especially `ClusterStateEndpoint` and OM insight summaries. Service IDs from cluster state are surfaced as dashboard cards.

## Risks and edge cases
`cancelOverviewSignal` and `cancelOMDBSyncSignal` are module globals, so concurrent component instances would share cancellation state. `decommissionResponse.value?.data?.DatanodesDecommissionInfo.length` assumes the list property exists whenever `data` exists. Casting `missingContainersCount as number` when it may be string `N/A` relies on surrounding checks. `clusterCapacity` subtracts `remaining` from `capacity`; invalid or string values from the API could produce bad formatting.

## Test signals
There is no direct frontend test in this subset. Backend coverage comes indirectly from `TestClusterStateEndpoint`, deleted/open key endpoint tests elsewhere, and utility tests for the response-producing backend. UI behavior should be covered with a mocked axios/rendering test for partial request failure, cancellation, and `N/A` fallback rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/overview/overview.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/pipelines/pipelines.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/pipelines/pipelines.tsx

## Purpose
This React class component renders the Recon Pipelines page. It fetches pipeline metadata from `/api/v1/pipelines` and displays active pipeline rows in an Ant Design table with search, sort, status filtering, replication icons, leader metrics, and auto-refresh.

## Important APIs, types, and functions
`PipelineStatusList` defines allowed pipeline status filter values. `IPipelineResponse` models each table row, including `pipelineId`, `status`, replication type/factor, leader node, datanodes, leader election metrics, lifetime, and container count. `COLUMNS` defines Ant table columns and renderers. `_loadData` uses `AxiosGetHelper` to fetch `IPipelinesResponse`. `onShowSizeChange` and `onTabChange` are placeholders for pagination logging and future inactive-pipeline support.

## Control flow, state, and persistence
The component stores `activeLoading`, `activeDataSource`, `activeTotalCount`, and `lastUpdated` in memory. On mount it fetches data and starts `AutoReloadHelper` polling. On unmount it stops polling and cancels the module-level `cancelPipelineSignal`. Render wraps searchable columns using `ColumnSearch` at render time and uses `rowKey='pipelineId'`.

## Dependencies and integration points
Dependencies include Ant Design table/tabs/tooltips, `pretty-ms` for durations, `moment` for refresh time, `ReplicationIcon`, `ColumnSearch`, and Recon axios/autoreload helpers. The backend contract is `/api/v1/pipelines`; the datanode column expects each datanode item to expose `hostName` and `uuid`, although the interface currently declares `datanodes: string[]`.

## Risks and edge cases
The `datanodes` type is inaccurate for the actual renderer, weakening TypeScript coverage. A module-level abort controller has the same multi-instance caveat as other Recon views. `onTabChange` advertises inactive-pipeline behavior but does nothing. `onShowSizeChange` logs to console rather than updating any data-source page size, which is acceptable for client-side tables but noisy in production.

## Test signals
No direct UI test is in this subset. Useful tests would mock `/api/v1/pipelines`, verify column search injection, status filters, datanode tooltip rendering, cancellation on unmount, and formatting for zero/unavailable leader election metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/pipelines/pipelines.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/volumes/volumes.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/volumes/volumes.tsx

## Purpose
This React class component renders the Recon Volumes page. It lists OM volume metadata, supports column selection, adjustable fetch limits, links from volumes to filtered bucket listings, and opens an ACL drawer for a selected volume.

## Important APIs, types, and functions
`IVolumeResponse` models backend volume rows from `/api/v1/volumes`; `IVolumesState` stores table rows, selected columns, column options, selected limit, ACL drawer state, and refresh metadata. `COLUMNS` defines sortable/searchable table columns for volume, owner, admin, creation/modification times, quota, namespace capacity, bucket link, and a dynamically injected ACL column. `_addAclColumn` mutates module-level `COLUMNS` and `defaultColumns`. `_loadData` fetches volumes using `AxiosGetHelper('/api/v1/volumes', ..., { limit })`.

## Control flow, state, and persistence
All state is in memory. The constructor injects the ACL column and initializes selected limit to 1000. `_loadData` ensures selected columns are populated, closes any ACL panel, fetches data, maps `IVolumeResponse` into `IVolume`, then updates table state and `lastUpdated`. Column selection uses `MultiSelect`; limit selection uses `CreatableSelect`, including user-created numeric limits. Unmount aborts the current request and stops polling.

## Dependencies and integration points
The component depends on Ant Design table, React Router `Link`, `react-select/creatable`, local `MultiSelect`, `AclPanel`, `QuotaBar`, `ColumnSearch`, `AutoReloadPanel`, and Recon axios/common utilities. Bucket drilldown is encoded as `/Buckets?volume=<name>`. The ACL drawer expects `IAcl[]` in each volume response.

## Risks and edge cases
`COLUMNS` and `defaultColumns` are module-level arrays mutated by each constructor; `_addAclColumn` tries to avoid duplicate ACL columns, but shared mutable table definitions can surprise tests and hot reload. `_onCreateOption` accepts `parseInt(created)` truthiness, so `0` is rejected but strings like `10abc` pass `parseInt`; `isValidNewOption` has the same partial-parse behavior. `currentRow` is initialized as `{}` despite `IVolume` expectations, so `currentRow.acls` and `currentRow.volume` can be undefined until a row is selected. Request cancellation uses direct abort rather than the shared `cancelRequests` helper.

## Test signals
No direct frontend tests are in this subset. Good coverage would verify ACL column injection idempotence, custom limit validation, API limit query params, bucket link query encoding, selected-column filtering, and drawer state reset on reload.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/volumes/volumes.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/tsconfig.json -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/tsconfig.json

## Purpose
This TypeScript configuration defines the compile-time contract for the Recon Vite/React frontend. It type-checks source files under `src` without emitting output.

## Important options
The target is `es2015`, with `dom`, `dom.iterable`, and `esnext` libs. TypeScript is strict, JavaScript input is disabled, module output is `esnext`, module resolution is `node`, JSON modules are allowed, and `isolatedModules` plus `noEmit` suit Vite/SWC builds. `baseUrl` is `src`; path aliases map `@/*` to source-root imports and `@tests/*` to `src/__tests__/*`. Global types include Vite, SVGR, and Vitest globals.

## Control flow, state, and persistence
This file has no runtime control flow or persistence. Its practical effect is compile-time enforcement and IDE/module resolution behavior.

## Dependencies and integration points
It aligns with `vite.config.ts`, which defines matching `@` and `@tests` aliases and Vitest setup. The React JSX setting is `react`, matching classic JSX transform expectations while Vite uses `@vitejs/plugin-react-swc`.

## Risks and edge cases
`skipLibCheck` speeds builds but can hide dependency type conflicts. `isolatedModules` is necessary for Vite-style transpilation but disallows some TypeScript patterns. Strict mode exposes the inaccurate table row types seen in `pipelines.tsx`, though some `any` and widened column types bypass that protection.

## Test signals
No direct test file targets this config. Signals are frontend type-check/build success and Vitest discovery of `src/__tests__/**/*.test.tsx`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/tsconfig.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/vite.config.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/vite.config.ts

## Purpose
This Vite configuration builds and serves the Recon frontend. It configures React/SWC, static asset layout compatible with the existing webapp packaging, local API proxying, Less theming, aliases, and Vitest.

## Important APIs and options
`defineConfig` returns the Vite config. `pathResolve` resolves aliases relative to the project directory. `base: ""` makes assets relative so the app works behind a proxy or non-root path. Plugins include `react({ devTarget: "es2015" })` and `splitVendorChunkPlugin`. Build output targets ES2015, writes to `build`, and places JS under `static/js`, CSS under `static/css`, and other assets under `static/media`. Dev server proxies `/api` to `http://localhost:9888`. Less enables JavaScript, always-on math, relative URLs, and primary color override.

## Control flow, state, and persistence
Runtime control flow is limited to Vite’s build/dev server lifecycle and the `assetFileNames` callback. There is no application state.

## Dependencies and integration points
The config integrates Vite, `@vitejs/plugin-react-swc`, Rollup output naming, Ant Design Less variables, and Vitest with jsdom setup at `src/__tests__/vitest.setup.ts`. It mirrors `tsconfig.json` aliases and supports SVG imports through the types listed there.

## Risks and edge cases
`assetInfo.name!.split(".")[1]` assumes an asset name exists and has a simple extension; multi-dot names use the second segment rather than the last extension. `base: ""` is intentional for proxy deployment, but can alter assumptions for absolute URLs. The dev proxy is fixed to localhost port 9888. `splitVendorChunkPlugin` is legacy but still usable in Vite projects.

## Test signals
Vitest is configured for `src/__tests__/**/*.test.tsx` with verbose reporting and jsdom. Build success confirms asset callback and Less preprocessing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/vite.config.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/OMMetadataManagerTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/OMMetadataManagerTestUtils.java

## Purpose
This final test utility class builds OM and Recon OM metadata fixtures for Recon tests. It creates temporary OM DBs, copies OM checkpoints into Recon, writes key/directory/deleted-key records for multiple bucket layouts, provides mock OM service providers, and creates pipeline/block location helpers.

## Important APIs and functions
`initializeNewOmMetadataManager` creates an OM metadata manager with a default `sampleVol/bucketOne`; `initializeEmptyOmMetadataManager` creates an empty one. `getTestReconOmMetadataManager` checkpoints an OM DB, starts `ReconOmMetadataManagerImpl`, and imports the checkpoint. The overloaded `writeDataToOm`, `writeKeyToOm`, `writeOpenFileToOm`, `writeOpenKeyToOm`, `writeDeletedKeysToOm`, `writeDirToOm`, and `writeDeletedDirToOm` methods populate OM tables with legacy, default, and FSO key shapes. `getMockOzoneManagerServiceProvider` and `getMockOzoneManagerServiceProviderWithFSO` return Mockito-backed providers with table names. `getRandomPipeline` and `getOmKeyLocationInfo` create SCM block-location fixtures.

## Control flow, state, and persistence
The class writes directly to RocksDB-backed OM tables and creates DB checkpoints on disk. It maintains a static `OzoneConfiguration configuration` reused by `getTestReconOmMetadataManager`; callers can read or replace it through accessors. Key-building branches on `BucketLayout.FILE_SYSTEM_OPTIMIZED` to choose object-ID path keys versus regular ozone keys.

## Dependencies and integration points
It is used throughout Recon endpoint and task tests, including container, blocks, cluster state, namespace summary, and deleted-key scenarios. It integrates with OM helpers (`OmKeyInfo`, `OmBucketInfo`, `OmDirectoryInfo`, `RepeatedOmKeyInfo`), Recon recovery (`ReconOMMetadataManager`), SCM pipeline classes, and Mockito.

## Risks and edge cases
The static configuration can leak settings between tests unless reset. Many helpers have long parameter lists, so object ID and parent ID ordering mistakes can silently create invalid FSO paths. Several generated records omit optional fields such as ACLs, timestamps, or replication variants unless specifically supplied. Mock table names are important because downstream tasks branch on table names.

## Test signals
This file is a fixture provider rather than a test. Its correctness is exercised indirectly by endpoint tests in this subset, especially `TestContainerEndpoint`, `TestBlocksEndPoint`, and `TestClusterStateEndpoint`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/OMMetadataManagerTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/ReconTestInjector.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/ReconTestInjector.java

## Purpose
`ReconTestInjector` wraps Guice setup for Recon unit and integration tests. It lets tests compose a temporary `OzoneConfiguration`, optional Recon SQL schema, OM/SCM service instances, container metadata managers, and extra bindings without repeating module wiring.

## Important APIs and functions
The outer class stores configured components and exposes `getInstance`/`getInjector`. `setupInjector` creates a base `AbstractModule` binding `OzoneConfiguration`, supplied OM/SCM providers, optional container DB managers, and caller-provided instance/class/inherited bindings. `getTestOzoneConfiguration` points Recon DB, OM snapshot DB, and SCM DB dirs at the temp directory and sets test datanode/prometheus endpoints. The nested `Builder` exposes fluent methods such as `withReconSqlDb`, `withOmServiceProvider`, `withReconOm`, `withReconScm`, `withContainerDB`, `addBinding`, `addModule`, and `build`.

## Control flow, state, and persistence
`build` calls `setupInjector`, which optionally constructs `AbstractReconSqlDBTest`, appends SQL modules, creates the Guice injector, and creates SQL schema after injection. Persistence is limited to temporary DB paths passed by tests.

## Dependencies and integration points
The class integrates Guice, Recon SQL DB test modules, SCM facade classes, Recon metadata manager implementations, and service-provider interfaces. It is central to the endpoint tests in this subset.

## Risks and edge cases
Raw `Class` maps/sets lose generic type safety. Optional manager binding means missing dependencies fail at injection time rather than builder time. `tmpDir` is required only by a runtime precondition. Binding default container DB implementations under `withContainerDB` can create substantial RocksDB/SQL state that must be cleared by tests.

## Test signals
No direct tests target this builder, but every endpoint test using `new ReconTestInjector.Builder(...).build()` validates its wiring. Failures usually surface as Guice creation errors or missing schema/table errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/ReconTestInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconCodecs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconCodecs.java

## Purpose
This JUnit test verifies binary persistence round trips for codecs used by Recon metadata tables.

## Important APIs and functions
`testContainerKeyPrefixCodec` creates a `ContainerKeyPrefix`, serializes it with singleton `ContainerKeyPrefixCodec.get()`, deserializes it, and asserts equality. `testIntegerCodec` performs the same persisted-format round trip for Hadoop `IntegerCodec`.

## Control flow, state, and persistence
The tests operate entirely in memory. They validate the byte-array persisted representation but do not write to RocksDB.

## Dependencies and integration points
The tested codec supports `ContainerKeyPrefix`, which is used by Recon container-to-key mapping. `IntegerCodec` is a generic DB codec used by table definitions.

## Risks and edge cases
The container prefix test uses `System.currentTimeMillis`, so equality depends on deterministic serialization of arbitrary long container IDs and key prefixes but does not check stable byte ordering. It only covers one key prefix and version value.

## Test signals
Strong signal for basic serialize/deserialize symmetry. It does not cover backward compatibility, malformed bytes, null handling, or lexicographic ordering expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconCodecs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconUtils.java

## Purpose
This JUnit test covers utility methods in `ReconUtils`, including Recon DB directory resolution, tar creation/extraction, HTTP checkpoint download plumbing, latest DB selection, and power-of-two bucket index calculation.

## Important APIs and functions
`testGetReconDbDir` checks config-to-`File` resolution. `testCreateTarFile` writes two files and calls `ReconUtils.createTarFile`. `testUntarCheckpointFile` creates a tar and extracts it with `untarCheckpointFile`. `testMakeHttpCall` mocks `URLConnectionFactory` and `HttpURLConnection` to verify returned input stream contents. `testGetLastKnownDB` confirms prefix-based latest file selection. `testNextClosestPowerIndexOfTwo` compares `ReconUtils.nextClosestPowerIndexOfTwo` against a fixed reference for zero, powers, neighbors, extremes, and random values. `getContainer` is a public static fixture helper for building `ContainerInfo`.

## Control flow, state, and persistence
Tests use JUnit `@TempDir` filesystem state and clean up tar artifacts. The HTTP test is fully mocked and does not perform network I/O. The power-index test exercises many branches, including negative values and `Long.MIN_VALUE`.

## Dependencies and integration points
Dependencies include Apache Commons IO, Hadoop `URLConnectionFactory`, SCM `ContainerInfo`, `RatisReplicationConfig`, and JUnit temp directories. `getContainer` can be reused by other tests needing simple container fixtures.

## Risks and edge cases
Tar tests validate successful extraction count but not path traversal hardening, permissions, nested directories, or corrupt tar behavior. `testGetLastKnownDB` relies on filesystem listing/order behavior only through the utility. Random values improve coverage but are not deterministic.

## Test signals
Good utility-level coverage for common success paths and regression coverage for signed power-index behavior. Security-sensitive tar extraction should have additional malicious-archive tests if not elsewhere covered.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestTarExtractor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestTarExtractor.java

## Purpose
This JUnit/Mockito test verifies `TarExtractor` executor lifecycle behavior: pool creation, thread naming, shutdown, and idempotent start.

## Important APIs and functions
`testStartCreatesFixedThreadPoolWithConfiguredSize` mocks static `Executors.newFixedThreadPool` and verifies the configured pool size. `testThreadFactoryUsesConfiguredPrefix` captures the `ThreadFactory` and asserts created thread names start with the configured prefix. `testStopShutsDownExecutor` verifies `shutdown` after `stop`. `testStartIsIdempotent` calls `start` twice and verifies only one executor is created.

## Control flow, state, and persistence
The tests are in memory and use Mockito static mocking. `TarExtractor` is constructed outside the static mock block so its internal thread factory builder can call the real default factory. Shutdown behavior stubs `awaitTermination`.

## Dependencies and integration points
Dependencies include JUnit 5 and Mockito static mocking. This indirectly protects Recon code that uses `TarExtractor` to parallelize snapshot tar extraction.

## Risks and edge cases
The tests do not submit extraction tasks or verify forced shutdown on timeout/interruption. Static mocking of `Executors` is sensitive to construction ordering, which the comments explicitly call out.

## Test signals
Good lifecycle regression coverage for concurrency setup. Functional tar extraction behavior is covered separately by `TestReconUtils`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/TestTarExtractor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/NSSummaryTests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/NSSummaryTests.java

## Purpose
This abstract class contains shared namespace-summary endpoint assertions used by layout-specific `NSSummaryEndpoint` tests. It verifies basic-info responses for root, volume, bucket, directory, missing path, and key entities.

## Important APIs and functions
`testNSSummaryBasicInfoRoot` seeds root prefix ACL/metadata and asserts root entity type, counts, ACL conversion, and metadata. Instance methods test volume counts and `VolumeObjectDBInfo`, bucket counts and `BucketObjectDBInfo` for supplied `BucketLayout`, directory counts/quota defaults, missing-path `PATH_NOT_FOUND`, and key-level `KeyObjectDBInfo` including replication type.

## Control flow, state, and persistence
Only the root test writes to the prefix table; all methods call `NSSummaryEndpoint.getBasicInfo(path)` and assert the response entity. Persistence is through the caller-provided `ReconOMMetadataManager` tables and namespace summary state prepared by concrete tests.

## Dependencies and integration points
It integrates `NSSummaryEndpoint`, `ReconOMMetadataManager`, OM prefix ACLs, `NamespaceSummaryResponse`, object DB info DTOs, bucket layouts, and response statuses. It is designed for reuse by FSO, OBS, legacy, and mixed-layout tests.

## Risks and edge cases
The expected counts are hard-coded to a specific fixture shape, so changes in concrete test data require synchronized updates. The root ACL setup assumes the root prefix table key and ACL conversion behavior. The class is not independently executable because most methods are helpers rather than annotated tests.

## Test signals
High-value shared assertions for endpoint response contracts across namespace layouts. It covers success and not-found paths but not authorization or malformed path handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/NSSummaryTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestBlocksEndPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestBlocksEndPoint.java

## Purpose
This JUnit test validates `BlocksEndPoint.getBlocksPendingDeletion`, which groups pending deleted-block transactions by container state and supports limit and previous-key pagination.

## Important APIs and functions
`initializeInjector` builds a Recon test graph with SQL DB, Recon OM, SCM facade, container DB, `ContainerEndpoint`, and `BlocksEndPoint`, then captures `ReconContainerManager`, `ReconPipelineManager`, and SCM `DBStore`. `setUp` seeds open containers 100-107. The three tests insert `DeletedBlocksTransaction` rows into the SCM `DELETED_BLOCKS` table and call `getBlocksPendingDeletion(limit, prevKey)`. `getTestContainer` creates a `ContainerWithPipeline` for a given ID and state.

## Control flow, state, and persistence
The test writes SCM deleted-block transactions to the RocksDB table and container state to the Recon SCM facade. `testGetBlocksPendingDeletion` verifies one transaction under `"OPEN"`. `testGetBlocksPendingDeletionLimitParam` verifies only the first row is returned when limit is one. `testGetBlocksPendingDeletionPrevKeyParam` verifies seeking past transaction ID 2 returns TX 3 and seeking at/after existing TX IDs can return empty.

## Dependencies and integration points
Dependencies include `ReconTestInjector`, `OMMetadataManagerTestUtils`, SCM DB definitions, container manager/pipeline manager, protobuf `DeletedBlocksTransaction`, and `ContainerBlocksInfoWrapper`. This test connects SCM table data to endpoint DTOs.

## Risks and edge cases
`isSetupDone` avoids rebuilding the injector but `setUp` repeatedly adds the same container IDs, so test isolation depends on container manager behavior. The tests only cover open containers and do not exercise missing container state mapping, multiple states, or invalid parameters.

## Test signals
Good regression coverage for limit and prev-key semantics over SCM deleted-block transactions and DTO field population (`containerID`, local IDs, count, TX ID).
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestBlocksEndPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestClusterStateEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestClusterStateEndpoint.java

## Purpose
This JUnit test validates `ClusterStateEndpoint.getClusterState`, especially container state counts, SCM/OM service IDs, and storage report DTO typing/fields.

## Important APIs and functions
`setUp` builds a Recon injector with SQL DB, Recon OM, SCM facade, container DB, `ClusterStateEndpoint`, and `ContainerHealthSchemaManager`, then constructs an endpoint with a mocked `OzoneConfiguration`. `testGetContainerCounts` inserts open, deleted, and closed containers and asserts total excludes deleted while open/deleted counts are separate. `testScmAndOmServiceId` verifies config keys flow into `ClusterStateResponse`. `testStorageReportIsClusterStorageReport` uses mocks to validate `ClusterStorageReport` fields from SCM node stats and filesystem usage. `newContainerInfo` and `putContainerInfos` seed containers.

## Control flow, state, and persistence
The primary setup writes Recon SCM container state in the test facade. The storage-report test is pure Mockito and bypasses persistent state. Cluster state aggregation pulls from node manager, pipeline manager, container manager, unhealthy container schema manager, global stats, and configuration.

## Dependencies and integration points
Dependencies include Recon SCM managers, SQL schema manager, `ReconGlobalStatsManager`, `ClusterStateResponse`, `ClusterStorageReport`, SCM node stats, and OM/SCM HA service ID config keys. This endpoint feeds the frontend `overview.tsx` dashboard.

## Risks and edge cases
The total container expectation intentionally excludes `DELETED`; regressions here affect UI dashboard counts. Mocked storage report fields assert specific mapping of capacity, used, remaining, committed, minimum free, reserved, filesystem capacity/used/available. The tests do not cover missing/unavailable global stats or multiple datanodes beyond one mocked node.

## Test signals
Strong contract tests for overview-facing cluster summary fields and storage report type. They help protect frontend assumptions around `openContainers`, `deletedContainers`, `storageReport`, `scmServiceId`, and `omServiceId`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestClusterStateEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestContainerEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestContainerEndpoint.java

## Purpose
This large integration-style JUnit test validates `ContainerEndpoint` behavior across container-key lookup, container listing, missing/unhealthy containers, replica history, SCM-deleted containers, OM/SCM mismatch insights, OM containers deleted in SCM, duplicate FSO path reconstruction, and quasi-closed container APIs.

## Important APIs and functions
`initializeInjector` wires Recon OM, SQL DB, SCM facade, container DB, `ContainerEndpoint`, and `ContainerHealthSchemaManager`. `setUp` seeds OM key-location data for legacy/default containers and reprocesses OBS and FSO container-key mapper tasks in parallel. `setUpFSOData` and `setUpDuplicateFSOFileKeys` write FSO volume, bucket, directory, and key table entries. `reprocessContainerKeyMapper` runs `ContainerKeyMapperTaskOBS` and `ContainerKeyMapperTaskFSO`. Helper methods create containers, datanodes, unhealthy records, deleted lifecycle transitions, and pipeline-isolated SCM containers.

## Control flow, state, and persistence
The test exercises both RocksDB-backed OM/SCM state and SQL-backed unhealthy-container state. On repeated setup it clears shared container-key maps, resets truncation flags, and reinitializes container metadata from an empty map to reduce leakage. Tests mutate container lifecycle states through SCM events (`FINALIZE`, `CLOSE`, `DELETE`, `CLEANUP`, `QUASI_CLOSE`), write replica history into Recon container manager, and update OM-to-container mappings through reprocess tasks.

## Endpoint coverage
`getKeysForContainer` is tested for total count, limit, prev-key, legacy key versions/block IDs, FSO file-table keys, and duplicate FSO file names under different directories. `getContainers` is tested for limit, previous key, sequential and non-sequential IDs, and invalid parameters. `getMissingContainers`, `getUnhealthyContainers`, filtered unhealthy states, invalid states, and pagination verify counts, replica histories, checksum mismatch, and expected/actual/delta counts. `getReplicaHistoryForContainer` validates latest history de-duplication and descending order. `getSCMDeletedContainers` covers deleted lifecycle rows with limit and prev key. `getContainerMisMatchInsights` covers containers present only in OM, only in SCM, filter direction, pagination, and per-container pipeline-list isolation. `getOmContainersDeletedInSCM` covers deleted-in-SCM discrepancy rows, count/limit/prev behavior. Quasi-closed tests cover empty, basic, with replicas, pagination, count-only limit zero, invalid inputs, and dedicated count behavior.

## Dependencies and integration points
The test integrates nearly every Recon container subsystem: `ReconContainerMetadataManager`, `ReconNamespaceSummaryManager`, `ReconContainerManager`, `ReconPipelineManager`, `ContainerHealthSchemaManager`, `ContainerKeyMapperTaskOBS/FSO`, `NSSummaryTaskWithFSO`, OM metadata helpers, SCM lifecycle state machine, and endpoint DTOs such as `KeysResponse`, `ContainersResponse`, `UnhealthyContainersResponse`, `ContainerDiscrepancyInfo`, and `QuasiClosedContainersResponse`.

## Risks and edge cases
The class is marked `@Flaky("HDDS-14178")`, reflecting real isolation or timing sensitivity. It uses shared state and concurrent mapper reprocessing, so cleanup order is important. FSO tests depend on exact object IDs and path keys. Pagination tests assume sorted container IDs and stable RocksDB iteration. Mismatch tests manipulate mappings directly with batch deletes, which is powerful but can bypass invariants. Duplicate FSO setup intentionally uses repeated object/key values and is sensitive to endpoint path reconstruction logic.

## Test signals
This is the strongest test signal in the subset for container endpoints and related Recon tasks. It covers many production workflows and known regressions: table truncation/shared maps, FSO/OBS mapper interaction, unhealthy state compatibility, checksum mismatch, OM/SCM discrepancy direction, and quasi-closed response contracts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestContainerEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestDeletedKeysSearchEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestDeletedKeysSearchEndpoint.java

## Purpose
This JUnit test validates deleted-key search through `OMDBInsightEndpoint.getDeletedKeyInfo`. It covers root/volume restrictions, empty search, bucket/directory/key-level prefixes, nested directories, limits, bad requests, last-key calculation, pagination, empty buckets, and combinations of `prevKey` and `startPrefix`.

## Important APIs and functions
`setUp` creates an empty OM metadata manager, imports it into Recon OM, builds a Recon injector with SQL and container DB support, gets `OMDBInsightEndpoint`, then calls `populateOMDB`. `populateOMDB` writes 16 deleted keys across `volb/bucketb1` and `volc/bucketc1` with nested directory-like key names. `createDeletedKey` builds deleted table keys shaped as `/volume/bucket/key/random` and stores `RepeatedOmKeyInfo`. `writeDeletedKeysToOm` writes directly to the OM deleted table.

## Control flow, state, and persistence
The test persists deleted key rows into Recon OM metadata. Endpoint calls use `limit`, `prevKey`, and `startPrefix` to seek and filter table entries. Tests assert HTTP statuses and `KeyInsightInfoResponse` list sizes, last-key prefixes, and first returned key names after cursor skips.

## Dependencies and integration points
Dependencies include Recon OM metadata, `OMDBInsightEndpoint`, `KeyInsightInfoResponse`, OM `RepeatedOmKeyInfo`, `OmKeyInfo`, standalone replication config, and `ReconTestInjector`. The endpoint likely feeds Recon UI insight pages for deleted/pending-deletion key browsing.

## Risks and edge cases
The fixture is path-string based and does not create volume/bucket table entries for every prefix, so the endpoint behavior under real metadata validation may differ if validation is added. A key named `filgetec6` appears in the fixture and may be intentional noise or typo. Bad request tests for negative limit assert the path error message rather than a limit-specific error. Deleted keys include random suffixes, so tests compare counts and prefixes rather than exact keys.

## Test signals
Strong coverage for prefix filtering and cursor semantics, including empty prefix full-table scans. It protects user-visible pagination behavior through `lastKey` and the "No keys matched" `NO_CONTENT` contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestDeletedKeysSearchEndpoint.java -->
