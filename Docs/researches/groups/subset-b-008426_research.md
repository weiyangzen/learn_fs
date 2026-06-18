# subset-b-008426 Research

This grouped report covers the requested FoundationDB backup, restore, BulkDump, and audit CLI files. Each file section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/backup.cpp -->
# sources/storage-engines/foundationdb/fdbbackup/backup.cpp

## Purpose

`backup.cpp` is the multi-binary command implementation behind `backup_agent`, `fdbbackup`, `fdbrestore`, `dr_agent`, and `fdbdr`. It owns top-level CLI option tables, help output, executable-name dispatch, argument normalization, network/client setup, backup-agent status publication, and command-to-actor routing. It does not implement the core backup algorithms itself; instead it validates and translates CLI state into calls on `FileBackupAgent`, `DatabaseBackupAgent`, `IBackupContainer`, `BackupConfig`, and bulk backup/restore metadata APIs.

## Important APIs, Types, and Functions

Important local enums are `ProgramExe`, `BackupType`, `DBType`, and `RestoreType`, which classify the executable and subcommand. `getSnapshotMode`, `getRestoreMode`, and `getMutationLogType` map user strings to `SnapshotMode`, `RestoreMode`, and `MutationLogType`. The large `CSimpleOpt::SOption` arrays define supported flags for each action, including snapshot mode (`rangefile`, `bulkdump`, `both`), restore mode (`rangefile`, `bulkload`), blob credentials, encryption key and block size, tag names, key ranges, and DR source/destination clusters.

The main operational wrappers are `runAgent`, `runDBAgent`, `submitBackup`, `submitDBBackup`, `switchDBBackup`, `statusBackup`, `statusDBBackup`, `abortBackup`, `abortDBBackup`, `waitBackup`, `discontinueBackup`, `changeBackupResumed`, `changeDBBackupResumed`, `runRestore`, `dumpBackupData`, `expireBackupData`, `deleteBackupContainer`, `describeBackup`, `queryBackup`, `listBackup`, `listBackupTags`, and `modifyBackup`. `openBackupContainer` centralizes backup URL validation and container construction. `parseLine`, `addKeyRange`, and `decode_hex_string` integration parse user key ranges and restore prefixes.

`getLayerStatus`, `cleanupStatus`, `statusUpdateActor`, and `updateAgentPollRate` are the embedded layer-status subsystem for backup and DR agents. They build expiring JSON status documents and adjust per-agent polling based on aggregate process count.

## Control Flow

Startup calls `platformInit`, registers crash handling, normalizes stdout/stderr buffering, derives `ProgramExe` from `argv[0]`, then calls `reorderArguments`. `reorderArguments` moves non-option positional arguments before options so commands can be supplied before or after flags while still feeding `CSimpleOpt` a predictable command-first argv. `processOption` validates options against all option tables, including prefix options such as `--knob-`, accepts `--opt=value`, and treats dash/underscore spellings as equivalent.

After option parsing, `main` accumulates CLI state in local variables, configures trace logging, TLS, blob credentials, memory limits, client knobs, default backup ranges, and optional user/system restore ranges. It then initializes the network and selects one actor future by executable and subcommand. Most `fdbbackup` actions require a destination cluster via `initCluster`, while container-only actions such as list/delete/describe/dump/expire may only open trace files and containers. `fdbrestore` requires an explicit destination cluster file unless running dry-run validation. DR commands initialize both source and destination clusters, with abort optionally allowing destination-only behavior.

The selected actor is wrapped in `stopAfter`, `runNetwork` drives it, and exit status is derived from future completion. Errors are reported through `TraceEvent`, stderr messages, and FoundationDB exit codes.

## State and Persistence Behavior

The command mutates several persistent stores. Backup and restore lifecycle operations write FoundationDB system keyspace metadata through `FileBackupAgent` and `DatabaseBackupAgent`, including backup tags, state enums, mutation-stream IDs, pause keys, snapshot intervals, target snapshot versions, backup container metadata, and restore requests. `modifyBackup` performs transactionally guarded mutations to existing `BackupConfig` records, verifying the tag, aborted flag, runnable state, optional UID, new container, encryption metadata, and snapshot interval fields before commit.

Agent status is persisted under layer status key ranges. Status documents use JSON operators such as `$expires`, `$sum`, `$max`, and `$latest`, so dead agents age out without explicit cleanup. The status payload includes process information, locality, blob I/O stats, backup tag state, restorable version lag, byte counters, mutation stream IDs, pause state, and encryption key setup status.

Container operations persist to external backup stores through `IBackupContainer`: create/open, describe, list, expire, delete, dump file lists, get restore sets, and write encryption metadata. Blob credentials are loaded from CLI files and environment; proxy settings may come from `HTTP_PROXY` or `HTTPS_PROXY`.

## Dependencies and Integration Points

The file integrates FoundationDB Flow actors/coroutines, client APIs, `BackupAgent.h`, `BackupContainer.h`, `ManagementAPI.h`, `BulkLoading.h`, TLS and blob credential setup, JSON status builders, `SimpleOpt`, and platform-specific parent PID watching on Windows. Newer BulkDump/BulkLoad behavior is exposed through `SnapshotMode` and `RestoreMode`, but actual data movement is delegated below the CLI layer. `AuditStorageCommand.cpp` and the shell tests rely on restore-prefix behavior and backup status output from this file.

## Risks and Edge Cases

Argument reordering is broad: it validates against all option arrays before the specific subcommand parser runs, so an option valid for one command can be reordered and then rejected later by the selected `CSimpleOpt` table. This improves flexible command positioning but makes option-table drift risky. `BackupModifyOptions::hasChanges` ignores `encryptionKeyFile` unless a destination URL or interval is also present, matching the later warning that key-only changes do not apply, but it may surprise users. Relative negative versions and days-based parsing depend on `CORE_VERSIONSPERSECOND` approximations. `openBackupContainer` blocks `../` substrings but delegates full URL validation to container implementations. BulkDump snapshot generation is asynchronous from backup submission, so status becoming restorable does not necessarily mean all BulkDump metadata is already visible.

Restore validation rejects simultaneous target version and timestamp, requires an original cluster file to resolve timestamps, and supports incremental-only mutation-log restore into non-empty destinations. Encryption requires a key file before a positive block size can be accepted. BulkLoad restore mode is passed as a boolean choice to `FileBackupAgent::restore`; missing or incomplete BulkDump datasets are expected to surface below this layer.

## Test Signals

The `EXCLUDE_MAIN_FUNCTION` block includes parser tests for command reordering, `--opt=value`, missing parameters, prefix knob options, option-as-parameter behavior, and query command cluster-file support. The shell tests in this work item exercise local and blob backup/restore, encryption mismatch failures, partitioned mutation logs, BulkDump snapshot mode `both`, BulkLoad restore mode, and status JSON. `BulkDumpCommand.cpp` notes that status output is ctest-dependent, which also makes this CLI output a compatibility surface.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/backup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/Decode.h -->
# sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/Decode.h

## Purpose

`Decode.h` is a small public header for backup CLI string decoding. It declares the function used by `backup.cpp` to transform user-supplied hex-escaped restore prefixes into byte strings.

## Important APIs, Types, and Functions

The only API is `std::string decode_hex_string(std::string line, bool& err)`. The input is passed by value, allowing the implementation to modify a copy if needed. `err` is an out-parameter indicating parse failure, instead of throwing. The return value is the decoded byte string.

## Control Flow

The header itself has no control flow beyond include guards and `#pragma once`. Its observable behavior is through callers. In `backup.cpp`, `decode_hex_string` is called for `--add-prefix` and `--remove-prefix`; if `err` is set, the CLI prints a targeted parse error and exits before submitting a restore.

## State and Persistence Behavior

The header defines no persistent state. Its output can affect persistent restore behavior because decoded prefixes are passed into `FileBackupAgent::restore`, determining how restored keys are transformed in the destination database.

## Dependencies and Integration Points

It depends only on `<string>`. It is included by `fdbbackup/backup.cpp` and is part of the `fdbbackup` include surface rather than a local anonymous helper. The parser complements `backup.cpp` key-range parsing, which handles quoted strings and `\xNN` escapes for range arguments.

## Risks and Edge Cases

Because error reporting uses a mutable boolean out-parameter, callers must initialize or check it correctly. Prefix decoding is security-sensitive in restore workflows: a misdecoded prefix can restore into the wrong keyspace, especially system-key prefixes used by validation tests. There is no namespace, so the function name is global.

## Test Signals

The BulkDump/BulkLoad validation script passes `--add-prefix '\xff\x02/rlog/'`, exercising this API through `fdbrestore`. Restore-prefix failures would break audit-based restore validation and any tests using prefixed restore into system keyspace.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/Decode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/FileConverter.h -->
# sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/FileConverter.h

## Purpose

`FileConverter.h` defines the CLI option identifiers and `CSimpleOpt` option table for the fdbbackup file-converter tool. The converter appears to read backup files or containers, filter versions/key prefixes, validate filters, optionally save output, and handle encryption/blobstore transport.

## Important APIs, Types, and Functions

The header exposes namespace `file_converter`, an anonymous enum of option IDs, and the global `CSimpleOpt::SOption gConverterOptions[]`. Supported options include container URL (`-r`, `--container`), file type (`-t`, `--file-type`), version bounds (`--begin`, `--end`), input file (`-i`, `--input`), blob credentials, trace settings, list-only, filter validation, key prefix and hex prefix, proxy, begin/end version filters, knobs, save mode, and encryption key file. It also embeds `TLS_OPTION_FLAGS`, making TLS configuration available to the converter.

## Control Flow

There is no executable logic in this header, but the option table controls downstream converter parse flow. `SO_REQ_SEP` options require a separate argument; `SO_NONE` options are flags; `--knob-` is a prefix option. `SO_END_OF_OPTIONS` terminates the table.

## State and Persistence Behavior

No state is directly stored by the header. Runtime converter behavior can read containers, local input files, credentials, and encryption keys; `--save` suggests it may write converted files. Trace options affect log output, and knob options alter client/runtime behavior.

## Dependencies and Integration Points

The header depends on `<cinttypes>`, `SimpleOpt/SimpleOpt.h`, and `flow/TLSConfig.h`. It shares CLI conventions with `backup.cpp`: blob credentials, TLS flags, trace options, proxy, knobs, encryption key file, and version-oriented filtering. Because the option array is defined in the header rather than declared `extern`, inclusion from multiple translation units would risk duplicate definitions unless intentionally included once.

## Risks and Edge Cases

The enum values are positional and coupled to the option table; adding new options must preserve uniqueness. Defining `gConverterOptions` in a header is a linkage hazard. Prefix filtering has both raw and hex forms, so call sites must reject ambiguous combinations if that matters. Since TLS and blob credentials are available at this layer, converter tests need to cover both local and blobstore inputs.

## Test Signals

No tests in this subset directly invoke the file converter, but the shared backup tests cover adjacent option families: blob credentials, TLS-related S3 setup, encryption key files, proxy avoidance, and versioned backup container handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/FileConverter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/backup_tests_common.sh -->
# sources/storage-engines/foundationdb/fdbbackup/tests/backup_tests_common.sh

## Purpose

`backup_tests_common.sh` is the shared shell harness for backup/restore integration tests. It abstracts command-argument construction, S3/MockS3 cleanup, backup submission and polling, restore submission and polling, encryption mismatch assertions, and common cluster setup.

## Important APIs, Types, and Functions

`add_base_args` appends cluster-file and trace-log flags, choosing `-C` for backup commands and `--dest-cluster-file` for restore commands. `add_common_optional_args` appends blob credentials, `--mode`, encryption key file, and global `KNOBS`. `s3_preclear_url` and `s3_cleanup_url` wrap `s3client rm` with provider-specific TLS behavior. `run_backup` starts `fdbbackup start`, polls `fdbbackup status` until the backup is restorable or complete, optionally waits for BulkDump snapshot metadata, then discontinues the backup. `run_restore` starts `fdbrestore start` and polls status until completion or failure. `test_encryption_mismatches` asserts the expected failure matrix for encrypted and unencrypted backups. `run_restore_wait`, `setup_backup_test_environment`, and `setup_fdb_cluster_with_backup` support higher-level scripts.

## Control Flow

The helper expects strict-mode callers and uses bash namerefs to mutate argument arrays. Backup flow is deliberately non-blocking at first: it avoids `-w`, polls status for up to 10 minutes, logs progress every 30 seconds, and handles already-completed backups as success. For `bulkdump` or `both` snapshot modes, it runs an additional describe loop looking for `bulkDumpJobId` or `,bulk` because BulkDump snapshot metadata can appear after rangefile restorability. Restore flow similarly starts asynchronously and polls `fdbrestore status`, treating completed state, complete phase, or missing restore tag as success while rejecting aborted state or non-`None` `LastError`.

## State and Persistence Behavior

The helpers create and clean blobstore paths, scratch log directories, temporary encryption key files, and test clusters. They mutate the test database by loading, clearing, restoring, and validating data through external functions from `tests_common.sh`. They depend on global variables such as `USE_S3`, `KNOBS`, `TLS_CA_FILE`, `USE_PARTITIONED_LOG`, and `USE_ENCRYPTION_BLOCK_SIZE`.

## Dependencies and Integration Points

This script sources `../../fdbclient/tests/tests_common.sh` when available and is used by blob, directory, and BulkDump/BulkLoad tests. It integrates `fdbbackup`, `fdbrestore`, `s3client`, `backup_agent`, MockS3/AWS fixtures, TLS CA setup, and output matcher helpers.

## Risks and Edge Cases

The helpers parse human-readable CLI output, so output text changes can break tests. The BulkDump metadata wait only warns on timeout and proceeds, which helps avoid flakiness but can hide delayed BulkDump failures until restore or audit. Randomized encryption and partitioned-log toggles broaden coverage but make individual failures less reproducible unless logs preserve the chosen flags. The restore failure check avoids false positives from `LastError: None`, which is an important regression guard.

## Test Signals

This file is itself the test signal source for this subset. It checks restorable/completed backup status, BulkDump snapshot markers, restore phases, encryption mismatch failures, status JSON via `test_fdbcli_status_json_for_bkup`, data verification, and absence of Severity=40 logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/backup_tests_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/blob_backup_restore_test.sh -->
# sources/storage-engines/foundationdb/fdbbackup/tests/blob_backup_restore_test.sh

## Purpose

`blob_backup_restore_test.sh` is an end-to-end backup and restore test for blob storage using S3, GCS, Azure, or MockS3Server depending on environment. It validates that data can be backed up to blob storage, cleared from FoundationDB, restored, and verified, with optional encryption and partitioned mutation-log coverage.

## Important APIs, Types, and Functions

The script defines `cleanup`, `resolve_to_absolute_path`, and `test_s3_backup_and_restore`. The test function pre-clears the target object path, loads data, calls shared `run_backup`, checks backup status JSON, clears data, runs encryption mismatch tests, calls shared `run_restore`, verifies data, cleans the blob path, and scans logs for Severity=40.

## Control Flow

Strict bash options are enabled after function definitions. The script randomly chooses `USE_ENCRYPTION` and `USE_PARTITIONED_LOG`; if encryption is enabled, it may also randomly set `USE_ENCRYPTION_BLOCK_SIZE`. It resolves its directory, sources `tests_common.sh` and `backup_tests_common.sh`, sets up provider-specific blobstore environment with `setup_backup_test_environment` and `setup_s3_environment`, starts a one-process FDB cluster plus backup agent, constructs a `blobstore://` URL, and runs the test.

Cleanup is installed for process termination and normal exit. It uses a 30-second watchdog, respects preservation mode, shuts down FDB and blob fixtures, calls AWS cleanup if available, and removes the encryption key file.

## State and Persistence Behavior

The script mutates a temporary FDB cluster, blobstore bucket/prefix, scratch logs, and optionally an encryption key file. For real S3, KMS encryption knobs and TLS CA handling are inherited from common setup. The target cleanup URL rewrites `ctest` to `data/ctest`, matching backup container layout behavior.

## Dependencies and Integration Points

It depends on `backup_tests_common.sh`, shared FDB test fixtures, MockS3/AWS setup, `fdbbackup`, `fdbrestore`, `backup_agent`, and status/data verification helpers. It directly exercises `backup.cpp` options for blob credentials, encryption key file, encryption block size, partitioned mutation logs, cluster file, tag, destination container, and restore container.

## Risks and Edge Cases

Randomized feature selection can expose interactions but makes failure reproduction depend on logged globals. Cleanup must tolerate missing functions because failures can happen before all fixtures are sourced or started. The test assumes the edited cleanup URL accurately tracks the container data path. The encryption mismatch checks intentionally run before successful restore, so they must not leave persistent restore state that interferes with the real restore tag.

## Test Signals

Passing this script signals that blob credentials, object cleanup, backup agent status, blob backup submission, restorable polling, restore polling, encryption mismatch handling, data verification, and fatal-log scanning all work for the selected provider mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/blob_backup_restore_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/dir_backup_test.sh -->
# sources/storage-engines/foundationdb/fdbbackup/tests/dir_backup_test.sh

## Purpose

`dir_backup_test.sh` is the local filesystem counterpart to the blob backup test. It verifies `file://` backup containers, restore from the most recent generated backup directory, optional file-level encryption, optional encryption block-size override, and optional partitioned mutation-log backup.

## Important APIs, Types, and Functions

The script defines `cleanup`, `resolve_to_absolute_path`, `backup`, `restore`, and `test_dir_backup_and_restore`. `backup` runs `fdbbackup start -w` against `file://${scratch_dir}/backups` with optional encryption and partitioned-log flags. `restore` finds the newest `backup-*` subdirectory and runs `fdbrestore start -w` against it. The top-level test loads data, backs up, checks status JSON, clears data, tests encryption mismatch behavior against the concrete backup path, restores, verifies data, and checks logs.

## Control Flow

The script uses strict bash mode, randomizes partitioned log and encryption options, resolves its directory, sources cluster and common test fixtures, sets `FDB_DATA_KEYCOUNT=10` for a smaller dataset, creates a temporary scratch directory, optionally creates an encryption key, starts a one-process cluster and backup agent, then runs the test.

Cleanup is trap-driven, guarded by a 30-second watchdog, respects preservation mode, shuts down the cluster, removes the scratch directory, and deletes the encryption key file.

## State and Persistence Behavior

Persistent test artifacts live under the temporary scratch directory: cluster files, logs, backup container directories, generated backup names, and encryption keys. The test database is loaded, cleared, restored, and verified. Unlike the shared asynchronous helper, `backup` and `restore` use `-w`, so command completion is the primary synchronization point.

## Dependencies and Integration Points

The script uses `fdb_cluster_fixture.sh`, `tests_common.sh`, `backup_tests_common.sh`, `fdbbackup`, `fdbrestore`, and `backup_agent`. It exercises local URL handling in `backup.cpp`, including the backup container path, tag handling, trace logs, encryption flags, and mutation log type.

## Risks and Edge Cases

The restore path is selected with `ls -dt ... | head -1`, which assumes backup directory naming and mtimes are reliable. There is a likely typo, `readonly sourcedir`, after assigning `source_dir`; if bash treats the missing variable as creating an empty readonly `sourcedir`, the actual `source_dir` remains usable but this line is suspicious. Randomized encryption settings again require logs for reproduction. Since `-w` is used, hung backup/restore behavior would rely on external CTest timeouts rather than the polling logic in the shared helper.

## Test Signals

Passing this script signals that local directory backup/restore works, status JSON is valid, encryption mismatch failures are enforced for local containers, restored data matches expected values, and no Severity=40 log events were produced.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/dir_backup_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/s3_backup_bulkdump_bulkload.sh -->
# sources/storage-engines/foundationdb/fdbbackup/tests/s3_backup_bulkdump_bulkload.sh

## Purpose

`s3_backup_bulkdump_bulkload.sh` validates the newer BulkDump/BulkLoad backup path against traditional rangefile restore. It creates a backup in `both` snapshot mode so range files and SST files coexist, restores a traditional prefixed baseline, restores normal keys using BulkLoad when possible, and uses `audit_storage validate_restore` to compare results.

## Important APIs, Types, and Functions

Key functions are `restore_with_prefix_for_validation`, `run_validate_restore_audit`, `cleanup_validation_prefix`, and `test_bulkdump_bulkload`. `VALIDATION_PREFIX` is `\xff\x02/rlog/`, with end prefix `\xff\x02/rlog0`. `restore_with_prefix_for_validation` runs `fdbrestore start --add-prefix` with a validation tag and waits for completion. `run_validate_restore_audit` starts `audit_storage validate_restore "" \xff`, extracts the audit ID, retries transient errors, and polls `get_audit_status`. `test_bulkdump_bulkload` orchestrates data load, `run_backup` in `both` mode, prefixed rangefile restore, normal-key clear, BulkLoad or rangefile restore depending on encryption, audit comparison, cleanup, verification, encryption mismatch checks, blob cleanup, and log scanning.

## Control Flow

The script parses optional flags for encryption and partitioned-log coverage, including random variants. It sets a small data count, sources common test utilities, initializes provider environment, creates an encryption key when requested, starts a two-storage-server FDB cluster with BulkLoad-related knobs, and runs one blobstore URL test. The two-storage-server setup is intentional so BulkLoad can find a destination server distinct from the BulkDump source.

If encryption is enabled, BulkLoad validation is skipped because BulkLoad does not support encrypted backup data yet; the script falls back to rangefile restore and still verifies data and encryption mismatch behavior.

## State and Persistence Behavior

The script writes blobstore backup data, FDB cluster state, scratch logs, optional encryption key files, and temporary restored validation data under the system key prefix. It explicitly clears the validation prefix after audit or after encrypted fallback. Audit state is stored by the cluster audit subsystem and queried via `get_audit_status`.

## Dependencies and Integration Points

This script ties together `backup.cpp` snapshot mode `both`, restore mode `bulkload`, `Decode.h` prefix decoding, `BulkDumpCommand.cpp`/bulk dumping backend behavior, `AuditStorageCommand.cpp` validate-restore audit, blob credentials, MockS3/AWS fixtures, and shared backup helpers. It also depends on knobs `shard_encode_location_metadata`, `enable_read_lock_on_range`, and blobstore encryption configuration.

## Risks and Edge Cases

The audit ID is extracted by a 32-hex-character regex, so CLI output changes can break detection. Audit success is inferred from `Phase.*2` and failure from phases 3 or 4, making audit status formatting a test contract. Transient retry handling covers selected numeric errors only. Because validation data is restored into system keyspace, cleanup must run even after partial failures to avoid contaminating later tests. BulkLoad and encryption incompatibility is explicitly encoded as a skip, so encrypted runs do not validate BulkLoad equivalence.

## Test Signals

Passing this script signals that `both` backups produce usable rangefile and BulkDump/SST metadata, traditional prefixed restore works, BulkLoad restore can reproduce traditional restore output for plaintext backups, audit-based comparison succeeds, validation-prefix cleanup works, encryption mismatch failures still hold, and no Severity=40 errors occur.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/tests/s3_backup_bulkdump_bulkload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/AdvanceVersionCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/AdvanceVersionCommand.cpp

## Purpose

`AdvanceVersionCommand.cpp` implements the `fdbcli advanceversion <VERSION>` command. It forces a cluster to advance to at least the supplied commit version through the special key space, primarily for forced recovery or version-floor management.

## Important APIs, Types, and Functions

The command defines `advanceVersionSpecialKey` as `\xff\xff/management/min_required_commit_version`. `advanceVersionCommandActor` parses the target version, creates transactions, enables special-key-space writes, reads the current read version, writes the requested version when the current version is not yet above it, commits, and retries until the read version has advanced. `advanceVersionFactory` registers command help.

## Control Flow

The actor requires exactly two tokens. It parses the second token with `sscanf` and `%n` to reject trailing garbage. In a retry loop, it sets `SPECIAL_KEY_SPACE_ENABLE_WRITES`, gets a read version, writes the minimum required commit version if `rv <= v`, commits, and loops again. Once the observed read version is greater than the requested version, it prints the current read version and returns success. Errors are handled through `tr->onError`.

## State and Persistence Behavior

The command writes to a management special key, causing the cluster to recover or move forward to satisfy the minimum required commit version. It does not directly write ordinary key-value data, but the side effect is cluster-wide and operationally significant.

## Dependencies and Integration Points

It uses `fdbcli/fdbcli.h`, `IClientApi`, Flow arena/ref helpers, `safeThreadFutureToFuture`, `boost::lexical_cast`, and `fmt`. It runs inside the fdbcli command factory framework and relies on special-key-space semantics implemented below the client API.

## Risks and Edge Cases

The command loops after commit until a subsequent read version proves the cluster is past the target, so very large requested versions can have operational impact. It accepts signed `Version` syntax; negative or nonsensical operational values are not explicitly rejected in this file. Because it writes special keys, missing transaction option setup would fail. Retrying through `onError` is standard but may repeat the special-key write.

## Test Signals

No direct test from this subset targets `advanceversion`. Basic command testing would need to verify argument count, invalid version parse rejection, special-key write permissions, retry behavior, and final printed read version.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/AdvanceVersionCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/AuditStorageCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/AuditStorageCommand.cpp

## Purpose

`AuditStorageCommand.cpp` implements the `fdbcli audit_storage` command family. It starts or cancels cluster storage audits for high availability, replica consistency, location metadata, storage-server shards, restore validation, and metadata encoding.

## Important APIs, Types, and Functions

`auditStorageCommandActor` maps command tokens to `AuditType` values and returns the relevant audit `UID`. Startable audit types include `ValidateHA`, `ValidateReplica`, `ValidateLocationMetadata`, `ValidateStorageServerShard`, `ValidateRestore`, and `ValidateMetadataEncoding`. Cancel supports the first five distributed audit types. For HA and replica audits, an optional storage engine filter is parsed through `KeyValueStoreType::fromString` and restricted to `SSD_BTREE_V2`, `SSD_ROCKSDB_V1`, and `SSD_SHARDED_ROCKSDB`. `auditStorageFactory` registers help.

## Control Flow

With `audit_storage cancel <type> <id>`, the actor validates token count, maps the type, parses the UID, and calls `cancelAuditStorage` with a 60-second timeout. For start commands, it maps the type, optionally handles `metadata_encoding` as a client-side scan via `checkMetadataEncodingCommandActor`, parses begin/end key arguments, validates `end <= allKeys.end` and `begin < end`, optionally parses the engine filter, and calls `auditStorage` with the key range and timeout.

## State and Persistence Behavior

Distributed audits are persisted through FoundationDB management APIs and later observed by `get_audit_status`. Cancelling mutates audit state for the specified audit ID. The metadata encoding path creates a synthetic local audit ID but performs client-side validation rather than submitting a distributed audit.

## Dependencies and Integration Points

The file depends on `ManagementAPI.h`, `NativeAPI.actor.h`, and `Audit.h`. It integrates directly with backup/restore validation: `s3_backup_bulkdump_bulkload.sh` uses `audit_storage validate_restore "" \xff` after restoring a traditional prefixed baseline and a BulkLoad result, then polls `get_audit_status validate_restore id <AuditID>`.

## Risks and Edge Cases

Token count handling differs by audit type: most audits can use default full range, one begin key, begin/end, or begin/end/engine for selected types. Invalid ranges silently fall back to usage output and empty UID. `UID::fromString` is not guarded locally, so malformed cancel IDs depend on lower-level behavior. `ValidateMetadataEncoding` is start-only, not cancelable through this branch. Help text includes the supported engine and type names and is therefore a compatibility surface.

## Test Signals

The BulkDump/BulkLoad script is a direct integration test for `ValidateRestore`. It expects the command to print a 32-hex-character audit ID, and it treats audit phase 2 as success. Additional tests should cover cancel paths, invalid ranges, unsupported engine filters, and metadata encoding behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/AuditStorageCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/BulkDumpCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/BulkDumpCommand.cpp

## Purpose

`BulkDumpCommand.cpp` implements the `fdbcli bulkdump` command family used to enable BulkDump mode, submit SST dump jobs, query progress, and cancel jobs. It is the CLI control surface for bulk dumping ranges to local directories or blobstore URLs.

## Important APIs, Types, and Functions

The command exposes usage strings for `mode`, `dump`, `status`, and `cancel`. `getOngoingBulkDumpJob` reports whether a submitted job exists. `getBulkDumpCompleteRanges` prints completed task count for a range. `bulkDumpCommandActor` handles all subcommands. It calls `getBulkDumpMode`, `setBulkDumpMode`, `createBulkDumpJob`, `submitBulkDumpJob`, `validateBulkJobId`, `cancelBulkDumpJob`, `getBulkDumpProgress`, `getSubmittedBulkDumpJob`, `getBulkOwnerSuffix`, `formatBytesProgress`, and `printProgressMetrics`.

## Control Flow

`bulkdump mode` with no value prints enabled/disabled state. `bulkdump mode on|off` writes the mode and emits a trace event. `bulkdump dump <BEGINKEY> <ENDKEY> <DIR>` first requires mode enabled, validates token count, checks the range is non-empty and within normal keyspace, creates a `BulkDumpState` for SST output, chooses `BLOBSTORE` transport if the destination starts with `blobstore://` and otherwise `CP`, submits the job, and returns its job ID. `bulkdump cancel <JOBID>` validates the ID and cancels future task spawning. `bulkdump status` prints aggregate progress, owner suffix, task counts, byte progress, ETA/rate metrics, and error warning.

## State and Persistence Behavior

Mode changes and job submissions are persisted in cluster metadata through BulkDump management APIs. Submitted jobs include range, root path, dump type `SST`, transport method, and job ID. Progress is aggregated from task state in the cluster. Cancelled jobs remain identifiable but stop spawning new tasks.

## Dependencies and Integration Points

The file depends on `BulkDumping.h`, `BulkLoading.h`, `ManagementAPI.h`, Flow utilities, and fdbcli command registration. Backup mode `bulkdump` and `both` from `backup.cpp` rely on the same BulkDump backend concepts even though backup submission is routed through `FileBackupAgent`. The BulkDump/BulkLoad shell test depends on BulkDump snapshot metadata generated by backup code and on status text stability from this command family.

## Risks and Edge Cases

BulkDump dump refuses system keyspace ranges because BulkLoad can only inject normal keys. Destination transport is inferred by a simple `blobstore://` prefix check. Status output has an explicit ctest dependency comment, so formatting changes can break tests. The `jobState` loaded during status is currently not used except to exercise the transaction path before owner suffix retrieval, which may be intentional future-proofing or leftover code.

## Test Signals

The direct status output contract is used by ctests outside this file. The `s3_backup_bulkdump_bulkload.sh` test indirectly validates BulkDump by requiring `both` backup mode to produce SST data that BulkLoad can restore identically to rangefile restore.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/BulkDumpCommand.cpp -->
