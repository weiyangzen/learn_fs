# subset-b-008124 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconContainerMetadataManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconContainerMetadataManagerImpl.java

Purpose: Implements `ReconContainerMetadataManager`, the Recon-side service for container/key reverse indexes, per-container key counts, replica history, and the total container count. It binds Recon's internal RocksDB column families from `ReconDBDefinition` and also uses the generated SQL `GlobalStatsDao` for `CONTAINER_COUNT_KEY`.

Important APIs: staged manager creation over a staged `DBStore`, `reinitialize`, `reinitWithNewContainerDataFromOm`, batched store/delete for `ContainerKeyPrefix` and `KeyPrefixContainer`, `getKeyPrefixesForContainer`, `getContainerForKeyPrefixes`, `getContainersIterator`, replica history getters/setters, and `incrementContainerCountBy`. It exposes table accessors for tests and iterator-based callers.

Control flow and persistence: initialization opens `CONTAINER_KEY`, `KEY_CONTAINER`, `CONTAINER_KEY_COUNT`, and `REPLICA_HISTORY_V2`. If `KEY_CONTAINER` is empty, it backfills it from `CONTAINER_KEY`. Writes maintain both forward and reverse key mappings when a key prefix is present, and commit through `RDBBatchOperation`. `reinitWithNewContainerDataFromOm` truncates container tables, repopulates mappings, and resets SQL container count to zero.

Dependencies and integration: depends on `ReconDBProvider`, `ReconOMMetadataManager`, codecs for `ContainerKeyPrefix` and `KeyPrefixContainer`, JOOQ SQL configuration, and OM key tables for pipeline lookup. Container-key mapper tasks are its primary writers; API endpoints likely page through `getKeyPrefixesForContainer` and `getContainers`.

Risks: `getPipelines` builds a stream but does not terminally consume it, so pipelines may never be added. `getContainersIterator.next` increments `numberOfKeys` by one per prefix row instead of using stored counts. `initializeTables` logs but does not fail fast on table-open errors. Container count writes are read-modify-write through SQL and can race across tasks.

Test signals: existing tests include `TestReconContainerMetadataManagerImpl`; useful coverage should include reverse-index backfill, pagination from a non-existent or exact previous key, staged-manager behavior, replica history V2 persistence, and concurrent container count updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconContainerMetadataManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBDefinition.java

Purpose: Defines the internal Recon RocksDB layout by extending `DBDefinition.WithMap`. The definition is the single registry of column families used by the Recon RocksDB store.

Important APIs/types: static `DBColumnFamilyDefinition` constants for `CONTAINER_KEY`, `KEY_CONTAINER`, `CONTAINER_KEY_COUNT`, `REPLICA_HISTORY`, `NAMESPACE_SUMMARY`, `REPLICA_HISTORY_V2`, `FILE_COUNT_BY_SIZE`, and `GLOBAL_STATS`. The constructor accepts the DB name, `getName` returns that runtime name, and `getLocationConfigKey` points to `OZONE_RECON_DB_DIR`.

State and persistence: the class defines persisted key/value codecs: `ContainerKeyPrefixCodec`, `KeyPrefixContainerCodec`, `LongCodec`, `NSSummaryCodec`, `ContainerReplicaHistoryList` codec, `FileSizeCountKey` codec, and `GlobalStatsValue` codec. The unmodifiable column-family map is what `DBStoreBuilder.createDBStore` uses to open or create Recon's store.

Dependencies and integration: consumed by `ReconDBProvider.initializeDBStore`; manager implementations retrieve typed tables through these definitions. The old `REPLICA_HISTORY` and newer `REPLICA_HISTORY_V2` coexist, which preserves upgrade compatibility while allowing bcsId-aware history.

Risks: adding or renaming a column family here is a storage-format change. Code that writes SQL global stats and RocksDB `GLOBAL_STATS` can create two stats stores with different lifecycles. Codec compatibility for protobuf-backed keys is critical because existing RocksDB data is read through these definitions at startup.

Test signals: codec tests and DB-provider tests are the main signals. Add coverage when introducing new families to verify DB open, staged DB open, and round-trip encoding for each persisted key/value pair.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBProvider.java

Purpose: Provides the singleton Recon internal `DBStore`, supports staged DB creation for snapshot rebuilds, and swaps a staged DB into the live DB path.

Important APIs: `getDbStore`, `getStagedReconDBProvider`, `provideReconDB`, `replaceStagedDb`, `close`, and static `truncateTable`. `getStagedReconDBProvider` deletes any stale `.staged` DB and opens a fresh one. `replaceStagedDb` closes the staged and live stores, renames the live DB to `.backup`, renames staged into the live name, then reopens.

Control flow and persistence: startup recovers old last-known Recon DB paths from `ReconUtils.getLastKnownDB`. If the live DB is missing but a `.backup` exists, it restores the backup. DB open delegates to `DBStoreBuilder.createDBStore(configuration, new ReconDBDefinition(dbName))`.

Dependencies and integration: depends on `OzoneConfiguration`, `ReconUtils`, Apache Commons `FileUtils`, and local filesystem atomic moves. Managers are reinitialized against this provider after DB replacement.

Risks: `replaceStagedDb` recovery assumes the failure mode leaves enough paths to move back; partial filesystem failures can still strand `.staged` or `.backup` directories. `truncateTable` deletes row by row and is expensive for large column families. Atomic moves may fail across filesystems, so the configured DB directory must keep staged and live DBs on the same mount.

Test signals: `TestReconDBProvider` should cover initialization and provider binding. Additional valuable tests are interrupted replacement, backup restoration, stale staged cleanup, and `truncateTable` behavior on null and populated tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconFileMetadataManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconFileMetadataManagerImpl.java

Purpose: Implements `ReconFileMetadataManager` for RocksDB-backed file-size distribution counts.

Important APIs: staged manager creation, `reinitialize`, `batchStoreFileSizeCount`, `batchDeleteFileSizeCount`, `getFileSizeCount`, `getFileCountTable`, `commitBatchOperation`, and `clearFileCountTable`.

State and persistence: owns the `FILE_COUNT_BY_SIZE` table from `ReconDBDefinition`, keyed by `FileSizeCountKey` and valued by `Long`. It writes only through caller-provided batches and commits those batches through the shared Recon `DBStore`. Clearing the table delegates to `ReconDBProvider.truncateTable`.

Dependencies and integration: injected from `ReconDBProvider`; used by `FileSizeCountTaskHelper`, `FileSizeCountTaskFSO`, and `FileSizeCountTaskOBS`. The table is read-modify-written by helper code during incremental processing and reprocess flushes.

Risks: `initializeTables` logs errors but leaves `fileCountTable` nullable, so later callers can fail with NPEs instead of a clear startup failure. The manager offers no compare-and-swap or locking around read-modify-write counts, so correctness depends on task-level partitioning and flush synchronization. Row-wise truncate can be slow for high-cardinality volume/bucket/size distributions.

Test signals: manager-level tests should store, update, delete, clear, and stage the file-count table. Task tests should assert that zero or negative resulting counts delete rows and that FSO and OBS reprocess truncate only once.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconFileMetadataManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconGlobalStatsManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconGlobalStatsManagerImpl.java

Purpose: Implements `ReconGlobalStatsManager` over the RocksDB `GLOBAL_STATS` column family. It stores simple named counters or stats as `GlobalStatsValue`.

Important APIs: staged manager creation, `reinitialize`, `batchStoreGlobalStats`, `getGlobalStatsValue`, `getGlobalStatsTable`, and `commitBatchOperation`.

State and persistence: opens `ReconDBDefinition.GLOBAL_STATS` as `Table<String, GlobalStatsValue>`. Writers batch string keys and protobuf-backed values, then commit through the shared Recon `DBStore`.

Dependencies and integration: injected from `ReconDBProvider`. This manager is the RocksDB counterpart to the older/generated SQL global stats paths used elsewhere, such as `ReconContainerMetadataManagerImpl` for container count and Om table insight tasks for table-level counts.

Risks: the repository has both SQL global stats and RocksDB global stats abstractions. Callers must be explicit about which store is authoritative for a metric, or Recon can show stale or divergent counters. Like other managers, table initialization errors are logged but not propagated.

Test signals: round-trip tests should cover a null-safe `GlobalStatsValue`, staged manager writes, and batch commit. Integration tests should verify tasks reading global stats use the same storage path as the tasks writing them.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconGlobalStatsManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconNamespaceSummaryManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconNamespaceSummaryManagerImpl.java

Purpose: Provides wrapper operations for the RocksDB namespace summary table used by Recon namespace APIs and `NSSummaryTask`.

Important APIs: `getStagedNsSummaryManager`, `reinitialize`, `clearNSSummaryTable`, `storeNSSummary`, batched store/delete, `deleteNSSummary`, `getNSSummary`, `commitBatchOperation`, and `getNSSummaryTable`.

State and persistence: opens `NAMESPACE_SUMMARY` from the shared Recon DB, mapping object IDs to `NSSummary` values. The task layer builds and mutates summaries, while this class persists them with direct puts or `RDBBatchOperation` batches. Clear uses row-wise truncation.

Dependencies and integration: injected with `ReconDBProvider` and `NSSummaryTask`. Staged manager creation is used during staged OM snapshot reprocess. The `NSSummaryTaskWithFSO`, Legacy, OBS, and `NSSummaryAsyncFlusher` classes are primary callers.

Risks: a field `nsSummaryTask` is retained only to construct staged managers, which can create circular lifecycle coupling. The raw `Table` return type in `getNSSummaryTable` loses generic safety. Table clear is destructive and depends on `NSSummaryTask` rebuild coordination to avoid concurrent incremental writes into an emptying table.

Test signals: `TestReconNamespaceSummaryManagerImpl` covers basic table operations. Rebuild and endpoint tests should verify clear plus reprocess produces complete bucket, directory, and aggregate rows before queries rely on them.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconNamespaceSummaryManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/StorageContainerServiceProviderImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/StorageContainerServiceProviderImpl.java

Purpose: Implements `StorageContainerServiceProvider` by delegating SCM RPCs and downloading SCM RocksDB snapshots for Recon.

Important APIs: `getPipelines`, `getPipeline`, `getContainerWithPipeline`, `getExistContainerWithPipelinesInBatch`, `getNodes`, container count overloads, `getSCMDBSnapshot`, `getListOfContainerIDs`, and `getListOfContainerInfos`.

Control flow and persistence: most methods are thin wrappers over `StorageContainerLocationProtocol`. `getSCMDBSnapshot` locates the leader from SCM peer roles, builds a security client and `ReconCertificateClient`, downloads a tar checkpoint through `InterSCMGrpcClient`, untars it into the Recon SCM DB directory, deletes the tar, and returns a `RocksDBCheckpoint`.

Dependencies and integration: depends on SCM client protocol, `ReconUtils`, `ReconStorageConfig`, `ReconContext`, security config, Ratis peer roles, and filesystem storage under `RECON_SCM_SNAPSHOT_DB`. Recon SCM sync code uses this provider for container and snapshot state.

Risks: peer role parsing uses fixed colon indexes, making it sensitive to peer-role string format. Snapshot failure marks Recon health unhealthy and records `GET_SCM_DB_SNAPSHOT_FAILED`, but returns null, so callers must check. The catch block catches `Throwable`, which includes errors beyond recoverable IO. Security and gRPC setup are on the hot path for snapshot retrieval.

Test signals: `TestStorageContainerServiceProviderImpl` is the direct unit signal. Add tests for leader parsing, null return on download failure, tar cleanup, health-state update, and `getListOfContainerInfos` delegation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/StorageContainerServiceProviderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/package-info.java

Purpose: Package documentation for Recon SPI implementations.

Important APIs/types: no executable APIs. The file declares package `org.apache.hadoop.ozone.recon.spi.impl` and documents that classes here provide connectivity to underlying Ozone subsystems.

State and persistence: none.

Dependencies and integration: indirectly covers provider implementations such as Recon DB, OM, SCM, JMX, and Prometheus providers. It helps Javadoc readers distinguish SPI implementation classes from interfaces in the sibling package.

Risks: low runtime risk. The main maintenance risk is documentation drift if package responsibilities expand beyond service provider implementations.

Test signals: none needed beyond compilation and license checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/package-info.java

Purpose: Package documentation for Recon service provider interfaces.

Important APIs/types: no executable APIs. The file declares package `org.apache.hadoop.ozone.recon.spi` and documents that SPI interfaces allow Recon implementations to connect to Ozone subsystems.

State and persistence: none.

Dependencies and integration: applies to interfaces such as storage container, metrics, OM, and Recon metadata managers. The implementation package supplies concrete classes.

Risks: no runtime risk. Documentation should remain broad enough to cover both external service providers and internal metadata managers.

Test signals: compilation and source style checks only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperHelper.java

Purpose: Shared implementation for FSO and OBS container-key mapper tasks. It builds and maintains mappings from containers to key prefixes, reverse mappings from key prefixes to containers, and per-container key counts.

Important APIs: static `reprocess`, `process`, `handleKeyReprocess`, `flushAndCommitContainerKeyInfoToDB`, and test-only `clearSharedContainerCountMap`. Private handlers translate OM PUT, DELETE, and UPDATE events into container-key map changes.

Control flow and persistence: reprocess uses `ParallelTableIteratorOperation` over one bucket layout, worker-local `ContainerKeyPrefix` maps, and a static cross-task `ConcurrentHashMap<Long, AtomicLong>` for container counts. Static initialization truncates shared tables once across FSO and OBS. The last active task writes the shared count map, increments total container count, clears shared state, and resets the initialization flag. Incremental process filters by table, builds local add/delete/count deltas, scans reverse index for deletes, and commits a single batch.

Dependencies and integration: called by `ContainerKeyMapperTaskFSO` and `ContainerKeyMapperTaskOBS`; writes through `ReconContainerMetadataManager`; reads OM key location versions and container IDs.

Risks: correctness depends on both reprocess tasks participating; if only one task runs, the active counter and global state semantics can surprise. Exceptions before decrement can leave the static active count or initialization flag stale. Incremental container count updates use SQL read-modify-write. Delete handling scans reverse index and local map, so key equality/version semantics are important.

Test signals: cover concurrent FSO/OBS reprocess, failure cleanup, duplicate key versions, delete after put in same batch, update with missing old value, and shared-state reset between tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskFSO.java

Purpose: `ReconOmTask` wrapper that runs container-key mapping for File System Optimized buckets.

Important APIs: constructor injection of `ReconContainerMetadataManager` and `OzoneConfiguration`, `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess reads tuning knobs for flush threshold, max keys in memory, iterators, and workers, then delegates to `ContainerKeyMapperHelper.reprocess` with `BucketLayout.FILE_SYSTEM_OPTIMIZED`. Incremental process delegates to the helper for the `fileTable` event stream.

Dependencies and integration: participates with `ContainerKeyMapperTaskOBS` through helper static coordination. Staged tasks use the staged Recon DB store so full snapshot rebuilds can be swapped atomically.

Risks: the helper's static active-task coordination assumes FSO and OBS reprocess lifecycles align. Table name is hardcoded as `fileTable`, while other code sometimes imports constants, so OM table-name changes would break filtering silently.

Test signals: verify `getTaskName`, staged manager wiring, config propagation, file-table filtering, and concurrent FSO/OBS rebuild behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskOBS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskOBS.java

Purpose: `ReconOmTask` wrapper that runs container-key mapping for Object Store bucket keys.

Important APIs: `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess loads the same parallelism and flush-threshold configs as the FSO task and delegates to `ContainerKeyMapperHelper.reprocess` with `BucketLayout.OBJECT_STORE`. Incremental processing filters the OM update batch to `keyTable` events.

Dependencies and integration: writes to the same Recon container-key tables and shared per-container count map as the FSO task. It is intended to run beside FSO so total container counts include both layouts.

Risks: hardcoded `keyTable` string can drift from OM constants. OBS and Legacy data can both be present in OM key table in other parts of Recon; this task uses `BucketLayout.OBJECT_STORE` for reprocess but incremental filtering is table-only and relies on upstream task assignment/event validity to avoid Legacy contamination.

Test signals: assert OBS reprocess only scans object-store key table, process handles only key-table events, and shared helper state is correct when paired with FSO.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskOBS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerSizeCountTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerSizeCountTask.java

Purpose: Periodic SCM-side task that bins containers by used-byte size and stores counts in the SQL `CONTAINER_COUNT_BY_SIZE` table.

Important APIs: `run`, `runTask`, test-visible `processContainers`, private `process`, `writeCountsToDB`, delete handling, and static bin-key helpers.

Control flow and persistence: `run` waits for the configured interval while `canRun`, then invokes `initializeAndRunTask`. `runTask` gets all containers from `ContainerManager`, truncates SQL counts on first run, and calls `processContainers`. The task keeps an in-memory `processedContainers` map of container ID to last size. Each pass increments counts for new/current containers, decrements previous bins on size change, ignores containers already marked `DELETED`, and decrements counts for containers missing from the latest SCM list.

Dependencies and integration: uses SCM `ContainerManager`, JOOQ DSL, generated `ContainerCountBySizeDao`, `ReconUtils.getContainerSizeUpperBound`, and `ReconTaskStatusUpdater`.

Risks: state is partly in memory; restart truncates and rebuilds from current SCM list. Negative used bytes are normalized to zero. SQL updates are read-modify-write per bin and can preserve zero/negative rows if inputs are inconsistent. The write lock protects local state but not other SQL writers.

Test signals: cover first-run truncation, deleted-container removal, size updates across bins, negative used bytes, task status update on partial failures, and SQL insert/update behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerSizeCountTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DataNodeMetricsCollectionTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DataNodeMetricsCollectionTask.java

Purpose: Callable that collects a datanode's pending deletion bytes through its JMX endpoint.

Important APIs: constructor builds a `MetricsServiceProvider` from `MetricsServiceProviderFactory`; `call` returns `DatanodePendingDeletionMetrics`; private `getJmxMetricsUrl` builds HTTP or HTTPS URL using datanode port metadata.

Control flow and state: `call` asks the metrics provider for bean `Hadoop:service=HddsDatanode,name=BlockDeletingService`, extracts `TotalPendingBlockBytes`, and returns host, UUID, and bytes. Empty or failed responses produce a metric record with `-1L`.

Dependencies and integration: uses `DatanodeInfo`, datanode HTTP/HTTPS ports, `ReconUtils.getMetricsData`, `ReconUtils.extractLongMetricValue`, and Recon's JMX metrics provider. Likely used by insight endpoints/tasks aggregating pending deletion backlog.

Risks: missing port values or unreachable JMX endpoints degrade to `-1L`, which callers must treat as unknown rather than real negative backlog. Bean/key names are string constants tied to datanode metrics implementation. The task logs failures at error level per datanode, which can be noisy during cluster-wide outages.

Test signals: mock metrics provider/factory to cover HTTP vs HTTPS URL construction, missing metrics, extraction success, provider exceptions, and absent bean fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DataNodeMetricsCollectionTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DeletedKeysInsightHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DeletedKeysInsightHandler.java

Purpose: `OmTableHandler` for OM's deleted key table. It maintains object counts and replicated/unreplicated sizes for keys pending backend deletion.

Important APIs: `handlePutEvent`, `handleDeleteEvent`, no-op `handleUpdateEvent`, and `getTableSizeAndCount`.

Control flow and persistence: incremental PUT casts the event value to `RepeatedOmKeyInfo`, adds the number of contained key infos, and adds total sizes. DELETE subtracts those values with floor-at-zero guards. Reprocess iterates `omMetadataManager.getDeletedTable()` and aggregates totals from all `RepeatedOmKeyInfo` rows.

Dependencies and integration: used by broader OM table insight tasks through the `OmTableHandler` interface. It depends on `RepeatedOmKeyInfo.getTotalSize`, table-derived metric keys from the interface, and Recon global stats maps supplied by the caller.

Risks: PUT/DELETE casts are unchecked. Reprocess assigns `unReplicatedSize += result.getRight()` and `replicatedSize += result.getLeft()`, while incremental PUT uses left for unreplicated and right for replicated; this apparent swap is a high-value correctness check. Update is no-op because deleted-key sizes are assumed immutable.

Test signals: existing `TestOmTableInsightTask` references deleted table handling. Tests should verify left/right size semantics, multi-key repeated entries, null values, and floor-at-zero delete behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DeletedKeysInsightHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountKey.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountKey.java

Purpose: Composite RocksDB key for file-size count rows, grouping by volume, bucket, and file-size upper bound.

Important APIs/types: immutable fields `volume`, `bucket`, `fileSizeUpperBound`; `getCodec`; protobuf conversion methods `toProto` and `fromProto`; value getters; `equals`, `hashCode`, and `toString`.

State and persistence: persisted with a `DelegatedCodec` over `FileSizeCountKeyProto`. The key is used in `ReconDBDefinition.FILE_COUNT_BY_SIZE` and therefore its serialized field order and presence semantics are storage compatibility concerns.

Dependencies and integration: created by `FileSizeCountTaskHelper.getFileSizeCountKey` using OM key volume/bucket and `ReconUtils.getFileSizeUpperBound`. Consumed by `ReconFileMetadataManagerImpl` for RocksDB operations.

Risks: constructor accepts null values but equality/hash/protobuf setters do not tolerate null volume/bucket/upper bound. Changing proto fields or binning semantics breaks existing RocksDB rows. The key does not include bucket layout, relying on volume/bucket identity to distinguish logical buckets.

Test signals: codec round-trip, equality/hash map behavior, and all expected file-size upper-bound bins should be covered. Tests should reject or document null handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskFSO.java

Purpose: `ReconOmTask` for file-size distribution in File System Optimized buckets.

Important APIs: constructor injection, `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess reads parallelism, memory, and flush-threshold configs, then delegates to `FileSizeCountTaskHelper.reprocess` with `BucketLayout.FILE_SYSTEM_OPTIMIZED`. Incremental process delegates to `FileSizeCountTaskHelper.processEvents` for OM `FILE_TABLE`.

Dependencies and integration: writes through `ReconFileMetadataManager`; participates in shared file-count-table truncation through the helper's static flag. Staged task wiring allows snapshot rebuilds into staged Recon DB.

Risks: static truncation coordination spans FSO and OBS; a failed reprocess can leave the truncation flag in a state that must be reset correctly. The task trusts helper read-modify-write operations for counts.

Test signals: verify config propagation, staged manager use, file-table filtering, task name, and reprocess interaction with OBS so the table is truncated once and both layouts repopulate it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskHelper.java

Purpose: Shared implementation for FSO and OBS file-size count tasks.

Important APIs: `handlePutKeyEvent`, `handleDeleteKeyEvent`, `getFileSizeCountKey`, `truncateFileCountTableIfNeeded`, `reprocess`, `reprocessBucketLayout`, `processEvents`, `writeCountsToDB`, and `buildTaskResult`.

Control flow and persistence: reprocess truncates the RocksDB file-count table once across tasks using `ReconConstants.FILE_SIZE_COUNT_TABLE_TRUNCATED`, then parallel-iterates the relevant OM key table. Each worker accumulates local `FileSizeCountKey -> delta` counts and flushes at a per-worker threshold. Incremental processing walks the OM event batch, converts PUT/DELETE/UPDATE into deltas, and writes them. `writeCountsToDB` reads existing counts, applies deltas, writes positive results, and deletes rows that fall to zero or below.

Dependencies and integration: depends on `OMMetadataManager`, `BucketLayout`, `ParallelTableIteratorOperation`, `ReconFileMetadataManager`, `ReconUtils.getFileSizeUpperBound`, and OM table constants from wrapper tasks.

Risks: read-modify-write is not atomic across concurrent callers; helper comments assume FSO and OBS write disjoint keys, but bucket names may still collide only if volume/bucket identity is unique. `processEvents` logs `value.getClass()` even when value is null, causing possible NPE on null-valued non-delete events. Runtime exceptions from `writeCountsToDB` bubble out of process/reprocess paths.

Test signals: cover concurrent worker flushes, update old/new size bins, delete missing key info, zero-row deletion, truncation reset after failure, and null event values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskOBS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskOBS.java

Purpose: `ReconOmTask` for file-size distribution in Object Store buckets.

Important APIs: constructor, `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess delegates to `FileSizeCountTaskHelper.reprocess` with `BucketLayout.OBJECT_STORE`. Incremental process filters OM events to `KEY_TABLE` and delegates to the helper.

Dependencies and integration: shares the `FILE_COUNT_BY_SIZE` table and helper-level truncation flag with `FileSizeCountTaskFSO`. Uses `ReconFileMetadataManager` for RocksDB writes.

Risks: OM key table can include Legacy and OBS concerns elsewhere in Recon; this task relies on layout-specific reprocess and table-level incremental processing. If legacy keys are still present in `KEY_TABLE` events, counts can include unintended buckets unless upstream validation partitions them.

Test signals: cover OBS key table filtering, staged manager behavior, shared truncation with FSO, and update/delete deltas for object-store keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountTaskOBS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/GlobalStatsValue.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/GlobalStatsValue.java

Purpose: Value wrapper for RocksDB global stats rows.

Important APIs/types: immutable `Long value`, `getCodec`, `getValue`, `toProto`, `fromProto`, and `toString`.

State and persistence: serialized through a `DelegatedCodec` over `GlobalStatsValueProto`. `toProto` writes null as zero, so null and zero are indistinguishable after persistence.

Dependencies and integration: used by `ReconDBDefinition.GLOBAL_STATS` and `ReconGlobalStatsManagerImpl`. It is intended for efficient single-value stats in Recon's internal RocksDB.

Risks: no `equals`/`hashCode`, so tests or maps comparing values need to compare `getValue`. Null-to-zero conversion may hide uninitialized values. There is a parallel SQL global stats path in this code area, so metric ownership must be clear.

Test signals: codec round-trip including null, string output, and manager-level batch writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/GlobalStatsValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/MultipartInfoInsightHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/MultipartInfoInsightHandler.java

Purpose: `OmTableHandler` for multipart upload info. It maintains counts and byte sizes for in-progress multipart uploads.

Important APIs: `handlePutEvent`, `handleDeleteEvent`, `handleUpdateEvent`, and `getTableSizeAndCount`.

Control flow and persistence: PUT increments object count by one and adds each part's data and replicated sizes. DELETE decrements count and subtracts each part with floor-at-zero guards. UPDATE leaves count unchanged, subtracts sizes from old parts, and adds sizes from new parts. Reprocess scans the configured multipart table and aggregates sizes from each `OmMultipartKeyInfo` part map.

Dependencies and integration: depends on `OmMultipartKeyInfo`, protobuf `PartKeyInfo`, `ReconBasicOmKeyInfo`, OM table access, and caller-provided stats maps from table insight tasks.

Risks: unchecked casts require event validator correctness. UPDATE subtraction does not floor at zero, unlike DELETE, so malformed old/new events can create negative counters. Warnings for negative sizes in DELETE are unreachable after floor-at-zero calculation because `newSize` cannot be negative. Part iteration assumes protobuf conversion succeeds for every part.

Test signals: `TestOmTableInsightTask` is the likely integration signal. Add direct tests for put/delete/update with multiple parts, missing old values, negative-counter prevention, and reprocess parity with incremental events.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/MultipartInfoInsightHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryAsyncFlusher.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryAsyncFlusher.java

Purpose: Background queue-based flusher for namespace summary reprocess workers. It merges worker-local `NSSummary` deltas with persisted summaries and propagates file deltas up ancestor chains before writing batches.

Important APIs: static `create`, `submitForFlush`, `checkForFailures`, `close`, and private `flushLoop`, `flushWithPropagation`, `propagateDeltaToAncestors`, `writeToDb`.

Control flow and persistence: workers submit maps to a bounded `LinkedBlockingQueue`, giving natural backpressure. The daemon flusher polls until stopped and queue-drained. Each batch is merged with current DB state, child-dir and metadata fields are repaired, numeric file deltas are applied, and file counts/sizes are propagated through parents found in merged map or DB. Writes use `RDBBatchOperation`.

Dependencies and integration: used by `NSSummaryTaskWithFSO` and `NSSummaryTaskWithOBS` during reprocess. It writes through `ReconNamespaceSummaryManager`.

Risks: `close` sets STOPPING and then `join`s without interrupt or timeout; if the background thread is blocked in `poll` it should wake, but a stuck DB write can hang close. Failure state rejects new submissions and may leave queued batches unprocessed. Propagation stops if an ancestor is not yet present in DB, so task phase ordering is critical.

Test signals: cover queue backpressure, DB write failure propagation, close drains all submitted batches, ancestor propagation, metadata repair, and missing-ancestor behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryAsyncFlusher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTask.java

Purpose: Top-level `ReconOmTask` that rebuilds and incrementally maintains Recon namespace summaries for FSO, Legacy, and OBS bucket layouts.

Important APIs/types: `RebuildState`, `BucketType`, constructor wiring of three subtasks, `getStagedTask`, `process`, `reprocess`, `executeReprocess`, `buildTaskResult`, and test hooks for rebuild state.

Control flow and persistence: incremental `process` runs FSO, Legacy, and OBS processors in a static three-thread executor, each with its own seek position. It returns a `TaskResult` carrying updated subtask seek positions. Reprocess uses a static `AtomicReference` to prevent concurrent rebuilds, clears the namespace summary table, and invokes the three reprocess subtasks in parallel. Success resets state to IDLE; failures set FAILED.

Dependencies and integration: depends on `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, `OzoneConfiguration`, and config keys for flush thresholds and parallelism. Upgrade actions and endpoints inspect rebuild state through test-visible/static paths.

Risks: static executor is never shut down. Returning success when another thread is already rebuilding may hide skipped work from callers expecting this invocation to rebuild. FAILED state can be retried because compare-and-set uses current state, but callers must know this behavior. Clear plus parallel rebuild means subtask ordering must ensure parent summaries exist when needed.

Test signals: `TestNSSummaryUnifiedControl`, tree precompute tests, and endpoint tests cover much of this. Add coverage for subtask seek-position recovery, duplicate rebuild request semantics, and executor failure behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskDbEventHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskDbEventHandler.java

Purpose: Shared DB/event mutation logic for namespace summary subtasks.

Important APIs: bucket cache lookup/invalidation, `handlePutKeyEvent`, reprocess variant, `handlePutDirEvent`, reprocess variant, `handleDeleteKeyEvent`, `handleDeleteDirEvent`, `flushAndCommitNSToDB`, `flushAndCommitUpdatedNSToDB`, and `propagateSizeUpwards`.

Control flow and persistence: process-mode handlers merge local map state with existing RocksDB summaries, update file counts, unreplicated and replicated sizes, file-size buckets, child-dir sets, names, and parent IDs, then batch-store/delete through `ReconNamespaceSummaryManager`. Key changes update the immediate parent and propagate deltas to ancestors. Directory changes link or unlink child directory IDs and move existing subtree totals into or out of ancestors.

Dependencies and integration: extended by FSO, Legacy, and OBS namespace tasks. Depends on `ReconOMMetadataManager` bucket lookup, `NSSummary`, `ReconUtils.getFileSizeBinIndex`, and `RDBBatchOperation`.

Risks: recursive propagation depends on correct parent IDs and can silently stop on missing summaries. Delete operations can drive negative counts if events are duplicated or summaries are stale. Reprocess-specific handlers avoid DB reads and therefore rely on later async merge. Bucket cache invalidates only on bucket delete events; missed deletes can use stale object IDs after recreate.

Test signals: test parent propagation for deep trees, delete directory with subtree totals, replicated-size sentinel `-1`, bucket cache invalidation on recreate, hard-delete cleanup, and parity between reprocess and incremental outcomes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskDbEventHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithFSO.java

Purpose: Namespace summary subtask for File System Optimized tables.

Important APIs: `getTaskTables`, `processWithFSO`, `reprocessWithFSO`, and private handlers for file table, directory table, deleted directory table, and parallel reprocess phases.

Control flow and persistence: incremental processing starts at a supplied seek position, filters to `FILE_TABLE`, `DIRECTORY_TABLE`, and `DELETED_DIR_TABLE`, applies file or directory handlers, collects hard-deleted directory object IDs, and flushes updates plus deletes when the map reaches threshold. Reprocess runs in two phases: directory table first, then file table, each parallelized with worker-local maps and `NSSummaryAsyncFlusher`. Directory skeletons are persisted before file deltas propagate.

Dependencies and integration: extends `NSSummaryTaskDbEventHandler`; uses `ParallelTableIteratorOperation`, `StringCodec`, OM file and directory tables, and `ReconNamespaceSummaryManager`.

Risks: `eventCounter` counts all events after seek, not only processed task-table events, so seek semantics must match the shared event stream. The objectIds-to-delete list is reused across flushes intentionally, which repeats delete attempts. Reprocess correctness depends on directory phase completing and closing its flusher before file phase starts.

Test signals: cover file PUT/DELETE/UPDATE, directory PUT/DELETE/UPDATE, deleted-dir hard delete, seek-position continuation, two-phase reprocess, and async flusher failure during either phase.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithLegacy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithLegacy.java

Purpose: Namespace summary subtask for Legacy buckets, supporting both object-store-like and filesystem-path behavior based on OM config.

Important APIs: `processWithLegacy`, `reprocessWithLegacy`, `processWithFileSystemLayout`, `processWithObjectStoreLayout`, `setKeyParentID`, `setParentBucketId`, and `isBucketLayoutValid`.

Control flow and persistence: incremental processing skips bucket-table events except to invalidate bucket cache on delete, processes only `KEY_TABLE`, verifies the bucket layout is LEGACY, then either treats keys ending in `OM_KEY_PREFIX` as directory markers when filesystem paths are enabled or treats all keys as bucket children when disabled. Reprocess scans the Legacy key table, filters by bucket layout, computes parent IDs, applies shared key/dir handlers, and flushes by threshold.

Dependencies and integration: uses `ReconOMMetadataManager` for bucket and parent marker lookups, `OmConfig.ENABLE_FILESYSTEM_PATHS`, `BucketLayout.LEGACY`, and `NSSummaryTaskDbEventHandler`.

Risks: filesystem-path parent reconstruction requires parent marker keys to exist; missing markers throw `IOException` and fail processing. `isBucketLayoutValid` assumes bucket lookup returns non-null. Directory names use full key names, which may matter for endpoint display. Legacy and OBS both interact with key table, so layout filtering is essential.

Test signals: cover legacy filesystem-path mode, object-store mode, missing parent marker, bucket delete/recreate cache invalidation, legacy-vs-OBS filtering, and update events that move size bins or directory markers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithOBS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithOBS.java

Purpose: Namespace summary subtask for Object Store buckets.

Important APIs: `reprocessWithOBS`, `processWithOBS`, private `processKeyTableInParallel`, and `getKeyParentID`.

Control flow and persistence: reprocess scans the object-store key table in parallel, checks each key's bucket layout from the bucket table, resolves parent object ID to the bucket object ID, accumulates worker-local summary deltas, and submits them to `NSSummaryAsyncFlusher`. Incremental processing invalidates bucket cache on bucket delete, filters to `KEY_TABLE`, validates value type, filters to OBJECT_STORE buckets, and applies key PUT/DELETE/UPDATE as bucket-child changes.

Dependencies and integration: extends the shared DB event handler, uses `ReconOMMetadataManager`, OM bucket table, `BucketLayout.OBJECT_STORE`, `ParallelTableIteratorOperation`, and `ReconNamespaceSummaryManager`.

Risks: reprocess performs bucket table lookups per key without the shared cache, which can be expensive. Process path assumes bucket lookup is non-null before calling `getBucketLayout`. OBS update assumes keys cannot move between buckets in an UPDATE event. Parent lookup failure aborts the subtask.

Test signals: cover bucket layout filtering, null bucket info, bucket delete/recreate cache invalidation, update with old value, reprocess parallel flush, and parent ID assignment to bucket object ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithOBS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdateEvent.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdateEvent.java

Purpose: Immutable data carrier for one OM RocksDB update event consumed by Recon tasks.

Important APIs/types: getters for action, table, key, value, old value, and sequence number; nested `OMUpdateEventBuilder`; and enum `OMDBUpdateAction` with PUT, DELETE, UPDATE.

State and persistence: no persistence. It transports decoded key/value objects and the batch sequence number from `OMDBUpdatesHandler` to `ReconOmTask` processors.

Dependencies and integration: built by `OMDBUpdatesHandler` after decoding RocksDB write batch entries with OM DB codecs. Consumed by container-key, file-size, namespace summary, and insight tasks.

Risks: builder setters are package-private raw-style methods, so type safety is limited inside the package. `equals` and `hashCode` ignore value, old value, and sequence number; this is suitable for de-dup by key/table/action but not full event identity. `equals` assumes updatedKey/table/action are non-null.

Test signals: cover builder output, equality semantics, sequence number propagation, and consumer handling for each action type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdateEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdatesHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdatesHandler.java

Purpose: RocksDB write-batch handler that converts OM DB write operations into decoded `OMDBUpdateEvent` instances for Recon tasks.

Important APIs: constructor with `OMMetadataManager`, `setLatestSequenceNumber`, `getLatestSequenceNumber`, overridden `put` and `delete` with column-family index, `close`, and `getEvents`.

Control flow and state: `processEvent` maps column-family index to table name, retrieves the column-family definition, decodes key and value bytes, fetches old value either from the latest event map or OM table `getSkipCache`, validates events with `OmUpdateEventValidator`, and emits PUT, DELETE, or UPDATE. `omdbLatestUpdateEvents` tracks the latest event per table/key within the batch so multiple operations collapse old-value semantics correctly. Many RocksDB handler methods are intentionally no-op because Recon only needs put/delete.

Dependencies and integration: depends on OM DB definitions/codecs, `OMMetadataManager`, RocksDB `ManagedWriteBatch.Handler`, and `OmUpdateEventValidator`. Downstream `OMUpdateEventBatch` wraps the generated events for task processing.

Risks: unsupported merge/delete-range/single-delete operations would be ignored if OM began emitting them. DELETE without an old value is skipped, so missing local state can lose delete events. `close` clears the latest-event map but intentionally leaves event list available. Generic raw tables and decoded objects rely on validator coverage.

Test signals: cover PUT new key, PUT existing key as UPDATE, PUT after DELETE in same batch, DELETE old-value capture, validation skips, non-string key warning path, close behavior, and ignored operation types if OM usage changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdatesHandler.java -->
