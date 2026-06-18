# subset-b-008053 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/ContainerDatanodeDatabase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/ContainerDatanodeDatabase.java

Purpose: `ContainerDatanodeDatabase` owns the SQLite backing store used by the container log parser commands. It creates raw per-datanode log tables, derives a latest-state table, builds indexes, and exposes query methods for state listings, container details, duplicate-open detection, replication count anomalies, unhealthy replicas, and quasi-closed-stuck candidates.

Important APIs and types: Public entry points are `createDatanodeContainerLogTable`, `createIndexes`, `insertContainerDatanodeData`, `insertLatestContainerLogData`, `listContainersByState`, `showContainerDetails`, `findDuplicateOpenContainer`, `listReplicatedContainers`, `listUnhealthyContainers`, and `listQuasiClosedStuckContainers`. It depends on `DatanodeContainerInfo`, `SQLDBConstants`, SQLite JDBC, `HddsProtos.LifeCycleState`, `ContainerHealthState`, and `OzoneConfiguration`.

Control flow: `getConnection` loads the SQLite driver and opens a local database with journal, sync, locking, cache, and temp-store settings tuned for offline bulk load. Creation methods drop/recreate source and latest tables, then build indexes. Insert paths batch `DatanodeContainerInfo` rows and reselect the latest timestamp per datanode/container into `ContainerLogTable`. Query paths run SQL, format tabular output, and optionally fetch one extra row to print a "more entries" note.

State and persistence behavior: Persistent state is two SQLite tables: `DatanodeContainerLogTable` stores every parsed transition with timestamp, BCSID, message, log level, and replica index; `ContainerLogTable` stores the latest state and BCSID per datanode/container. `showContainerDetails` reconstructs latest-per-datanode in memory, checks BCSID consistency, timestamp ordering, default replication factor, deleted/open/quasi-closed/unhealthy sets, and reports derived health labels.

Dependencies and integration points: The class is the central persistence/query layer for CLI container log commands outside this group. It consumes output from `ContainerLogFileParser`, uses SQL text from `SQLDBConstants`, and emits human-readable diagnostics to injected or system `PrintWriter`s. It relies on Ozone default replication configuration at class load time.

Risks: Timestamp comparisons are lexicographic and assume log timestamp strings sort chronologically. `DEFAULT_REPLICATION_FACTOR` parses a string setting as an integer, which is fragile if the configured value is symbolic. Health classification is heuristic and can misclassify during overlapping transitions. `insertContainerDatanodeData` is synchronized, but every batch opens a new SQLite connection, so throughput depends heavily on SQLite locking and caller concurrency.

Test signals: Good tests should cover table recreation, batching boundaries, latest-row selection, limit behavior, duplicate OPEN detection, BCSID mismatch, under/over replication, unhealthy and quasi-closed-stuck SQL, empty results, invalid replication query mode, and injection of custom writers for deterministic output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/ContainerDatanodeDatabase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/ContainerLogFileParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/ContainerLogFileParser.java

Purpose: `ContainerLogFileParser` scans extracted container log files, parses structured log lines into `DatanodeContainerInfo`, and persists parsed records through `ContainerDatanodeDatabase`.

Important APIs and types: The public API is `processLogEntries(String, ContainerDatanodeDatabase, int)`. Internally it uses `Files.walk`, a fixed thread pool, `CountDownLatch`, an `AtomicBoolean` failure flag, and a private `processFile` parser. It recognizes `ID`, `BCSID`, `State`, and `Index` key-value fields split by `" | "`.

Control flow: The directory walk collects regular files, derives the datanode ID from the substring after `.log.`, and submits each valid file to the executor. `processFile` reads lines as UTF-8, extracts timestamp and log level from the first two fields, parses key-value fields, treats non-key fields as an error/message string, filters to `Index=0`, batches up to 5000 entries, and inserts each batch.

State and persistence behavior: The parser itself stores only the `hasErrorOccurred` flag and per-file batch lists. Durable state is delegated to SQLite through `insertContainerDatanodeData`. Invalid filenames are skipped with console messages; malformed lines without an ID are logged but do not abort.

Dependencies and integration points: It integrates with the database utility and expects log naming in the form containing `.log.<datanodeId>`. It is part of the container log debug pipeline that first creates tables, then parses files, then derives latest-state rows.

Risks: `line.split` assumes every line has timestamp and log-level fields; short or malformed lines can throw unchecked exceptions and mark the worker failed. Latch count is initialized to all regular files, including skipped invalid names, but skipped files do not count down, so invalid filenames can deadlock. The thread pool is shut down only after latch wait. The index filter currently excludes EC/non-zero replica index data.

Test signals: Tests should include multiple files, invalid filenames, empty datanode IDs, malformed lines, non-zero index filtering, batch flush at and below 5000, propagated SQL failure, and no hang when files are skipped.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/ContainerLogFileParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/DatanodeContainerInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/DatanodeContainerInfo.java

Purpose: `DatanodeContainerInfo` is an immutable value object representing one parsed container log event for a datanode.

Important APIs and types: It exposes a nested `Builder` with setters for container ID, datanode ID, timestamp, state, BCSID, error message, log level, and index value, plus getters for all fields.

Control flow: Construction is builder-only. The builder stores mutable interim values, and `build` copies them into final fields without validation.

State and persistence behavior: The object is in-memory only but directly maps to columns in `DatanodeContainerLogTable`. Default primitive values are zero if parser code does not set them; strings can remain null.

Dependencies and integration points: It is produced by `ContainerLogFileParser`, consumed by `ContainerDatanodeDatabase`, and re-created from SQL query results for health analysis.

Risks: Lack of validation means partially parsed events can become database rows. There is no equals/hashCode/toString, so debugging and collection comparisons need custom field checks.

Test signals: Builder round-trip tests should verify all fields, default unset values, and database insert/query compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/DatanodeContainerInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/SQLDBConstants.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/SQLDBConstants.java

Purpose: `SQLDBConstants` centralizes SQLite driver settings, table names, batch/cache sizes, lifecycle/health state constants, DDL, DML, query SQL, and index SQL for the container log database.

Important APIs and types: Constants include `DEFAULT_DB_FILENAME`, `DRIVER`, `CONNECTION_PREFIX`, `CACHE_SIZE`, `BATCH_SIZE`, table names, create/drop/insert SQL, latest-state queries, health queries, and replication queries. It imports `HddsProtos` and `ContainerHealthState` to derive state strings.

Control flow: There is no runtime flow beyond static constant initialization. The private constructor prevents instantiation.

State and persistence behavior: These strings define the SQLite schema and therefore the persisted shape of parsed container-log diagnostics. The latest table uses a `(datanode_id, container_id)` primary key and `INSERT OR REPLACE`.

Dependencies and integration points: `ContainerDatanodeDatabase` uses every major SQL constant. The queries encode assumptions about latest timestamps, state names, deleted replicas, and a hard-coded quasi-closed threshold of at least three replicas.

Risks: SQL is assembled with string replacement for the replication operator; current callers restrict it but the pattern is brittle. The quasi-closed query uses `>= 3` instead of the configurable default replication factor. Latest-state joins may duplicate rows if multiple events share an identical timestamp.

Test signals: Tests should verify table creation, primary-key replacement, index creation, latest selection, state string compatibility, hard-coded threshold behavior, and operator replacement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/SQLDBConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.ozone.debug.logs.container.utils` contains classes used by the Ozone container log parser tool.

Important APIs and types: It declares package-level Javadoc only; there are no methods, state, or executable paths.

Control flow and state: None.

Dependencies and integration points: The documentation covers `ContainerLogFileParser`, `ContainerDatanodeDatabase`, `DatanodeContainerInfo`, and `SQLDBConstants`.

Risks and test signals: The only risk is stale package documentation if the utility package grows beyond container log parsing. No direct test is needed beyond Javadoc/package compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/package-info.java

Purpose: This package descriptor marks `org.apache.hadoop.ozone.debug.logs` as the command area for parsing and analyzing extracted logs.

Important APIs and types: It contains only package-level Javadoc.

Control flow and state: None.

Dependencies and integration points: It describes the broader log debug namespace that includes container log parsing commands and utilities.

Risks and test signals: Stale documentation is the only meaningful risk. Package compilation is the only direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/CompactionLogDagPrinter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/CompactionLogDagPrinter.java

Purpose: `CompactionLogDagPrinter` implements the `ozone debug om generate-compaction-dag` offline command, reading OM RocksDB compaction-log entries and rendering a PNG of the backward compaction DAG.

Important APIs and types: It is a picocli `Callable<Void>` subcommand with inherited `OMDebug --db` and required `--output-file`. It uses `RocksDBUtils`, `ManagedRocksDB`, `ManagedRocksIterator`, `COMPACTION_LOG_TABLE`, `HddsProtos.CompactionLogEntryProto`, `CompactionLogEntry`, `CompactionDag`, and `PrintableGraph`.

Control flow: `call` opens OM RocksDB read-only with discovered column families, resolves the compaction log column family handle, iterates all rows, parses protobuf values, feeds input/output file lists and sequence numbers into `CompactionDag`, then calls `pngPrintMutableGraph`.

State and persistence behavior: The command does not mutate OM DB. It writes only the requested PNG. All graph state is transient in `CompactionDag` and `PrintableGraph`.

Dependencies and integration points: It integrates OM RocksDB metadata, the rocks diff compaction DAG model, and the graph rendering helper in `org.apache.ozone.graph`.

Risks: Column family discovery or missing compaction-log handles can fail at runtime. Invalid protobuf data is wrapped in `RuntimeException`. Empty DAGs cause `PrintableGraph.generateImage` to throw. Column family handles are collected but not explicitly closed in this method.

Test signals: Tests should cover successful image generation, empty graph failure, invalid output path, malformed compaction log value, and missing column family behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/CompactionLogDagPrinter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/ContainerToKeyMapping.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/ContainerToKeyMapping.java

Purpose: `ContainerToKeyMapping` implements the offline `ozone debug om container-key-mapping` command. Given a comma-separated set of container IDs, it scans an OM RocksDB and emits JSON mapping each container to committed keys, optional in-progress keys, and unreferenced FSO key counts.

Important APIs and types: Public behavior is through `call`. It uses `OMDBDefinition` table definitions for volumes, buckets, directories, files, object-store keys, open files/keys, and multipart uploads. It builds a temporary `omdirtree.db` using `DBStoreBuilder`, `LongCodec`, `StringCodec`, and a `dirTreeTable`. Helper APIs include `getKeyContainers`, `prepareDirIdTree`, `reconstructFullPath`, `getDirParentNamePair`, and `jsonOutput`.

Control flow: `call` parses container IDs, opens OM DB read-only with `NO_CACHE`, initializes table handles, and delegates to `retrieve`. `retrieve` optionally builds a directory tree for full FSO path reconstruction, initializes output maps, optionally scans open file, open key, and multipart tables, then scans committed FSO file and OBS key tables. Each key's block locations are checked against target containers, paths are normalized, and Jackson writes a deterministic JSON object keyed by container ID.

State and persistence behavior: OM DB is read-only. The only write is a temporary local `omdirtree.db` next to the OM DB, deleted before and after use. Runtime state includes the volume ID cache, bucket-to-volume map, container-to-key maps, open-key maps, and unreferenced-count map. Missing FSO parent directories increment `unreferencedKeys` instead of producing a path.

Dependencies and integration points: The command is registered under `OMDebug`, consumes OM metadata table formats for both FSO and OBS buckets, and surfaces block-to-key relationships for container forensics. Tests in this group seed `OmMetadataManagerImpl` tables and execute the command through `OzoneDebug`.

Risks: The temporary DB is placed beside the inspected OM DB, so permissions and cleanup matter. `--onlyFileNames` does not affect open keys or multipart keys, which retain table-key format. FSO path reconstruction depends on directory table completeness and `name#parent` serialization. Errors during scans are printed and swallowed, yielding partial JSON.

Test signals: Existing tests cover FSO paths, OBS keys, only-file-name mode, open FSO/OBS keys, multipart uploads, missing containers, and unreferenced FSO files. Additional useful tests would cover duplicate container IDs, invalid numeric input, temporary DB cleanup on exceptions, and multiple blocks per key across containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/ContainerToKeyMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/OMDebug.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/OMDebug.java

Purpose: `OMDebug` is the service-provider entry point for OM-related `ozone debug` subcommands.

Important APIs and types: It implements `DebugSubcommand`, is annotated with `@MetaInfServices`, and declares picocli subcommands `CompactionLogDagPrinter`, `PrefixParser`, and `ContainerToKeyMapping`. It exposes inherited `--db` through `getDbPath`.

Control flow: Picocli instantiates this parent command, parses the required `--db` option with inherited scope, and subcommands read the configured path from `parent.getDbPath()`.

State and persistence behavior: It stores only the CLI-provided OM RocksDB path. It performs no direct IO.

Dependencies and integration points: The class is discovered by the extensible debug command framework and groups offline OM DB tools.

Risks and test signals: Missing or invalid `--db` handling is delegated to subcommands. Tests should confirm command registration, inherited option parsing, and that each child sees the same DB path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/OMDebug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/PrefixParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/PrefixParser.java

Purpose: `PrefixParser` implements `ozone debug om prefix`, an offline helper for inspecting FSO bucket metadata below a given prefix path in an OM DB.

Important APIs and types: It is a picocli `Callable<Void>` with required `--path`, `--bucket`, and `--volume`. Key APIs include `parse`, `dumpTableInfo`, `dumpInfo`, `getPrefixFilter`, `getParserStats`, and the `Types` enum. It uses `OmMetadataManagerImpl`, `OzoneManagerUtils.getResolvedBucketInfo`, `BucketLayout`, `KeyPrefixFilter`, and OM directory/file tables.

Control flow: `parse` validates the DB path, starts an OM metadata manager pointed at the DB directory, checks volume and bucket existence, rejects non-FSO buckets, then walks each path element by constructing OM ozone path keys from the current parent object ID. If a directory component is missing, it records a non-existent directory and dumps entries at the last valid level. It finally scans directory and file tables with a prefix filter.

State and persistence behavior: The command is read-only against OM DB. It maintains `parserStats` counters in memory and prints details to stdout, including type, effective path, DB key, object ID, and parent ID.

Dependencies and integration points: It depends on OM metadata manager table semantics for FSO object IDs and is registered under `OMDebug`.

Risks: `main` constructs `PrefixParser` without a parent, so direct invocation can dereference null unless callers use `parse` directly. `getRangeKVs` is capped at 1000 entries. Output uses `System.out` rather than command writer helpers. The path iterator and `key.getName(1)` assume a specific encoded key layout.

Test signals: Useful tests should cover invalid DB path, invalid volume, invalid bucket, OBS bucket rejection, existing nested path, missing directory, stats counters, and table-scan cap behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/PrefixParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.debug.om` as the home of OM debug commands.

Important APIs and types: It contains only package Javadoc and the package declaration.

Control flow and state: None.

Dependencies and integration points: It describes the namespace containing the OM debug parent and offline OM DB commands.

Risks and test signals: Staleness is the only practical risk. Package compilation is the direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/package-info.java

Purpose: This package descriptor documents the root `org.apache.hadoop.ozone.debug` package as Ozone debug tooling.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It covers the root debug command namespace used by service-loaded debug subcommands.

Risks and test signals: Only documentation drift is relevant. Package compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/RatisDebug.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/RatisDebug.java

Purpose: `RatisDebug` registers Ratis-related `ozone debug` commands.

Important APIs and types: It implements `DebugSubcommand`, is discovered through `@MetaInfServices`, and declares `RatisLogParser` as its subcommand.

Control flow and state: The class has no fields or methods beyond picocli metadata; picocli routes execution to the `parse` child command.

Dependencies and integration points: It integrates the Ratis parser into the generic `OzoneDebug` command tree.

Risks and test signals: Command registration is the main behavior to test. Functional parsing behavior lives in `RatisLogParser`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/RatisDebug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.debug.ratis` as the Ratis debug command namespace.

Important APIs and types: It contains only package-level Javadoc.

Control flow and state: None.

Dependencies and integration points: It describes the package containing the Ratis debug parent command.

Risks and test signals: Documentation drift is the only risk; compilation is the only direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/BaseLogParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/BaseLogParser.java

Purpose: `BaseLogParser` is the shared implementation for dumping Ratis segment files through Apache Ratis' `ParseRatisLog`.

Important APIs and types: It defines required CLI option `--segmentPath/--segment-path`, method `parseRatisLogs(Function<StateMachineLogEntryProto,String>)`, and testing setter `setSegmentFile`.

Control flow: `parseRatisLogs` builds a `ParseRatisLog.Builder`, sets the segment file and optional state-machine log string converter, builds a parser, and calls `dumpSegmentFile`.

State and persistence behavior: It stores only the segment file path and reads the segment through the Ratis parser. It does not write persistent data.

Dependencies and integration points: `RatisLogParser` supplies role-specific state-machine log converters for OM, SCM, datanode, or generic parsing.

Risks: Exceptions are caught and printed to stdout instead of propagated, so CLI exit status can report success even when parsing failed. The error message references `RatisLogParser` regardless of subclass.

Test signals: Tests should verify builder invocation through actual or fixture segment files, converter selection, `setSegmentFile`, and failure reporting behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/BaseLogParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/RatisLogParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/RatisLogParser.java

Purpose: `RatisLogParser` implements `ozone debug ratis parse`, selecting a state-machine decoder for OM, SCM, datanode, or generic Ratis log output.

Important APIs and types: It extends `BaseLogParser`, implements `Callable<Void>`, has `--role`, and uses `OMRatisHelper`, `SCMRatisRequest`, `ContainerStateMachine`, `StateMachineLogEntryProto`, and a dummy `RaftGroupId` for datanode log decoding.

Control flow: `call` lowercases `role`, prints the selected mode, and calls `parseRatisLogs` with the appropriate converter: OM, SCM, datanode container command decoder, or null for generic output. `smToContainerLogString` wraps the datanode converter with the dummy pipeline ID.

State and persistence behavior: The command reads the segment file and prints decoded entries. It has no durable state.

Dependencies and integration points: It is registered by `RatisDebug` and relies on Ratis tooling plus Ozone component-specific state-machine log translators.

Risks: Unknown roles silently fall back to generic parsing. Datanode parsing uses a dummy pipeline ID and null context, so output is diagnostic rather than exact runtime replay. Failures are swallowed by `BaseLogParser`.

Test signals: Tests should cover role dispatch, converter output for representative entries, generic fallback, datanode dummy ID notice, and segment parsing failure behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/RatisLogParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/package-info.java

Purpose: This package descriptor documents command-line utilities for dumping Ratis log files.

Important APIs and types: It declares only package Javadoc.

Control flow and state: None.

Dependencies and integration points: It describes the package containing `BaseLogParser` and `RatisLogParser`.

Risks and test signals: Documentation drift is the only risk; compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockExistenceVerifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockExistenceVerifier.java

Purpose: `BlockExistenceVerifier` implements the `blockExistence` replica verification check by making `getBlock` calls to a chosen datanode for each key location.

Important APIs and types: It implements `ReplicaVerifier`, creates a `ContainerOperationClient` and `XceiverClientManager`, uses `Pipeline.copyForReadFromNode`, `ContainerProtocolCalls.getBlock`, `OmKeyLocationInfo`, and `BlockVerificationResult`.

Control flow: `verifyBlock` builds a pipeline targeting the given datanode, acquires a read client, calls `getBlock` with block ID, token, and replica indexes, treats a response with `BlockData` as pass, otherwise returns a completed failed check, and releases the client in `finally`.

State and persistence behavior: The verifier has no persistence; state is the network client manager and response result.

Dependencies and integration points: It is selected by `ReplicasVerify --block-existence` and runs against a live cluster through SCM/datanode container protocols.

Risks: The `finally` releases `client` even if acquisition failed; release behavior must tolerate null. IO failures are marked incomplete rather than failed checks. Correctness depends on the key location token and pipeline metadata being current.

Test signals: Tests should cover pass, missing block data, IO exception, client release, and correct targeting of a single datanode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockExistenceVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockVerificationResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockVerificationResult.java

Purpose: `BlockVerificationResult` is the JSON-facing result model for one replica check.

Important APIs and types: It stores `completed`, `pass`, and `failures`, and offers factories `pass`, `failCheck`, and `failIncomplete`.

Control flow and state: Instances are immutable after construction. `failCheck` means the check completed and found bad data; `failIncomplete` means the verifier could not complete due to an operational error.

Dependencies and integration points: `ReplicasVerify` serializes these values into each replica's `checks` array and uses `passed()` to compute block/key pass state.

Risks: Failure lists are not defensively copied, though factories use immutable singleton/empty lists. There is no typed reason code beyond message text.

Test signals: Tests should assert factory semantics, getters, and serialization shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockVerificationResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ChecksumVerifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ChecksumVerifier.java

Purpose: `ChecksumVerifier` implements the `checksum` replica verification check by streaming a block from a specific datanode and relying on the client read path to validate checksums.

Important APIs and types: It implements `ReplicaVerifier`, uses `BlockInputStreamFactoryImpl`, `OzoneClientConfig`, `Pipeline.copyForReadFromNode`, `IOUtils.copyLarge`, `NullOutputStream`, and `OzoneChecksumException`.

Control flow: `verifyBlock` builds a single-datanode read pipeline, opens a block input stream with the key location token and replication config, copies the entire stream to a null sink, returns pass on completion, returns `failCheck` when the root cause is an `OzoneChecksumException`, and returns `failIncomplete` for other IO failures.

State and persistence behavior: It performs no writes. It holds configuration and container client manager state for repeated checks.

Dependencies and integration points: It is selected by `ReplicasVerify --checksums` and exercises the same client-side checksum path used by data reads.

Risks: Full data streaming can be expensive for large key sets. Only IO exception causes are inspected, so nested checksum causes outside the immediate cause may be missed. Operational read failures are incomplete rather than data failures.

Test signals: Tests should cover checksum exception classification, non-checksum IO classification, successful stream drain, and single-datanode pipeline selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ChecksumVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ContainerStateVerifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ContainerStateVerifier.java

Purpose: `ContainerStateVerifier` implements the `containerState` replica verification check, combining datanode-reported container state, SCM container state, and SCM replica-count health.

Important APIs and types: It implements `ReplicaVerifier`, uses `ContainerOperationClient`, `XceiverClientManager`, Guava `Cache<Long, ContainerInformation>`, `ContainerProtocolCalls.readContainer`, `ContainerInfo`, `ContainerReplicaInfo`, `ContainerHealthResult`, and `BlockVerificationResult`.

Control flow: For each block replica, it fetches container information from SCM or cache, reads container data from the target datanode using the encoded token, compares replica state and SCM lifecycle state against allowed sets, computes a replication status from SCM replica information, and passes only when replication is healthy and both states are acceptable.

State and persistence behavior: The verifier is read-only. Runtime state is a bounded container info cache, including SCM lifecycle state, encoded token, and computed replication status. Invalid cache size falls back to one million entries with a stderr warning.

Dependencies and integration points: It is selected by `ReplicasVerify --container-state`, shares SCM/datanode clients with other replica checks, and reports container-level replication problems on every replica output for that container.

Risks: Replica-count health is simplified to non-`UNHEALTHY` string comparisons and required-node count; it may not reflect full SCM placement policy. Cache entries can become stale during a long-running command. `IOException` message matching for missing containers is string-based.

Test signals: Tests should cover good states, bad replica states, bad SCM states, missing container data, missing container exception classification, cache hit/miss, invalid cache size fallback, under/over replication text, and SCM replica fetch failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ContainerStateVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicaVerifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicaVerifier.java

Purpose: `ReplicaVerifier` is the common interface for per-replica block checks used by `ReplicasVerify`.

Important APIs and types: It declares `verifyBlock(DatanodeDetails, OmKeyLocationInfo)` and `getType()`.

Control flow and state: Implementations perform the actual work. The interface defines no state.

Dependencies and integration points: Implemented by block existence, checksum, and container state verifiers. `ReplicasVerify` stores a list of these implementations and serializes each result under its type.

Risks and test signals: Adding a verifier requires stable `getType` strings for JSON and summary counters. Tests should verify each implementation conforms to the pass/completed semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicaVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasDebug.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasDebug.java

Purpose: `ReplicasDebug` registers replica-oriented debug commands under `ozone debug replicas`.

Important APIs and types: It implements `DebugSubcommand`, uses `@MetaInfServices`, and declares subcommands `ChunkKeyHandler` and `ReplicasVerify`.

Control flow and state: The parent command has no fields or direct execution path. Picocli routes to child commands.

Dependencies and integration points: It integrates live-cluster replica diagnostics into the generic Ozone debug command framework.

Risks and test signals: Command registration and help output are the main direct behaviors to test. Operational risks live in the child commands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasDebug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasVerify.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasVerify.java

Purpose: `ReplicasVerify` implements `ozone debug replicas verify`, a live-cluster command that scans keys under a key, bucket, volume, or all volumes and runs selected replica verification checks.

Important APIs and types: It extends shell `Handler`, mixes in `ScmOption` and `ShellReplicationOptions`, accepts an Ozone URI, `--all-results`, grouped verification flags `--checksums`, `--block-existence`, `--container-state`, and `--container-cache-size`. It uses `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneKey`, `OmKeyInfo`, `OmKeyLocationInfo`, `ReplicaVerifier`, `JsonUtils`, counters, and a shutdown hook.

Control flow: `execute` determines verification scope from URI depth, constructs the requested verifier list, registers a shutdown hook, then calls `findCandidateKeys`. The scan walks the addressed key, bucket, volume, or all volumes; directory marker keys ending in `/` are skipped. `processKey` fetches key info from OM, filters by replication options, iterates latest block locations, iterates each pipeline datanode, runs every verifier, writes nested JSON for blocks/replicas/checks, aggregates failed verification types, and includes the key only if it failed or `--all-results` is set.

State and persistence behavior: The command does not mutate Ozone. Runtime state includes counters for processed volumes, buckets, keys, passed/failed keys, per-type failure counters, start/end times, selected verification types, and any thrown exception. It prints JSON to stdout and summary information to stderr through the shutdown hook.

Dependencies and integration points: It integrates Ozone shell address parsing, OM key lookup, SCM/datanode clients through verifier implementations, replication filters, and the global shutdown hook manager.

Risks: If no verification flag is supplied, the arg group may still allow an empty verifier list depending on picocli binding; keys would pass without checks. Full namespace scans can be expensive and network-heavy. The shutdown hook may print summaries on normal JVM exit as well as interruption. EC/Ratis filtering requires exact replication type and factor match.

Test signals: Useful tests cover scope selection, replication filtering, key/bucket/volume/all-volumes walking, directory-marker skip, JSON pass/fail structure, summary counters, all-results behavior, per-type failure counting, verifier exception propagation, and shutdown-hook summary timing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasVerify.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkKeyHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkKeyHandler.java

Purpose: `ChunkKeyHandler` implements `ozone debug replicas chunk-info`, returning per-datanode chunk location, block metadata, checksums, and EC chunk type for an existing key.

Important APIs and types: It extends `KeyHandler`, uses OM `lookupKey`, `OmKeyInfo`, `OmKeyLocationInfo`, `ContainerOperationClient`, `XceiverClientManager`, `ContainerProtocolCalls.getBlock`, `readContainerFromAllNodes`, `ContainerLayoutVersion`, Jackson streaming `JsonGenerator`, `ECReplicationConfig`, and `ChunkType`.

Control flow: The command resolves the key address, fetches latest key locations, rejects keys with no locations, chooses a read pipeline, reads container metadata from all nodes, gets block data, computes the chunk file path from each datanode's container path and configured layout, emits datanode identity and block/chunk fields, serializes checksum arrays and stripe checksums, and annotates EC replicas as data or parity based on replica index.

State and persistence behavior: It is read-only against OM and datanodes. Output is streamed JSON to stdout; errors for individual datanodes go to stderr and processing continues.

Dependencies and integration points: Registered under `ReplicasDebug`, it links OM key metadata with datanode container storage layout to show the physical chunk file path.

Risks: The acquired `xceiverClient` is tied to a pipeline but the loop intends per-datanode behavior; `getBlock` may not actually retarget for each datanode in the loop. `readContainerResponses.get(datanodeDetails)` can be null. Stripe checksum handling assumes checksum data exists and has at least one checksum. For large keys, output can be large.

Test signals: Tests should cover zero-location keys, Ratis and EC pipelines, data/parity classification, checksum and stripe checksum serialization, missing block response, missing read-container response, and correct file path for file-per-block/file-per-chunk layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkType.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkType.java

Purpose: `ChunkType` labels erasure-coded key chunks as `DATA` or `PARITY`.

Important APIs and types: It is a two-value enum used by `ChunkKeyHandler`.

Control flow and state: There is no behavior or mutable state. `ChunkKeyHandler` chooses `PARITY` when the EC replica index is greater than the data count, otherwise `DATA`.

Dependencies and integration points: It appears in chunk-info JSON output for EC keys.

Risks and test signals: The enum is stable, but classification depends on correct one-based replica index handling. Tests should validate boundary indexes around the data/parity split.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/package-info.java

Purpose: This package descriptor documents the replica chunk-info debug package.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It describes the namespace containing `ChunkKeyHandler` and `ChunkType`.

Risks and test signals: Documentation drift is the only risk; compilation is enough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/package-info.java

Purpose: This package descriptor documents the replica debug command package.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It describes the namespace containing the replica verifier command framework and chunk-info tools.

Risks and test signals: Documentation drift is the only risk; compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/BlockIdDetails.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/BlockIdDetails.java

Purpose: `BlockIdDetails` is a simple fsck data carrier describing which volume, bucket, and key own a block.

Important APIs and types: It has getters and setters for `bucketName`, `blockVol`, and `keyName`, plus `toString`, `equals`, and `hashCode`.

Control flow and state: It is mutable and stores only three string fields.

Dependencies and integration points: `ContainerMapper` creates instances while mapping container IDs and local block IDs back to OM key metadata.

Risks: Field name `blockVol` is less clear than volume name. Mutability means map values can be changed after insertion. There is no JSON annotation, so Jackson uses bean naming.

Test signals: Tests should verify equality, hash code, string format if relied upon, and JSON serialization shape through `ContainerMapper`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/BlockIdDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/ContainerMapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/ContainerMapper.java

Purpose: `ContainerMapper` is a small offline fsck utility that scans an OM DB and builds a JSON mapping from container ID to local block IDs and owning key details.

Important APIs and types: Entry points are `main(String[])` and `parseOmDB(OzoneConfiguration)`. It uses `OmMetadataManagerImpl`, the default-layout key table, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `OmKeyLocationInfo`, `BlockIdDetails`, and Jackson `ObjectMapper`.

Control flow: `main` reads the OM DB path from `args[0]`, sets `OZONE_OM_DB_DIRS`, calls `parseOmDB`, and prints JSON. `parseOmDB` opens metadata manager, iterates the default key table, round-trips each `OmKeyInfo` through protobuf, walks every key-location version and block location, and appends a map of local block ID to `BlockIdDetails` under each container ID.

State and persistence behavior: It is read-only. Runtime state is a nested `Map<Long, List<Map<Long, BlockIdDetails>>>`. The metadata manager is stopped in `finally`.

Dependencies and integration points: It depends on OM DB table layout for default buckets only; FSO buckets are not covered by `getBucketLayout()`.

Risks: `args[0]` is read before null/length validation. Protobuf round-trip is redundant and can throw parsing errors. The nested list-of-single-entry-maps is awkward for consumers. FSO/OBS mixed deployments may be partially mapped.

Test signals: Tests should cover missing DB config, empty key table, multiple blocks per key, multiple keys per container, default bucket-only behavior, and JSON output shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/ContainerMapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/package-info.java

Purpose: This package descriptor documents the fsck tool package.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It describes the namespace containing `ContainerMapper` and `BlockIdDetails`.

Risks and test signals: Documentation drift is the only risk; compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/utils/Filter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/utils/Filter.java

Purpose: `Filter` is a generic model for representing one comparison operation, value, and optional nested filter map.

Important APIs and types: It exposes constructors accepting `FilterOperator` or string operator names, getters/setters, `getFilterOperator`, `toString`, and enum values `EQUALS`, `LESSER`, `GREATER`, and `REGEX`.

Control flow and state: Instances are mutable. String operator parsing is a simple case-insensitive if/else chain and returns null for unknown operators.

Dependencies and integration points: This utility can represent nested record filters for debug/query tooling, although no direct consumer appears in the listed files.

Risks: Unknown operators silently become null. `value` is `Object`, so consumers need type checks. `nextLevel` defaults to null and is mutable. There is no validation for incompatible operator/value combinations.

Test signals: Tests should cover all operator strings, unknown operator handling, nested filters, mutators, and `toString`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/utils/Filter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/utils/package-info.java

Purpose: This package descriptor documents utility classes for Ozone.

Important APIs and types: It contains only package-level Javadoc.

Control flow and state: None.

Dependencies and integration points: It covers utility classes such as `Filter`.

Risks and test signals: Documentation drift is the only risk; compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/Edge.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/Edge.java

Purpose: `Edge` customizes graph rendering by suppressing edge labels in generated compaction DAG images.

Important APIs and types: It extends JGraphT `DefaultEdge` and overrides `toString` to return an empty string.

Control flow and state: There is no state beyond `DefaultEdge` internals. Rendering code uses the string representation as the label.

Dependencies and integration points: `PrintableGraph` uses `DefaultDirectedGraph<String, Edge>` so PNG output does not show source/target text on edges.

Risks and test signals: Behavior is intentionally minimal. Tests can assert `new Edge().toString().isEmpty()` indirectly through clean graph render labels if image inspection is available.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/Edge.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/PrintableGraph.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/PrintableGraph.java

Purpose: `PrintableGraph` converts a Guava `MutableGraph<CompactionNode>` into a JGraphT graph and writes a hierarchical PNG image.

Important APIs and types: Constructor accepts a Guava graph and `GraphType`. Public methods are `generateImage` and `getGraph`. It uses `DefaultDirectedGraph`, `JGraphXAdapter`, `mxHierarchicalLayout`, `mxCellRenderer`, `ImageIO`, `CompactionNode`, and custom `Edge`.

Control flow: Construction calls `getGraph`, which adds vertices for every compaction node and directed edges for every Guava edge. `generateImage` rejects an empty graph, lays out the JGraphX adapter hierarchically, renders a white-background image at scale 2, and writes it as PNG.

State and persistence behavior: Runtime state is the converted JGraphT graph. Persistent output is the image file path supplied by the caller.

Dependencies and integration points: `CompactionLogDagPrinter` uses this wrapper to render OM compaction DAGs. `TestPrintableGraph` validates empty and non-empty graph outputs for all graph type labels.

Risks: Vertex labels can collide when graph type reduces nodes to equal strings, causing merged vertices. Image generation depends on AWT/ImageIO availability. `generateImage` writes directly to the requested path without creating parent directories.

Test signals: Existing tests cover empty graph error and file creation for all `GraphType` values. Additional tests could assert vertex labels and edge count in `getGraph`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/PrintableGraph.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/package-info.java

Purpose: This package descriptor documents generic Ozone graph classes, although the source path is `org/apache/ozone/package-info.java` and the declared package is `org.apache.ozone.graph`.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It documents the graph helper package used by compaction DAG rendering.

Risks and test signals: The path/package mismatch is notable for source-tree tooling even though Java permits package declarations independent of file directories if the compiler source root includes this file. Compilation is the direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestCheckNative.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestCheckNative.java

Purpose: `TestCheckNative` verifies `ozone debug checknative` output for native library availability.

Important APIs and types: It uses `OzoneDebug`, `GenericTestUtils.PrintStreamCapturer`, `ROCKS_TOOLS_NATIVE_PROPERTY`, JUnit conditional annotations, and AssertJ.

Control flow: Each test captures stdout, executes `new OzoneDebug().getCmd().execute("checknative")`, normalizes repeated spaces, and checks expected library lines. One test runs when rocks-tools native is not enabled; the other runs when the system property is true.

State and persistence behavior: No persistence. It mutates only captured process stdout and closes the capturer after each test.

Dependencies and integration points: It is a CLI integration test for the debug command registry and native-check reporting.

Risks: The assertions encode expected false values for Hadoop, ISA-L, and OpenSSL in the test environment. Environment-specific native library loading can change test applicability.

Test signals: Required signals are header text and exact `rocks-tools` boolean matching the system property condition.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestCheckNative.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestDBDefinitionFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestDBDefinitionFactory.java

Purpose: `TestDBDefinitionFactory` verifies that debug DB definition lookup returns the expected `DBDefinition` implementation for OM, SCM, Recon, and datanode schema versions.

Important APIs and types: It uses `DBDefinitionFactory.getDefinition`, `setDnDBSchemaVersion`, `OMDBDefinition`, `SCMDBDefinition`, `ReconSCMDBDefinition`, `ReconDBDefinition`, `DatanodeSchemaOneDBDefinition`, `DatanodeSchemaTwoDBDefinition`, and `DatanodeSchemaThreeDBDefinition`.

Control flow: A single test requests definitions by DB name and by datanode DB path/config after setting schema version to V2, V1, and V3, asserting the returned class each time.

State and persistence behavior: It uses no real DB. It does mutate global/static datanode schema selection in `DBDefinitionFactory`.

Dependencies and integration points: This protects the `ozone debug db` family of commands that need the right column-family definitions for each DB flavor.

Risks: Static schema version state can leak to later tests if not reset elsewhere. The datanode path is `/tmp/test-container.db` but no filesystem access is expected.

Test signals: Exact class identity for all supported database definition cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestDBDefinitionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/audit/parser/TestAuditParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/audit/parser/TestAuditParser.java

Purpose: `TestAuditParser` is the regression suite for the audit log parser CLI, covering load, built-in templates, custom SQL query, error propagation, and help output.

Important APIs and types: It uses `AuditParser`, picocli `CommandLine`, custom `IExceptionHandler2`, test resources `testaudit.log` and `testloadaudit.log`, temporary output directories, captured `System.out/err`, and AssertJ/JUnit assertions.

Control flow: `@BeforeAll` creates temp DB paths and loads the primary audit log. Each test redirects stdout/stderr, executes parser arguments through picocli handlers that rethrow parse/execution failures, and asserts output content. Tests query top commands, top users, top active seconds, arbitrary SQL count, invalid load behavior, and help text.

State and persistence behavior: The suite creates a SQLite audit DB in a temp directory and deletes the output base directory after all tests. Static stdout buffer `OUT` and parser instance are reused and reset per test.

Dependencies and integration points: It tests the audit parser command surface that lives outside this work item but is part of cli-debug.

Risks: The invalid load test expects an `ArrayIndexOutOfBoundsException` cause, which is brittle and exposes parser internals. Static buffers and parser state can leak if reset fails.

Test signals: Exact template rows, query count `12`, expected help usage prefix, and expected exception type/message for malformed load input.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/audit/parser/TestAuditParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/audit/parser/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/audit/parser/package-info.java

Purpose: This test package descriptor documents audit parser tests.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It describes the test namespace containing `TestAuditParser`.

Risks and test signals: Documentation drift is the only risk; test compilation is the direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/audit/parser/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/kerberos/TestOzoneDebugKerberos.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/kerberos/TestOzoneDebugKerberos.java

Purpose: `TestOzoneDebugKerberos` validates the `ozone debug kerberos` diagnostics and principal translation command surfaces.

Important APIs and types: It uses `OzoneDebug`, `GenericTestUtils` output capturers, AssertJ, and system property `java.security.krb5.conf`.

Control flow: Each test captures stdout/stderr, executes either `kerberos diagnose` or `kerberos translate-principal testuser/host@EXAMPLE.COM`, normalizes spaces, and asserts headers, sections, summary counters, and return codes. The failure scenario sets `java.security.krb5.conf` to an invalid path to force the JVM Kerberos probe to fail.

State and persistence behavior: No persistence. The test temporarily mutates a JVM system property and clears it after each test.

Dependencies and integration points: It covers debug command registration plus environmental Kerberos probes and auth-to-local mapping behavior.

Risks: Results depend on local Kerberos environment; translation may pass or fail, so the test accepts either but requires return code consistency. Diagnose success only requires nonnegative return code.

Test signals: Presence of all diagnostic sections, `FAIL` on invalid krb5 config, and translation summary with pass/fail return-code alignment.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/kerberos/TestOzoneDebugKerberos.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/kerberos/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/kerberos/package-info.java

Purpose: This test package descriptor documents Kerberos debug tests.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It describes the namespace containing `TestOzoneDebugKerberos`.

Risks and test signals: Documentation drift is the only risk; test compilation is the direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/kerberos/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/om/TestContainerToKeyMapping.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/om/TestContainerToKeyMapping.java

Purpose: `TestContainerToKeyMapping` verifies the offline OM container-to-key mapping command across FSO keys, OBS keys, open keys, multipart uploads, absent containers, and unreferenced FSO files.

Important APIs and types: It uses `OmMetadataManagerImpl`, `OzoneDebug`, `CommandLine`, temp OM DB paths, `OmVolumeArgs`, `OmBucketInfo`, `OmDirectoryInfo`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmMultipartKeyInfo`, `StandaloneReplicationConfig`, and protobuf `PartKeyInfo`.

Control flow: Setup creates an `om.db`, redirects command output, populates volume/bucket/directory/file/key/open-key/multipart tables with synthetic metadata and block locations, then closes the store. Each test executes `om container-key-mapping --db <path> --containers ...` with relevant flags and asserts the emitted JSON contains expected paths, container IDs, `openKeys`, `totalKeys`, or `unreferencedKeys`.

State and persistence behavior: Test state is a temporary RocksDB OM metadata store. It creates both FSO and OBS bucket metadata, committed keys, open keys, multipart entries, and an intentionally missing parent directory. Cleanup closes the store if still open.

Dependencies and integration points: This is the strongest local signal for `ContainerToKeyMapping`; it exercises real OM table codecs and command dispatch through `OzoneDebug`.

Risks: Assertions are substring-based rather than full JSON structural checks. It does not test invalid input, duplicate containers, or cleanup of the temporary `omdirtree.db` after command failure.

Test signals: Required signals are full FSO path reconstruction, OBS database-key output, filename-only mode, open-key inclusion, MPU inclusion, zero result for nonexistent container, and unreferenced count for missing FSO parent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/om/TestContainerToKeyMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/ozone/TestPrintableGraph.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/ozone/TestPrintableGraph.java

Purpose: `TestPrintableGraph` verifies PNG generation behavior for `PrintableGraph` across all graph label modes.

Important APIs and types: It uses mocked Guava `MutableGraph<CompactionNode>`, parameterized JUnit tests over `PrintableGraph.GraphType`, temp directories, and Mockito.

Control flow: The empty-graph test constructs a graph with no mocked nodes and expects `generateImage` to throw `IOException` with `Graph is empty.`. The non-empty test stubs four `CompactionNode`s, generates an image for each graph type, and asserts the output path exists.

State and persistence behavior: It writes generated image files under a JUnit temp directory and uses no other persistence.

Dependencies and integration points: It covers the graph helper used by OM compaction DAG rendering.

Risks: The non-empty test stubs nodes but not edges, so it verifies vertex-only rendering but not edge conversion. It does not inspect image content.

Test signals: Empty graph message and file existence for `FILE_NAME`, `KEY_SIZE`, and `CUMULATIVE_SIZE`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/ozone/TestPrintableGraph.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/pom.xml

Purpose: This Maven module defines `ozone-cli-interactive`, the top-level interactive CLI jar for Ozone.

Important APIs and types: It inherits from the root `ozone` parent, packages a jar, sets `classpath.skip=false`, and depends on picocli, `picocli-shell-jline3`, `ozone-cli-admin`, `ozone-cli-debug`, `ozone-cli-shell`, and runtime `slf4j-reload4j`.

Control flow and state: Build-time only. The dependencies assemble the command tree and REPL implementation used by `OzoneInteractiveShell`.

Dependencies and integration points: This module binds admin, debug, shell, tenant, and S3 command implementations into an interactive shell artifact.

Risks: Runtime behavior depends on transitive command registrations from the child CLI modules. Missing runtime logging or jline dependencies would break the shell startup.

Test signals: Build signals include dependency resolution, jar packaging, and execution of `OzoneInteractiveShell` with the expected command set.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveShell.java

Purpose: `OzoneInteractiveShell` starts a JLine/picocli REPL that groups all major Ozone command families under one interactive `ozone` prompt.

Important APIs and types: It uses `PicocliCommandsFactory`, `CommandLine`, `REPL`, `Shell`, `OzoneShell`, `TenantShell`, `S3Shell`, `OzoneAdmin`, `OzoneDebug`, `OzoneInteractiveWelcome`, and a private `TopCommand`.

Control flow: `main` creates a picocli factory and top command, adds subcommands `sh`, `tenant`, `s3`, `admin`, and `debug`, creates a lightweight `Shell` implementation for name/prompt/welcome lines, and constructs a `REPL`. The top command itself is a no-op grouping command.

State and persistence behavior: There is no persistence. Runtime state is the REPL session, command tree, and welcome-line list.

Dependencies and integration points: It is the executable entry point for the `ozone-cli-interactive` module and composes command sets from separate Ozone CLI artifacts.

Risks: The `new REPL(...)` constructor is expected to start or own the interactive loop; if it does not, `main` would exit immediately. Command aliases and option behavior depend on the embedded child command instances. There is no direct handling of startup exceptions.

Test signals: Tests should verify subcommand registration, prompt/name values, welcome lines, and that basic commands can be invoked through the REPL command tree.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/src/main/java/org/apache/hadoop/ozone/shell/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/src/main/java/org/apache/hadoop/ozone/shell/package-info.java

Purpose: This package descriptor documents the top-level interactive CLI package.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It describes the package containing `OzoneInteractiveShell`.

Risks and test signals: Documentation drift is the only risk; compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/src/main/java/org/apache/hadoop/ozone/shell/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/dev-support/findbugsExcludeFile.xml

Purpose: This SpotBugs exclude file is the module-local filter for `ozone-cli-repair`.

Important APIs and types: It is an empty `<FindBugsFilter>` document.

Control flow and state: Build-time only; it does not suppress any findings currently.

Dependencies and integration points: The cli-repair `pom.xml` points SpotBugs at this file.

Risks and test signals: Empty filters are low risk but can become a place for accidental broad suppressions later. Build validation should confirm the XML is well-formed and SpotBugs can load it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/pom.xml

Purpose: This Maven module defines `ozone-cli-repair`, the jar containing advanced offline/repair tools for Ozone.

Important APIs and types: It inherits from the root Ozone parent, packages a jar, sets `classpath.skip=false`, and depends on Guava, commons-io/lang3/codec, picocli, Jakarta annotations, Hadoop common, HDDS CLI/config/container/SCM/RocksDB artifacts, Ozone debug/shell/client/common/interface/manager artifacts, Ratis artifacts, RocksDB JNI, SLF4J, and metainf-services. Test dependencies include HDDS test jars and utilities.

Control flow and state: Build-time configuration includes SpotBugs with the module exclude file, compiler annotation processors for metainf-services and picocli native-image config generation, and an enforcer override banning selected annotation imports.

Dependencies and integration points: The module packages service-loaded repair subcommands such as datanode schema upgrade and transaction info repair. Runtime dependencies include RocksDB and checkpoint differ support needed by offline DB operations.

Risks: This module has a broad dependency surface and touches offline persistent state, so dependency version mismatches can be high impact. Annotation processor configuration must stay aligned with service registration. Banned import overrides need to remain intentional.

Test signals: Build should compile annotation-generated service metadata, run SpotBugs with the exclude file, enforce banned imports, and execute repair CLI tests that exercise RocksDB/container dependencies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/OzoneRepair.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/OzoneRepair.java

Purpose: `OzoneRepair` is the top-level executable for advanced Ozone repair commands.

Important APIs and types: It extends `GenericCli`, implements `ExtensibleParentCommand`, uses `HddsVersionProvider`, and returns `RepairSubcommand.class` from `subcommandType`.

Control flow: `main` instantiates `OzoneRepair` and runs the provided argv. The extensible command framework discovers subcommands implementing `RepairSubcommand`.

State and persistence behavior: This parent command stores no repair state and performs no direct IO.

Dependencies and integration points: It is the command root for service-loaded repair namespaces such as datanode repair and OM/SCM transaction repairs.

Risks and test signals: Direct risks are command discovery and help/version metadata. Tests should verify subcommand loading and top-level invocation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/OzoneRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ReadOnlyCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ReadOnlyCommand.java

Purpose: `ReadOnlyCommand` is a marker interface for repair subcommands that do not modify state.

Important APIs and types: It declares no methods.

Control flow and state: None.

Dependencies and integration points: Repair command infrastructure or documentation can use this marker to distinguish diagnostic/read-only tools from mutating repair tools.

Risks and test signals: The risk is semantic drift if mutating commands implement it or read-only commands omit it. Tests are usually indirect through command classification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ReadOnlyCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/RepairTool.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/RepairTool.java

Purpose: `RepairTool` is the base class for actionable repair commands, providing dry-run formatting, force handling, offline service checks, user confirmation, and stdout/stderr helpers.

Important APIs and types: It extends `AbstractSubcommand` and implements `Callable<Void>`. Subclasses implement `execute` and may override `serviceToBeOffline`. Options are `--force` and `--dry-run`. It defines `Component` enum values `DATANODE`, `OM`, and `SCM`.

Control flow: `call` determines the service requirement, prompts for user confirmation for non-dry-run offline tools, calls `isServiceStateOK`, and runs subclass `execute` only when checks pass. Service state is inferred from environment variables `OZONE_<SERVICE>_RUNNING` and `OZONE_<SERVICE>_PID`; `--force` bypasses a positive running check.

State and persistence behavior: It stores a lazily created `Scanner` for confirmation input and resets it in `finally`. It does not persist data itself but controls whether mutating subclasses are allowed to proceed.

Dependencies and integration points: `TransactionInfoRepair` and `UpgradeContainerSchema` inherit this behavior. The class relies on deployment wrappers setting the Ozone service environment variables accurately.

Risks: Service-running detection is environment-variable based and can be false negative. Confirmation reads from stdin, which can block noninteractive use unless `--dry-run` or null service. Dry-run prefixes all messages, including errors. `--force` can permit unsafe mutation while a service is running.

Test signals: Tests should cover dry-run skip, force bypass, running-service refusal, no-service online tools, confirmation accept/reject, formatted messages, and scanner cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/RepairTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/TransactionInfoRepair.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/TransactionInfoRepair.java

Purpose: `TransactionInfoRepair` updates the highest term/index stored in the transaction info table of an offline OM or SCM RocksDB.

Important APIs and types: It extends `RepairTool`, accepts required `--db`, `--term`, and `--index`, uses `ManagedRocksDB`, `RocksDBUtils`, `TransactionInfo`, `StringCodec`, `OMDBDefinition.TRANSACTION_INFO_TABLE_DEF`, and `SCMDBDefinition.TRANSACTIONINFO`.

Control flow: `execute` opens the DB with latest options, determines the target column family from the parent command name (`om` or `scm`), resolves the column family handle, reads and logs original transaction info, builds a new `TransactionInfo`, and writes it unless dry-run is active. RocksDB resources and column family handles are closed in `finally`.

State and persistence behavior: This is a mutating offline repair unless `--dry-run` is set. It writes the `TRANSACTION_INFO_KEY` value in the selected column family. It requires the relevant OM or SCM service to be offline through `RepairTool`.

Dependencies and integration points: It is intended for repair command parents named `om` or `scm`; `serviceToBeOffline` also uses that parent name to select the service.

Risks: Parent-name coupling can fail if command names change. Input term/index are described as non-zero but not validated. Opening with empty column-family descriptor list relies on RocksDB utility behavior. Incorrect values can make Ratis metadata inconsistent.

Test signals: Tests should cover OM and SCM column family selection, dry-run no-write, actual write and reread, missing column family, invalid parent command, running-service gate, and zero/negative term-index validation if added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/TransactionInfoRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/DatanodeRepair.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/DatanodeRepair.java

Purpose: `DatanodeRepair` registers datanode-specific repair commands.

Important APIs and types: It implements `RepairSubcommand`, uses `@MetaInfServices`, and declares `UpgradeContainerSchema` as a picocli subcommand.

Control flow and state: The class has no fields or direct execution method. Picocli routes to `upgrade-container-schema`.

Dependencies and integration points: It plugs datanode repair tooling into `OzoneRepair` service discovery.

Risks and test signals: Command registration and help output are the main direct behaviors. Upgrade behavior is in `UpgradeContainerSchema`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/DatanodeRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/package-info.java

Purpose: This package descriptor documents datanode repair tools.

Important APIs and types: It contains package-level Javadoc only.

Control flow and state: None.

Dependencies and integration points: It describes the namespace containing `DatanodeRepair` and schema-upgrade repair commands.

Risks and test signals: Documentation drift is the only risk; compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/ContainerUpgradeResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/ContainerUpgradeResult.java

Purpose: `ContainerUpgradeResult` records the outcome of upgrading one container from datanode schema V2 to schema V3.

Important APIs and types: It stores original `ContainerData`, optional new `ContainerData`, row count, monotonic start/end times, status, backup `.container` path, and new `.container` path. Methods include setters, getters, `success`, `getCostMs`, `toString`, and enum `Status`.

Control flow: Construction captures the original container and start time. `success` records total migrated rows, end time, and `SUCCESS`. `toString` emits schema versions and file paths when new data is available.

State and persistence behavior: The object is in-memory only, but its file-path fields refer to persisted backup and rewritten container metadata files.

Dependencies and integration points: `UpgradeContainerSchema.UpgradeTask` creates and fills these results while migrating per-container RocksDB rows to the volume DB.

Risks: Failed results never set `endTimeMs`, so `getCostMs` can be negative. The class assumes original/new data are `KeyValueContainerData` when formatting schema versions.

Test signals: Tests should assert success state, row count, timing, string content with and without new data, backup/new path propagation, and failed-result timing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/ContainerUpgradeResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/UpgradeContainerSchema.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/UpgradeContainerSchema.java

Purpose: `UpgradeContainerSchema` implements the offline datanode repair command `upgrade-container-schema`, migrating schema V2 key-value containers into the schema V3 per-volume database format.

Important APIs and types: It extends `RepairTool`, requires datanode offline, accepts optional `--volume`, and uses `UpgradeUtils`, `HddsVolume`, `DatanodeDetails`, `HDDSLayoutFeature`, `DatanodeStoreCache`, `DatanodeStoreSchemaThreeImpl`, `BlockUtils.getUncachedDatanodeStore`, `ContainerDataYaml`, `KeyValueContainerData`, `DatanodeSchemaThreeDBDefinition`, `FixedLengthStringCodec`, `NativeIO.renameTo`, and `ContainerUpgradeResult`.

Control flow: `execute` loads datanode details and layout features, refuses to proceed unless software and metadata layout support `DATANODE_SCHEMA_V3`, optionally validates a single volume path and version file, discovers all volumes, filters already-upgraded volumes, and calls `run`. `run` starts one `UpgradeTask` future per volume, waits for results, logs success or failure, and records `lastResults`.

State and persistence behavior: Each `UpgradeTask` validates cluster/current directories, creates a volume upgrade lock file, checks for an upgrade-complete marker, backs up the schema V3 volume DB directory, loads the volume DB store, walks container subdirectories, parses `.container` files, and upgrades only schema V2 key-value containers. For each container it opens the old per-container DB read-only, copies configured column family rows into the volume DB with a schema V3 container-key prefix, backs up the old `.container` file, writes a new schema V3 `.container` file, records row count, and finally creates a volume upgrade complete marker if the volume result succeeded. Dry-run still loads DBs and counts rows, and copies the container file to backup instead of renaming/writing.

Dependencies and integration points: This is part of datanode repair command discovery via `DatanodeRepair`. It relies on datanode volume layout conventions, container YAML parsing, V2/V3 datanode store definitions, and `UpgradeUtils` helpers for layout, volumes, marker files, and column family names.

Risks: This is high-impact offline mutation. Partial failure can leave DB backup, lock files, migrated rows, or backed-up container files before marker creation. The source `DatanodeStore` opened for each container is not visibly closed in `upgradeContainer`, so resource lifecycle depends on the store implementation or external cleanup. Dry-run copies backup container files, so it is not completely side-effect free. Volume upgrades run concurrently and may create timestamped backups that collide if repeated within the same second. Complete markers are created even if individual container failures are swallowed before `result.success`.

Test signals: Strong tests should cover layout gating, invalid volume path/version file, already-upgraded skip, lock-file and complete-file behavior, DB backup creation, V2-only filtering, non-key-value skip, container ID mismatch, row key prefixing, dry-run side effects, container YAML backup/rewrite, marker creation, lock deletion, failure propagation, and concurrent multi-volume execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/UpgradeContainerSchema.java -->
