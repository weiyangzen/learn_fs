# subset-b-008054 Research

Grouped research for the Ozone CLI repair and shell files in work item `subset-b-008054`. Each section is delimited for deterministic splitting into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/UpgradeUtils.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/UpgradeUtils.java

Purpose: package-private utility support for datanode schema-v2 to schema-v3 container upgrade repair. It centralizes volume discovery, datanode identity loading, layout-version inspection, marker-file naming, and column-family enumeration used by the actual upgrade tool.

Important APIs and control flow: `COLUMN_FAMILY_NAMES` is derived from `DatanodeSchemaTwoDBDefinition` so migration copies the schema-v2 table set consistently. `getDatanodeDetails` reads the configured datanode ID file and fails early if missing. `getLayoutFeature` opens `DatanodeLayoutStorage`, builds an `HDDSLayoutVersionManager`, and returns software and metadata features as a pair. `getAllVolume` builds a `MutableVolumeSet` and filters to `HddsVolume` instances. `createFile` writes a timestamp to marker files.

State and dependencies: persistent state is filesystem-based: `upgrade.complete`, `upgrade.lock`, and backup suffix conventions in each HDDS volume root. Dependencies are Ozone configuration, datanode layout storage, volume utilities, and schema DB definitions.

Risks and test signals: marker-file creation is simple but not atomic beyond the single file write, so concurrent manual runs rely on higher-level locking. Tests in `TestUpgradeContainerSchema` indirectly exercise ID, volume, layout, and marker behavior during end-to-end upgrade.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/UpgradeUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/VolumeUpgradeResult.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/VolumeUpgradeResult.java

Purpose: mutable result aggregate for one HDDS volume during datanode container schema upgrade. It records volume-level success/failure, elapsed time, the opened schema-three store, and per-container migration results.

Important APIs and control flow: the constructor pins an `HddsVolume`. `setResultList` converts a list of `ContainerUpgradeResult` values into a map keyed by original container ID. `success` and `fail` finalize elapsed time from `Time.monotonicNow`, set status, and preserve exceptions on failure. `toString` serializes volume root, every container result, summed row count, elapsed time, status, and exception details.

State and dependencies: no direct persistence; it mirrors migration state already written by the upgrade task. It references `DatanodeStoreSchemaThreeImpl`, so later verification can inspect migrated block data from the schema-three store.

Risks and test signals: `resultMap` can remain null when a volume fails early, so callers must check status. `TestUpgradeContainerSchema` asserts success, container status, backup/new container file paths, schema version transitions, and uses `getStore` to validate migrated rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/VolumeUpgradeResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/package-info.java

Purpose: package documentation marker for datanode schema-upgrade repair commands. The comment describes the package as containing container-related commands, though the wording says "scm" and should be read as datanode container schema upgrade context.

APIs and integration: no executable API. It establishes package-level Javadoc for `org.apache.hadoop.ozone.repair.datanode.schemaupgrade`, which contains utilities, result types, and the upgrade command wired into the repair CLI through the datanode command tree.

State and dependencies: no runtime state or dependencies beyond Java package metadata.

Risks and test signals: stale package comments can mislead generated docs, but there is no behavioral risk. Behavioral coverage comes from `TestUpgradeContainerSchema`, not this package descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/LDBRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/LDBRepair.java

Purpose: top-level `ozone repair ldb` command container for generic RocksDB/LDB operational repair utilities.

Important APIs and control flow: annotated with picocli `@Command(name = "ldb")`, registers `RocksDBManualCompaction` as its only subcommand, and implements `RepairSubcommand`. `@MetaInfServices(RepairSubcommand.class)` makes it discoverable by the repair CLI service-loader mechanism.

State and dependencies: no direct state or persistence. It depends on picocli and `hdds-cli` service-provider conventions to attach to the `OzoneRepair` command graph.

Risks and test signals: any missing subcommand registration would hide the compaction tool from users. `TestOzoneRepair.subcommandsSupportDryRun` walks command metadata, while `TestLdbRepair` exercises the registered compaction command directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/LDBRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/RocksDBManualCompaction.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/RocksDBManualCompaction.java

Purpose: offline repair command that manually compacts one RocksDB column family for any Ozone-related RocksDB database. It is intentionally generic and warns operators to stop the owning service.

Important APIs and control flow: picocli options require `--db` and `--column-family`/`--cf`. `execute` confirms generic repair execution, then prompts a second "service stopped" warning unless dry-run is enabled. It opens the DB with latest options via `ManagedRocksDB.openWithLatestOptions`, resolves the target column family with `RocksDBUtils.getColumnFamilyHandle`, and runs `compactRange` with forced bottommost-level compaction. Errors are wrapped as `IOException`; RocksDB options and handles are closed in `finally`.

State and dependencies: mutates SST layout and removes tombstones in-place; it does not change logical key/value contents. Dependencies include managed RocksDB wrappers, `RocksDBUtils`, picocli, and `RepairTool` for dry-run/confirmation output.

Risks and test signals: running while OM/SCM/DN owns the DB can corrupt operational assumptions or hurt OM snapshot diff efficiency. `TestLdbRepair` verifies tombstones disappear, SST size shrinks, command exit succeeds, and DB/table options are preserved.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/RocksDBManualCompaction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/package-info.java

Purpose: package Javadoc marker for `org.apache.hadoop.ozone.repair.ldb`. The comment says "OM related repair tools", but the package actually holds generic LDB/RocksDB repair commands.

APIs and integration: no code API. It participates only in generated package documentation for the repair CLI module.

State and dependencies: no state, persistence, or runtime dependencies.

Risks and test signals: the inaccurate wording is documentation drift only. Actual command behavior is covered by `LDBRepair` metadata and `TestLdbRepair`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/CompactOMDB.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/CompactOMDB.java

Purpose: online OM repair/admin command that asks a running OM to compact a named om.db column family asynchronously.

Important APIs and control flow: picocli requires `--column-family` and accepts optional `--service-id`/`--om-service-id` and `--node-id`. `execute` resolves `OMNodeDetails` from configuration, creates an `OMAdminProtocolClientSideImpl` proxy for the selected OM as the current user, calls `compactOMDB(columnFamilyName)`, and prints follow-up log guidance. Dry-run resolves inputs but skips the RPC.

State and dependencies: state changes occur inside the running OM process, not in this CLI process. Dependencies are `OzoneConfiguration`, OM admin protocol PB client, UGI, and `RepairTool`.

Risks and test signals: user-visible success only means request submission, not compaction completion. Incorrect node/service selection can compact an unintended OM. No direct test in this subset; `TestOzoneRepair` ensures leaf repair commands expose dry-run unless marked read-only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/CompactOMDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/FSORepairTool.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/FSORepairTool.java

Purpose: offline OM repair tool for disconnected FILE_SYSTEM_OPTIMIZED bucket trees. It finds reachable objects, pending-deletion objects, and truly orphaned FSO file/directory records, then moves orphaned records into deletion tables when not in dry-run.

Important APIs and control flow: `execute` requires OM offline and delegates to `Impl.run`. Inputs are `--db`, optional `--volume`, and optional `--bucket`. `Impl` opens the OM DB via `OMDBDefinition`, opens a temporary `temp.db` with `reachable` and `pendingToDelete` tables, iterates volumes/buckets, skips non-FSO buckets and buckets with snapshots, DFS-marks reachable directories from bucket roots, marks descendants of `deletedDirectoryTable` entries as pending deletion, scans directory/file tables, and repairs orphaned rows. `markFileForDeletion` deletes from `fileTable` and inserts `RepeatedOmKeyInfo` into `deletedTable`; `markDirectoryForDeletion` deletes from `directoryTable` and inserts a unique entry into `deletedDirectoryTable`.

State and dependencies: mutates OM RocksDB tables in batches; creates and deletes sibling `temp.db`; depends on OM DB codecs, FSO key format, `OMFileRequest`, and object IDs.

Risks and test signals: the tool must run after OM/Ratis state is flushed and skips snapshot buckets to avoid snapshot-chain side effects. Prefix scans and DFS can be expensive. Tests in this subset verify repair prompt behavior, not FSO classification itself.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/FSORepairTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRatisLogRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRatisLogRepair.java

Purpose: offline OM Ratis log surgery command that replaces one failing OM transaction at a given Raft index with an `EchoRPC` no-op request.

Important APIs and control flow: `--index` and `--backup` are required. The mutually exclusive argument group accepts either `--segment-path` or `--ratis-log-dir`; directory mode finds the matching `log_<start>-<end>` or `log_inprogress_<start>` file. `execute` validates the segment path, prevents backup in the segment directory, creates a backup copy, streams the segment with `LogSegment.readSegmentFile`, and writes every entry to a temp output segment. `processLogEntry` leaves other entries unchanged and calls `getOmEchoLogEntry` for the target index, preserving Raft metadata while replacing OM request bytes. The temp segment atomically replaces the original.

State and dependencies: rewrites Ratis segment files and creates backups; uses Apache Ratis log APIs and OM request conversion helpers.

Risks and test signals: this is destructive and must be applied consistently across OMs only for the documented all-OM crash case. Dry-run still reads and validates but skips file mutation. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRatisLogRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRepair.java

Purpose: top-level `ozone repair om` command container for Ozone Manager repair operations.

Important APIs and control flow: picocli registers `FSORepairTool`, `SnapshotRepair`, `TransactionInfoRepair`, `QuotaRepair`, `CompactOMDB`, and `OMRatisLogRepair`. `@MetaInfServices(RepairSubcommand.class)` publishes this command to the repair CLI discovery path.

State and dependencies: no direct persistence. It defines the integration point between the global `OzoneRepair` command and OM-specific repair implementations, including both offline DB mutation tools and online RPC tools.

Risks and test signals: incorrect registration would hide or misplace critical repair tools. `TestOzoneRepair` recursively validates command metadata and dry-run support policy for leaf commands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotChainRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotChainRepair.java

Purpose: offline OM repair command for corrupted snapshot predecessor links in `snapshotInfoTable`.

Important APIs and control flow: command `snapshot chain` takes a bucket URI, snapshot name, `--db`, required `--global-previous` UUID, and required `--path-previous` UUID. It opens RocksDB with latest options, locates the `snapshotInfoTable` column family, builds the `SnapshotInfo` key from bucket URI and snapshot name, loads the target snapshot, scans all snapshot IDs into a set, rejects self-references and nonexistent predecessor IDs, mutates the target `SnapshotInfo`, serializes it, and writes it back unless dry-run is set.

State and dependencies: mutates a single row in OM RocksDB. It depends on `BucketUri`, `SnapshotInfo` codec/table-key rules, managed RocksDB handles, and `StringCodec`.

Risks and test signals: validation checks existence of predecessor IDs but not complete acyclicity or ordering semantics. Running with OM active is unsafe. `TestSnapshotChainRepair` covers success/dry-run, self-reference rejection, nonexistent predecessor rejection, and write/no-write behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotChainRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotRepair.java

Purpose: grouping command for snapshot-related OM repair operations.

Important APIs and control flow: picocli command `snapshot` registers `SnapshotChainRepair` as a subcommand. It does not implement execution logic itself.

State and dependencies: no runtime state. It depends only on picocli and the snapshot repair command class.

Risks and test signals: a metadata-only class, so risk is subcommand registration drift. `TestSnapshotChainRepair` exercises the registered path through `OzoneRepair` using `om snapshot chain`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/package-info.java

Purpose: package Javadoc marker for OM-related repair tools.

APIs and integration: no executable API. It documents the `org.apache.hadoop.ozone.repair.om` package, whose classes are registered below the `om` repair command.

State and dependencies: no state, persistence, or dependencies.

Risks and test signals: documentation-only file. Functional coverage is distributed across `TestOzoneRepair`, `TestSnapshotChainRepair`, and repair-tool-specific tests outside this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaRepair.java

Purpose: `om quota` command group and shared OM-client factory for quota repair status/start commands.

Important APIs and control flow: registers `QuotaStatus` and `QuotaTrigger`. `createOmClient` chooses connection mode from `--service-host`, `--service-id`, or the only configured service ID. It installs the protobuf RPC engine, creates an OM transport through `Hadoop3OmTransportFactory`, and returns an `OzoneManagerProtocolClientSideTranslatorPB`. If `forceHA` is true it verifies the supplied ID is an HA service ID. Helpers expose configured OM service IDs and current user.

State and dependencies: no direct persistence; returned clients invoke live OM RPCs. Dependencies include OM config keys, Hadoop RPC, OM transport factory, UGI, and Ratis `ClientId`.

Risks and test signals: ambiguous or missing service ID in multi-OM configurations fails early. Direct host mode bypasses HA routing and must target the leader for some operations. No direct quota tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaStatus.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaStatus.java

Purpose: read-only command that prints the status of the last OM quota repair run.

Important APIs and control flow: picocli options accept optional `--service-id`/`--om-service-id` and `--service-host`. As a child of `QuotaRepair`, `call` opens an OM protocol client with `forceHA=false`, invokes `getQuotaRepairStatus()`, prints the response to stdout, and closes the client.

State and dependencies: no state mutation. It depends on `QuotaRepair.createOmClient`, `OzoneManagerProtocol`, and `ReadOnlyCommand` marker semantics.

Risks and test signals: because it implements `ReadOnlyCommand`, it is exempt from the repair CLI dry-run requirement. Incorrect host/service selection can read from an unintended OM. `TestOzoneRepair.subcommandsSupportDryRun` specifically permits leaf commands that implement `ReadOnlyCommand`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaTrigger.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaTrigger.java

Purpose: online repair command that asks a running OM to start quota repair for all buckets or a specified bucket list.

Important APIs and control flow: accepts optional service selection arguments and `--buckets` as comma-separated `/<volume>/<bucket>` URIs. `execute` parses the list, opens an OM client via the parent `QuotaRepair`, logs the target scope, and unless dry-run calls `startQuotaRepair(bucketList)` followed by `getQuotaRepairStatus()`.

State and dependencies: state mutation happens in OM via RPC; the CLI does not edit DB files. Depends on `RepairTool`, `StringUtils`, `OzoneManagerProtocol`, and the shared quota client factory.

Risks and test signals: bucket URI strings are split but not deeply validated in this class, so server-side validation is important. Status printed after start is a snapshot, not completion proof. No direct quota trigger tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaTrigger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/package-info.java

Purpose: package Javadoc marker for OM quota repair tools.

APIs and integration: no executable code. It documents the package containing the quota command group and its status/start subcommands.

State and dependencies: no runtime state or dependencies.

Risks and test signals: documentation-only file. Command behavior depends on `QuotaRepair`, `QuotaStatus`, and `QuotaTrigger`; dry-run/read-only metadata is indirectly checked by `TestOzoneRepair`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/package-info.java

Purpose: package-level Javadoc marker for the Ozone Repair tool module.

APIs and integration: no executable API. It anchors documentation for common repair CLI types such as `OzoneRepair`, `RepairTool`, `ReadOnlyCommand`, and component subcommand providers outside this specific file.

State and dependencies: no state or persistence.

Risks and test signals: documentation-only. Functional behavior of the package is covered by command metadata tests such as `TestOzoneRepair`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/SCMRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/SCMRepair.java

Purpose: top-level `ozone repair scm` command container for Storage Container Manager repair utilities.

Important APIs and control flow: picocli registers `CertRepair` and shared `TransactionInfoRepair` under `scm`. `@MetaInfServices(RepairSubcommand.class)` publishes this provider to the global repair CLI.

State and dependencies: no direct state or persistence. It integrates SCM-specific repairs with service-loader command discovery.

Risks and test signals: registration errors would hide certificate recovery or SCM transaction repair. `TestTransactionInfoRepair` exercises the `scm update-transaction` path through the global CLI, and `TestOzoneRepair` validates dry-run metadata policy.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/SCMRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/CertRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/CertRepair.java

Purpose: grouping command for SCM certificate-related repair operations.

Important APIs and control flow: picocli command `cert` registers `RecoverSCMCertificate` as the implementation subcommand. It contains no execution body.

State and dependencies: no direct state. It depends only on picocli metadata and the recover command class.

Risks and test signals: command registration drift is the primary risk. There are no certificate recovery tests in this subset; global dry-run metadata is checked by `TestOzoneRepair`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/CertRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/RecoverSCMCertificate.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/RecoverSCMCertificate.java

Purpose: offline SCM repair command that restores missing local SCM certificate files from certificates persisted in the SCM RocksDB `VALID_SCM_CERTS` table, assuming private keys remain intact.

Important APIs and control flow: `--db` is required and SCM must be offline. `execute` normalizes the DB path, discovers the DB definition, locates the `VALID_SCM_CERTS` column-family definition and handle, opens RocksDB read-only, decodes all persisted certificates, selects the local host's sub-CA cert and the root-CA cert by subject-name prefixes, detects whether this host is root CA, and writes certificate PEM files using `CertificateCodec`. Helpers decode RocksDB rows, build cert paths with root included, and write root/subordinate/active certificate filenames.

State and dependencies: reads SCM DB without mutation, but writes certificate files under the configured SCM certificate locations. Depends on `SecurityConfig`, `SCMCertificateClient`, certificate codecs, DB definition discovery, and local hostname.

Risks and test signals: host-name subject matching can select nothing or the wrong cert if naming assumptions differ; caught RocksDB/certificate exceptions currently only log a generic error. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/RecoverSCMCertificate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/package-info.java

Purpose: package Javadoc marker for SCM certificate repair tools.

APIs and integration: no executable API. It documents the package that contains the SCM certificate command group and recovery tool.

State and dependencies: no runtime state.

Risks and test signals: documentation-only. Behavioral risk sits in `RecoverSCMCertificate`; no direct tests are included in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/package-info.java

Purpose: package Javadoc marker for SCM repair tools.

APIs and integration: no executable API. It documents the `org.apache.hadoop.ozone.repair.scm` command package registered below the global repair CLI.

State and dependencies: no runtime state or persistence.

Risks and test signals: documentation-only. SCM transaction repair command behavior is indirectly covered by `TestTransactionInfoRepair`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestOzoneRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestOzoneRepair.java

Purpose: command-level tests for the global Ozone repair CLI metadata and operator confirmation behavior.

Important APIs and control flow: `subcommandsSupportDryRun` recursively walks `new OzoneRepair().getCmd()` and asserts every leaf command contains `--dry-run` unless its user object implements `ReadOnlyCommand`. Other tests capture stdout/stderr, set `user.name` to `ozone`, feed stdin, and verify that risky executable commands prompt with the current user, abort on decline, proceed on "y", and skip prompts for parent/help/incomplete command invocations.

State and dependencies: mutates JVM global streams, stdin, and `user.name` during tests, restoring them in `@AfterEach`. Depends on picocli command metadata and the repair CLI prompt policy.

Risks and test signals: strong guard against adding destructive repair commands without dry-run support. It does not validate the underlying repair behavior beyond prompt flow.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestOzoneRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestTransactionInfoRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestTransactionInfoRepair.java

Purpose: parameterized tests for shared OM/SCM transaction-info repair behavior through the `OzoneRepair` command tree.

Important APIs and control flow: for both `om` and `scm`, static mocks replace `ManagedRocksDB.openWithLatestOptions`, `RocksDBUtils.getColumnFamilyHandle`, and `RocksDBUtils.getValue`. The test executes `<component> update-transaction --db testDBPath --term 1 --index 1` after confirming stdin. It verifies successful output, missing column-family errors, and RocksDB put failure handling.

State and dependencies: no real DB is written; mocked `ManagedRocksDB` and `RocksDB` simulate persistence. It depends on OM and SCM DB definitions for the expected transaction-info table names.

Risks and test signals: covers CLI wiring and error messages but not real RocksDB serialization side effects. It is a useful regression test for component-specific table selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestTransactionInfoRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/TestUpgradeContainerSchema.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/TestUpgradeContainerSchema.java

Purpose: integration-heavy tests for datanode container schema-v2 to schema-v3 repair.

Important APIs and control flow: setup creates temporary datanode volume and metadata directories, writes datanode layout storage and ID files, creates v2 containers with block/chunk data, shuts down volumes, and executes `ozone repair datanode upgrade-container-schema` with injected configuration. `failsBeforeOzoneUpgrade` verifies the command rejects runs before the required layout feature. `testUpgrade` runs both dry-run and real modes, checks per-volume/per-container success, verifies backup/new container data files and schema versions, and for real mode reads the schema-three block table to compare migrated block data.

State and dependencies: creates real container files and RocksDB data under JUnit temp dirs. Uses volume sets, block/chunk managers, schema-three store, and codec leak detection.

Risks and test signals: strong coverage for happy path, dry-run behavior, layout gate, backup files, and data preservation. Failure modes such as partial volume upgrade or lock contention are less visible here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/TestUpgradeContainerSchema.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/ldb/TestLdbRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/ldb/TestLdbRepair.java

Purpose: functional test for manual RocksDB column-family compaction.

Important APIs and control flow: setup creates a real temp `RDBStore` with a test column family and enables codec leak detection. The test inserts many keys, flushes, records SST size, deletes keys to create tombstones, flushes, closes the store, snapshots representative DB/table options, executes `RocksDBManualCompaction` with confirmation input, and then verifies SST size decreased, live SST metadata reports zero deletions, and RocksDB options are unchanged.

State and dependencies: mutates a real temp RocksDB directory. Uses `DBStoreBuilder`, `RocksDBUtils`, `RdbUtil`, managed RocksDB wrappers, and option inspection wrappers.

Risks and test signals: provides high-value evidence that compaction has the intended storage effect without changing RocksDB options. It does not test missing column-family or declined-confirmation paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/ldb/TestLdbRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/om/TestSnapshotChainRepair.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/om/TestSnapshotChainRepair.java

Purpose: unit tests for `om snapshot chain` repair validation and persistence behavior.

Important APIs and control flow: tests mock `ManagedRocksDB`, `RocksDBUtils`, and `OptionsUtil` to avoid a real DB. `setupMockDB` supplies a target `SnapshotInfo`, optional predecessor snapshots, a mocked iterator over encoded snapshot rows, and the target column-family handle. The success test runs both dry-run and real modes and verifies output plus whether `RocksDB.put` is invoked. Negative tests cover global previous equal to target ID, path previous equal to target ID, and nonexistent predecessor IDs.

State and dependencies: no real DB writes; assertions verify serialized key/value bytes passed to mocked RocksDB. Depends on `SnapshotInfo` codec and `StringCodec`.

Risks and test signals: confirms major guardrails but not global/path chain acyclicity, ordering, or real RocksDB open behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/om/TestSnapshotChainRepair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/dev-support/findbugsExcludeFile.xml -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclude-filter file for the `ozone-cli-shell` module.

Important structure and control flow: the XML defines an empty `<FindBugsFilter>`, meaning the module currently has no local suppressions. The `pom.xml` wires this file into the SpotBugs Maven plugin.

State and dependencies: build-time configuration only; no runtime state. Depends on the SpotBugs Maven plugin honoring `excludeFilterFile`.

Risks and test signals: an empty filter is a positive signal that warnings are not being locally suppressed. If future exclusions are added, they should be reviewed because they can hide shell command bugs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/pom.xml -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/pom.xml

Purpose: Maven module descriptor for `ozone-cli-shell`, the native Ozone shell command jar.

Important APIs and control flow: inherits from `hdds-hadoop-dependency-client`, sets artifact/version/packaging, and enables classpath generation. Dependencies include Jackson, Guava, picocli and picocli-shell-jline3, Hadoop common/HDFS client, Ozone client/common/interface modules, Ratis, JLine, SLF4J, metainf-services, runtime Ozone filesystem, and test hdds-config. Build plugins wire SpotBugs to the empty exclude file, configure annotation processors for metainf-services and picocli native-image config generation, and override enforcer import restrictions for selected annotations.

State and dependencies: build-time only. It controls generated service metadata, native-image metadata, runtime classpath, and static analysis behavior.

Risks and test signals: dependency scope mistakes can break CLI packaging or interactive shell runtime. Annotation-processor configuration is important because shell command metadata is consumed by tooling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ClearSpaceQuotaOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ClearSpaceQuotaOptions.java

Purpose: reusable picocli mixin for bucket/volume quota-clear commands.

Important APIs and control flow: defines boolean options `--space-quota` and `--namespace-quota`, with getters `getClrSpaceQuota` and `getClrNamespaceQuota`. Consumers decide whether at least one flag is required.

State and dependencies: no persistence; picocli populates booleans from CLI parsing. Depends only on picocli.

Risks and test signals: this class does not enforce "at least one" itself; callers such as `ClearQuotaHandler` must perform that validation. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ClearSpaceQuotaOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Handler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Handler.java

Purpose: base class for Ozone shell commands that open an `OzoneClient` and operate on an `OzoneAddress`.

Important APIs and control flow: implements `Callable<Void>`. `call` loads `OzoneConfiguration`, checks `isApplicable`, obtains an address from `getAddress`, creates a client through `address.createClient(conf)`, invokes subclass `execute`, and closes the client. Utility methods expose security gating, JSON object printing, JSON-array printing with a limit, message output, and the loaded config.

State and dependencies: holds per-invocation `conf`; no persistence. Depends on `AbstractSubcommand`, Ozone client factory via `OzoneAddress`, Jackson JSON helpers, and security utility.

Risks and test signals: subclasses rely on `getAddress` validation before client creation; command-specific failures bubble through `Shell.printError`. No direct test here, but nearly every shell handler uses this lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Handler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListLimitOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListLimitOptions.java

Purpose: reusable mutually exclusive list-length options for shell list commands.

Important APIs and control flow: picocli `@ArgGroup` contains `--length`/`-l` with default 100 and `--all`/`-a`. `getLimit` returns `Integer.MAX_VALUE` for all mode and rejects non-positive lengths. `isAll` exposes the all flag.

State and dependencies: parse-time state only. Depends on picocli argument-group semantics to keep the options exclusive.

Risks and test signals: returning `Integer.MAX_VALUE` pushes memory/latency risk to handlers that materialize results. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListLimitOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListPaginationOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListPaginationOptions.java

Purpose: reusable list pagination mixin combining list limit and start-after cursor.

Important APIs and control flow: mixes in `ListLimitOptions`, adds `--start`/`-s`, and exposes `getLimit`, `isAll`, and `getStartItem`. The start item is documented as excluded from results.

State and dependencies: parse-time state only; no persistence. Depends on `ListLimitOptions` and picocli mixin injection.

Risks and test signals: handlers must pass `startItem` to the correct client API and avoid over-materializing results. `ListBucketHandler` is one consumer in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListPaginationOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/MandatoryReplicationOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/MandatoryReplicationOptions.java

Purpose: replication-option specialization requiring both replication type and replication definition.

Important APIs and control flow: overrides `setReplication` and `setType` from `ReplicationOptions` only to attach required picocli options. Parsing still delegates validation and conversion to the base class.

State and dependencies: stores parsed values in inherited fields. Depends on `ReplicationOptions` and picocli option injection.

Risks and test signals: useful for commands where falling back to config would be ambiguous. Invalid type handling is inherited. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/MandatoryReplicationOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneAddress.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneAddress.java

Purpose: central URI parser, validator, object-address model, and client factory for Ozone shell commands.

Important APIs and control flow: constructors parse full or short Ozone URIs into volume, bucket, snapshot indicator, key, scheme, host, and port. `createClient` supports only `o3://`, rejects REST, resolves HA service IDs vs host:port vs config defaults, and handles multi-service ambiguity. `createClientForS3Commands` has separate service-ID logic for S3 commands. `ensureBucketAddress`, `ensureKeyAddress`, `ensurePrefixAddress`, `ensureSnapshotAddress`, `ensureVolumeAddress`, `ensureRootAddress`, and `ensureVolumeOrBucketAddress` validate address shape for command-specific converters. `toOzoneObj` maps the address to ACL resource types and store types.

State and dependencies: immutable-ish parsed address state with one mutable `isPrefix` marker. Depends on Ozone config keys, `OzoneClientFactory`, `OmUtils`, HTTP URI builder, and ACL object builders.

Risks and test signals: URI edge cases are high impact because all shell handlers rely on this class. Multi-HA default behavior and snapshot indicator parsing need broad tests outside this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneAddress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveWelcome.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveWelcome.java

Purpose: builds startup banner lines for the Ozone interactive shell.

Important APIs and control flow: `lines` loads `OzoneConfiguration`, reads Ozone version/release, formats configured OM and SCM endpoints, and appends help/exit/completion hints. `formatOmEndpoints` uses HA service IDs if present, otherwise the direct OM address; failures produce a configuration hint. `formatScmEndpoints` formats SCM client addresses similarly.

State and dependencies: no persistence; reads current process configuration. Depends on `OzoneVersionInfo`, `HddsUtils`, `OmUtils`, and OM/SCM config keys.

Risks and test signals: banner endpoint output is diagnostic only, but misleading configuration handling can confuse interactive users. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveWelcome.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneShell.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneShell.java

Purpose: main native Ozone shell command entry point, `ozone sh`/`sh`.

Important APIs and control flow: picocli `@Command` registers bucket, key, prefix, snapshot, tenant, token, and volume command groups, plus standard help and version provider. `main` instantiates `OzoneShell` and delegates to the inherited `run`.

State and dependencies: no direct persistence. Depends on the `Shell` base class for tracing, interactive mode, batch mode, and exception formatting.

Risks and test signals: subcommand list determines the public shell surface; missing entries remove command families. Tests for specific subcommands live elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/PrefixFilterOption.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/PrefixFilterOption.java

Purpose: reusable `--prefix`/`-p` option mixin for list commands.

Important APIs and control flow: stores a parsed prefix string and exposes it through `getPrefix`. Consumers pass the value to client list APIs.

State and dependencies: parse-time state only. Depends on picocli.

Risks and test signals: this class performs no normalization, escaping, or empty-string handling; semantics are defined by the consuming list API. `ListBucketHandler` consumes it in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/PrefixFilterOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/REPL.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/REPL.java

Purpose: JLine/picocli read-eval-print loop used by `Shell` interactive and batch modes.

Important APIs and control flow: constructor builds a dumb terminal, registers picocli commands and `help` with `SystemRegistry`, configures a `LineReader` with completion and auto-listing, optionally preloads batch commands, prints welcome lines for interactive mode, then loops reading and executing commands until EOF or batch exhaustion. User interrupts are ignored; other exceptions are traced through the registry. It prints a blank line before the next prompt.

State and dependencies: terminal/session state only. Depends on JLine terminal/reader/system registry and picocli shell integration.

Risks and test signals: batch mode relies on outer `Shell` exception handling for exit behavior. Dumb terminal mode favors broad compatibility. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/REPL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ReplicationOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ReplicationOptions.java

Purpose: shared parser and resolver for Ozone replication configuration options.

Important APIs and control flow: subclasses attach picocli options to protected setters. `fromParams` returns empty if neither type nor replication was supplied; for RATIS with no replication value it falls back to configured/default replication; otherwise it calls `ReplicationConfig.parseWithoutFallback`. `fromConfig` reads default type and replication from configuration and validates through `OzoneClientUtils`. `fromParamsOrConfig` chooses explicit parameters first. `setType` rejects unsupported `CHAINED` and `STAND_ALONE` and produces a user-facing error listing RATIS and EC.

State and dependencies: stores parsed type and replication strings in memory. Depends on `ReplicationConfig`, `ReplicationType`, Ozone config keys, and client validation helpers.

Risks and test signals: EC syntax and config fallback are sensitive; invalid values should fail before RPC. Consumers include bucket create and set replication config handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ReplicationOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/SetSpaceQuotaOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/SetSpaceQuotaOptions.java

Purpose: reusable picocli mixin for space and namespace quota-setting commands.

Important APIs and control flow: defines `--space-quota` with backward-compatible alias `--quota`, and `--namespace-quota`. Getters return raw strings so consumers can parse them with `OzoneQuota`.

State and dependencies: parse-time state only. Depends on picocli.

Risks and test signals: validation is intentionally deferred to callers, so command handlers must enforce at least one option and parse units/counts. `CreateBucketHandler` and `SetQuotaHandler` consume this mixin.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/SetSpaceQuotaOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Shell.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Shell.java

Purpose: abstract base for Ozone shell frontends, adding interactive/batch execution, tracing, deprecated option warnings, and user-friendly OM exception formatting to `GenericCli`.

Important APIs and control flow: constructor installs a custom execution strategy. `execute` warns on deprecated options, records command name, and if `--interactive` or `--execute` is present starts `REPL`; otherwise it initializes tracing and runs the parsed command under a tracing span. Batch mode wraps execution errors to exit the JVM with the CLI error code. `printError` unwraps `OMException` and prints concise result/message in non-verbose mode.

State and dependencies: holds command name and picocli spec for current execution. Depends on picocli, JLine factory, tracing utilities, and OM exception classes.

Risks and test signals: `System.exit` in batch errors is intentional but test-sensitive. Error formatting can hide stack traces unless verbose is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Shell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ShellReplicationOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ShellReplicationOptions.java

Purpose: optional replication options for Ozone shell commands.

Important APIs and control flow: attaches non-required picocli options `--type`/`--replication-type`/`-t` and `--replication`/`-r` to the inherited setters in `ReplicationOptions`. Downstream commands decide whether empty parameters are allowed.

State and dependencies: inherited parse-time state only. Depends on `ReplicationOptions` and picocli.

Risks and test signals: consumers must call the appropriate resolver (`fromParams`, `fromParamsOrConfig`) and enforce requiredness when needed. `SetReplicationConfigHandler` enforces explicit parameters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ShellReplicationOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/StoreTypeOption.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/StoreTypeOption.java

Purpose: reusable ACL store-type option and converter.

Important APIs and control flow: option `--store`/`-s` defaults to `OZONE` and is converted by this class to `OzoneObj.StoreType`. `convert` returns `OZONE` for null and otherwise uses enum `valueOf`.

State and dependencies: parse-time state only. Depends on picocli and `OzoneObj.StoreType`.

Risks and test signals: enum conversion is case-sensitive, so invalid/lowercase values fail through picocli. Consumed by `AclHandler` when building `OzoneObj`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/StoreTypeOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclHandler.java

Purpose: abstract base class for shell ACL commands across volumes, buckets, keys, and prefixes.

Important APIs and control flow: defines shared command names/descriptions for add/get/remove/set ACL commands. Mixes in `StoreTypeOption`, converts the current `OzoneAddress` to an `OzoneObj`, and delegates to subclass `execute(OzoneClient, OzoneObj)`.

State and dependencies: no persistence; carries parsed store type. Depends on `Handler`, `OzoneAddress.toOzoneObj`, and Ozone ACL object model.

Risks and test signals: address validation is supplied by concrete URI mixins; wrong resource type/store type would direct ACL operations to the wrong object. Bucket ACL handlers in this subset extend it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclOption.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclOption.java

Purpose: reusable ACL list option and operation helper for add/remove/set ACL commands.

Important APIs and control flow: an exclusive arg group accepts modern `--acls`/`--acl`/`-a` or hidden deprecated `-al`, split by comma, with conversion through `OzoneAcl.parseAcl`. `addTo`, `removeFrom`, and `setOn` call the corresponding `ObjectStore` ACL method and print per-ACL result messages or a set success line.

State and dependencies: parse-time ACL array state only; actual ACL persistence is handled by OM through `ObjectStore`. Depends on Guava immutable lists, `OzoneAcl`, and `ObjectStore`.

Risks and test signals: repeated add/remove operations are not transactional across multiple ACLs, so partial success is possible. Deprecated option remains accepted for compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/GetAclHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/GetAclHandler.java

Purpose: abstract implementation for ACL read commands with JSON or compact string output.

Important APIs and control flow: option `--json` is negatable and defaults true. `execute` fetches ACLs through `client.getObjectStore().getAcl(obj)`, prints pretty JSON by default, or joins ACL strings with commas. `formatAcl` strips trailing `[ACCESS]` to make non-JSON output compatible with set/add input syntax while preserving non-default scopes.

State and dependencies: read-only client operation; no persistence in this class. Depends on `AclHandler`, `OzoneAcl`, and JSON helper inherited from `Handler`.

Risks and test signals: string formatting uses regex replacement on `OzoneAcl.toString`, so changes to ACL string format could affect compatibility. Bucket-specific `GetAclBucketHandler` extends it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/GetAclHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/package-info.java

Purpose: package Javadoc marker for shell ACL helper classes.

APIs and integration: no executable code. It documents the reusable ACL base classes and options used by object-specific command packages.

State and dependencies: no runtime state.

Risks and test signals: documentation-only. Behavior is in `AclHandler`, `AclOption`, and `GetAclHandler`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/AddAclBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/AddAclBucketHandler.java

Purpose: bucket-specific `addacl` shell command.

Important APIs and control flow: mixes in `BucketUri` for validated `volume/bucket` address and `AclOption` for one or more ACLs. `getAddress` returns the bucket address, and `execute` delegates to `AclOption.addTo` with the client object store and output writer.

State and dependencies: ACL changes persist through OM via `ObjectStore.addAcl`; this handler holds only parsed CLI state. Depends on `AclHandler`, `BucketUri`, and `AclOption`.

Risks and test signals: multiple ACLs can partially succeed because each is added independently. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/AddAclBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketCommands.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketCommands.java

Purpose: command group for bucket-specific Ozone shell operations.

Important APIs and control flow: picocli command `bucket` registers info, list, create, set quota, link, delete, ACL operations, clear quota, set replication config, update, and hidden set-encryption-key handlers. It enables standard help and version provider.

State and dependencies: no direct state; public command surface metadata only. Depends on all registered handler classes and picocli.

Risks and test signals: this subcommand list controls user-facing availability. `UpdateBucketHandler` is referenced but outside this work item, so integration depends on that class compiling in the module.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketHandler.java

Purpose: base class for bucket commands that take exactly one bucket URI.

Important APIs and control flow: mixes in `BucketUri`; overrides `getAddress` to return the validated bucket address. Subclasses inherit `Handler.call` for client lifecycle and implement `execute(OzoneClient, OzoneAddress)`.

State and dependencies: parse-time address state only. Depends on `Handler`, `BucketUri`, and `OzoneAddress`.

Risks and test signals: all subclasses rely on `BucketUri.convert` to reject malformed bucket paths before execution. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketUri.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketUri.java

Purpose: picocli parameter/converter for bucket-address arguments.

Important APIs and control flow: defines positional parameter index 0 with Ozone shell URI help text and conversion through `BucketUri`. `convert` constructs an `OzoneAddress`, calls `ensureBucketAddress`, and returns the validated object.

State and dependencies: parse-time state only. Depends on `OzoneAddress` validation and shell URI documentation.

Risks and test signals: it rejects keys under buckets and missing volume/bucket names, protecting bucket handlers from accidental broader operations. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketUri.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ClearQuotaHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ClearQuotaHandler.java

Purpose: bucket `clrquota` command that clears space and/or namespace quota.

Important APIs and control flow: mixes in `ClearSpaceQuotaOptions`, resolves the target bucket through object store volume/bucket lookup, calls `clearSpaceQuota` and/or `clearNamespaceQuota` based on flags, and throws `IOException` if neither flag was supplied.

State and dependencies: persists quota changes through OM RPCs on `OzoneBucket`. Depends on `BucketHandler`, `ClearSpaceQuotaOptions`, and Ozone client model.

Risks and test signals: not atomic across both quota types if one call succeeds and the other fails. Validation is local for missing flags. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ClearQuotaHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/CreateBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/CreateBucketHandler.java

Purpose: bucket `create` command supporting owner, encryption, GDPR metadata, layout, default replication, and quota options.

Important APIs and control flow: builds `BucketArgs` with default storage type/versioning and owner defaulting to current user. Optional flags set bucket layout (`fso`, `obs`, or enum), GDPR metadata, BEK, default replication config from explicit replication params, and parsed space/namespace quota. It resolves the volume and calls `createBucket`, printing the created bucket in verbose mode.

State and dependencies: persists new bucket metadata through OM RPCs. Depends on `BucketArgs`, `OzoneQuota`, replication config wrappers, `UserGroupInformation`, and `BucketLayout`.

Risks and test signals: empty encryption key is rejected locally; layout aliases must stay aligned with server-supported layouts. Quota and replication parsing errors occur before RPC. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/CreateBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/DeleteBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/DeleteBucketHandler.java

Purpose: bucket `delete` command, with optional recursive deletion for non-empty buckets.

Important APIs and control flow: resolves target volume/bucket and OM service ID. Non-recursive mode calls `vol.deleteBucket`. Recursive mode requires `-y/--yes` or an interactive `yes` confirmation, then branches by bucket layout. OBS buckets are listed and deleted in batches of 1000 keys before deleting the bucket. FSO/legacy buckets are deleted through the OFS `FileSystem.delete(path, true)` path using an `ofs://<service-id>/volume/bucket` URI.

State and dependencies: deletes keys and bucket metadata through OM/OFS clients; this is irreversible and bypasses trash for recursive deletes per prompt. Depends on Ozone client, Hadoop FS, OFS constants, and bucket layout.

Risks and test signals: broad destructive behavior; confirmation text warns no recovery. Error handling prints messages but does not rethrow in recursive helpers. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/DeleteBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/GetAclBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/GetAclBucketHandler.java

Purpose: bucket-specific `getacl` command with optional link-source ACL resolution.

Important APIs and control flow: mixes in `BucketUri`, adds `--source` to fetch source bucket ACLs for link buckets, and otherwise delegates to `GetAclHandler`. `getSourceObj` recursively follows link buckets by reading bucket metadata and rebuilding `OzoneObj` for the source until a non-link bucket is reached.

State and dependencies: read-only ACL and bucket metadata access. Depends on `GetAclHandler`, `BucketUri`, `OzoneObjInfo`, and Ozone client bucket link fields.

Risks and test signals: recursive link resolution lacks explicit cycle detection; server-side link constraints likely prevent cycles, but this handler assumes that. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/GetAclBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/InfoBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/InfoBucketHandler.java

Purpose: bucket `info` command returning JSON bucket metadata.

Important APIs and control flow: resolves target bucket through volume/bucket lookup. If the bucket has source volume and source bucket, it wraps the object in `LinkBucket` to expose link-focused fields; otherwise it serializes the `OzoneBucket` directly. `LinkBucket` copies volume/name/source/creation/modification/owner/link fields for JSON output.

State and dependencies: read-only metadata access. Depends on `BucketHandler`, `OzoneBucket`, and JSON printing inherited from `Handler`.

Risks and test signals: wrapper field set may omit newer bucket properties for link buckets. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/InfoBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/LinkBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/LinkBucketHandler.java

Purpose: bucket `link` command that creates a bucket link pointing to another bucket.

Important APIs and control flow: takes two positional `BucketUri` parameters: source and target. `getAddress` returns source so client resolution follows the source URI. `execute` builds `BucketArgs` with source volume and bucket, resolves the target volume, creates the target bucket as a link, and prints it in verbose mode.

State and dependencies: persists link bucket metadata through OM RPC. Depends on `BucketArgs`, `StorageType.DEFAULT`, `OzoneVolume`, and bucket URI validation.

Risks and test signals: client connection is based on source address, so cross-cluster source/target semantics are not supported here. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/LinkBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ListBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ListBucketHandler.java

Purpose: bucket `list`/`ls` command for listing buckets in a volume.

Important APIs and control flow: extends `VolumeHandler` and mixes in pagination and prefix filter options plus `--has-snapshot`. It resolves the volume, calls `vol.listBuckets(prefix, start, filterByHasSnapshot)`, copies up to the requested limit into a list, wrapping link buckets in `InfoBucketHandler.LinkBucket`, then prints JSON array output. Verbose mode prints a count to stderr.

State and dependencies: read-only metadata listing. Depends on Ozone client volume APIs, `ListPaginationOptions`, `PrefixFilterOption`, and link-bucket wrapper.

Risks and test signals: results are materialized into memory up to limit; `--all` can be large. Pagination semantics depend on server-side start-item handling. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ListBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/RemoveAclBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/RemoveAclBucketHandler.java

Purpose: bucket-specific `removeacl` shell command.

Important APIs and control flow: mixes in validated `BucketUri` and `AclOption`. `execute` delegates to `AclOption.removeFrom`, which iterates parsed ACLs and calls `ObjectStore.removeAcl`.

State and dependencies: persists ACL removals through OM RPCs. Depends on `AclHandler`, `AclOption`, and bucket address conversion.

Risks and test signals: multi-ACL removal is not transactional and prints per-ACL existence/success messages. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/RemoveAclBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetAclBucketHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetAclBucketHandler.java

Purpose: bucket-specific `setacl` shell command that replaces existing ACLs.

Important APIs and control flow: mixes in `BucketUri` and `AclOption`; `execute` calls `AclOption.setOn`, which invokes `ObjectStore.setAcl` with the parsed ACL list and prints success.

State and dependencies: persists replacement ACL set through OM. Depends on `AclHandler`, `AclOption`, and Ozone ACL object conversion.

Risks and test signals: replacement semantics are broader than add/remove and can remove existing ACLs not included by the user. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetAclBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetEncryptionKey.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetEncryptionKey.java

Purpose: hidden deprecated bucket command to reset a bucket encryption key for buckets affected by historical HDDS-7449/HDDS-7526 issues.

Important APIs and control flow: command `set-encryption-key` is hidden and deprecated. It accepts `--key`/`-k`, resolves the target bucket through the object store, and calls `bucket.setEncryptionKey(bekName)`.

State and dependencies: persists bucket encryption metadata through OM RPC. Depends on `BucketHandler` and `OzoneBucket`.

Risks and test signals: the Javadoc explicitly warns this does not alter existing keys and later writes only are affected. The command is hidden because resetting encryption after creation is not normal user flow. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetEncryptionKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetQuotaHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetQuotaHandler.java

Purpose: bucket `setquota` command for changing bucket space and/or namespace quotas.

Important APIs and control flow: mixes in `SetSpaceQuotaOptions`, loads current bucket quotas, overrides provided values after parsing with `OzoneQuota`, requires at least one quota option, warns for buckets with old quota defaults suggesting inaccurate usage metrics, and calls `bucket.setQuota`.

State and dependencies: persists quota metadata through OM RPC. Depends on `OzoneQuota`, `OLD_QUOTA_DEFAULT`, and Ozone bucket APIs.

Risks and test signals: updates both quota values in one `OzoneQuota` object using existing values for omitted dimensions. Warning does not block old buckets. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetQuotaHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetReplicationConfigHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetReplicationConfigHandler.java

Purpose: bucket command for setting the default replication config on an existing bucket.

Important APIs and control flow: mixes in optional shell replication options, but `execute` requires explicit replication parameters by calling `replication.fromParams(getConf()).orElseThrow`. It resolves the target bucket and calls `bucket.setReplicationConfig(replicationConfig)`.

State and dependencies: persists bucket default replication metadata through OM. Depends on `ShellReplicationOptions`, `ReplicationConfig`, `OzoneIllegalArgumentException`, and Ozone bucket APIs.

Risks and test signals: rejects config fallback to avoid accidental changes from defaults; users must supply type/config explicitly. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetReplicationConfigHandler.java -->
