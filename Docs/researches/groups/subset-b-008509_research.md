# Group Research: subset-b-008509

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessSwitchover.toml -->
# sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessSwitchover.toml

## Purpose
Exercises API correctness while an AtomicSwitchover workload moves traffic to the extra single database, with a Status workload observing the transition.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ApiCorrectnessTest. Workload entry points are `ApiCorrectness`, `AtomicSwitchover`, `Status`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ApiCorrectness`(numKeys=2500, onlyLowerCase=True, shortKeysRatio=0.5, minShortKeyLength=1, maxShortKeyLength=3, minLongKeyLength=1, maxLongKeyLength=64, minValueLength=1); `AtomicSwitchover`; `Status`(testDuration=30.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: ApiCorrectnessTest: clearAfterTest=False, simBackupAgents='BackupToDB', timeout=2100, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
Status workload validates status reporting during the scenario; correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessSwitchover.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessWithConsistencyCheck.toml -->
# sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessWithConsistencyCheck.toml

## Purpose
Runs the API correctness workload with replica consistency checks on reads enabled, stressing read validation against the same operation mix.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ApiCorrectnessWithConsistencyCheck. Workload entry points are `ApiCorrectness`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ApiCorrectness`(numKeys=5000, onlyLowerCase=True, shortKeysRatio=0.5, minShortKeyLength=1, maxShortKeyLength=3, minLongKeyLength=1, maxLongKeyLength=128, minValueLength=1).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: ApiCorrectnessWithConsistencyCheck: clearAfterTest=True, timeout=2100, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: enable_replica_consistency_check_on_reads=True.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessWithConsistencyCheck.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupAndRestore.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupAndRestore.toml

## Purpose
Stages a partitioned-log Backup workload, a Restore workload, and a post-restore Cycle check for file-backed backup agents.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 3 `[[test]]` block(s): BackupPartitioned, RestorePartitioned, CycleAfterRestore. Workload entry points are `Cycle`, `Backup`, `Restore`, `Cycle`. Configuration keys include testClass='Backup', configuration=.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0); `Backup`(mutationLogType=1, backupAfter=10.0, restoreAfter=60.0); `Restore`; `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=10.0, skipSetup=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupPartitioned: clearAfterTest=False, runConsistencyCheck=False, waitForQuiescence=False, simBackupAgents='BackupToFile'; RestorePartitioned: runConsistencyCheck=False, waitForQuiescence=False, simBackupAgents='BackupToFile', clearAfterTest=False; CycleAfterRestore: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupAndRestore.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupCorrectnessPartitioned.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupCorrectnessPartitioned.toml

## Purpose
Combines Cycle traffic with BackupAndRestorePartitionedCorrectness over all ranges to validate partitioned backup correctness.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupAndRestorePartitioned. Workload entry points are `Cycle`, `BackupAndRestorePartitionedCorrectness`. Configuration keys include testClass='Backup', configuration=.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0); `BackupAndRestorePartitionedCorrectness`(backupAfter=10.0, restoreAfter=60.0, backupRangesCount=-1).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupAndRestorePartitioned: clearAfterTest=False, simBackupAgents='BackupToFile'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupCorrectnessPartitioned.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupNewAndOldRestore.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupNewAndOldRestore.toml

## Purpose
Creates both partitioned-log and default-log backups, restores one of the two tags, then validates data with Cycle.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): NewBackup, OldBackup, RestoreRandomBackup, CycleAfterRestore. Workload entry points are `Cycle`, `Backup`, `Cycle`, `Backup`, `Restore`, `Cycle`. Configuration keys include testClass='Backup', configuration=.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0); `Backup`(mutationLogType=1, backupTag='newBackup', backupAfter=10.0, restoreAfter=60.0); `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0, skipSetup=True); `Backup`(mutationLogType=0, backupTag='oldBackup', backupAfter=10.0, restoreAfter=60.0); `Restore`(backupTag1='newBackup', backupTag2='oldBackup'); `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=10.0, skipSetup=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: NewBackup: clearAfterTest=False, simBackupAgents='BackupToFile'; OldBackup: runConsistencyCheck=False, waitForQuiescence=False, clearAfterTest=False, simBackupAgents='BackupToFile'; RestoreRandomBackup: runConsistencyCheck=False, waitForQuiescence=False, simBackupAgents='BackupToFile', clearAfterTest=False; CycleAfterRestore: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupNewAndOldRestore.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupOldAndNewRestore.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupOldAndNewRestore.toml

## Purpose
Mirrors the new/old backup compatibility scenario in the opposite order to catch ordering-dependent restore bugs.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): OldBackup, NewBackup, RestoreRandomBackup, CycleAfterRestore. Workload entry points are `Cycle`, `Backup`, `Cycle`, `Backup`, `Restore`, `Cycle`. Configuration keys include testClass='Backup', configuration=.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0); `Backup`(mutationLogType=0, backupTag='oldBackup', backupAfter=10.0, restoreAfter=60.0); `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=30.0, skipSetup=True); `Backup`(mutationLogType=1, backupTag='newBackup', backupAfter=10.0, restoreAfter=60.0); `Restore`(backupTag1='oldBackup', backupTag2='newBackup'); `Cycle`(nodeCount=3000, transactionsPerSecond=2500.0, testDuration=10.0, skipSetup=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: OldBackup: runConsistencyCheck=False, waitForQuiescence=False, clearAfterTest=False, simBackupAgents='BackupToFile'; NewBackup: runConsistencyCheck=False, waitForQuiescence=False, clearAfterTest=False, simBackupAgents='BackupToFile'; RestoreRandomBackup: runConsistencyCheck=False, waitForQuiescence=False, simBackupAgents='BackupToFile', clearAfterTest=False; CycleAfterRestore: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupOldAndNewRestore.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestore.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestore.toml

## Purpose
Validates S3 blob backup output by comparing BulkLoad restore from SST files with traditional range-file restore.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupS3BlobBulkLoadRestore. Workload entry points are `Cycle`, `BackupS3BlobCorrectness`. Configuration keys include testClass='Backup', configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, generateFearless=False, simpleConfig=False, minimumRegions=1, extraMachineCountDC=3, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False, faultInjection=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=100, transactionsPerSecond=100.0, testDuration=30.0); `BackupS3BlobCorrectness`(backupAfter=10.0, restoreAfter=600.0, abortAndRestartAfter=0.0, stopDifferentialAfter=0.0, performRestore=True, backupRangesCount=-1, skipDirtyRestore=False, backupURL='blobstore://mocks3:mocksecret:mocktoken@127.0.0.1:8080/backup_container?bucket=backup_bucket&region=us-east-1&secure_connection=0&cwpf=1&cu=1').

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupS3BlobBulkLoadRestore: useDB=True, clearAfterTest=False, simBackupAgents='BackupToFile', waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=3600.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000, bulkdump_job_timeout=1200, bulkload_job_timeout=1200; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; backup agents/modes: BackupToFile, blobstore.

## Risks
bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestore.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreMultiRange.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreMultiRange.toml

## Purpose
Validates BulkDump/BulkLoad restore across five non-contiguous backup ranges and region-capable configuration.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupS3BlobBulkLoadRestoreMultiRange. Workload entry points are `Cycle`, `BackupS3BlobCorrectness`. Configuration keys include testClass='Backup', configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, generateFearless=True, simpleConfig=False, minimumRegions=2, extraMachineCountDC=3, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False, faultInjection=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=200, transactionsPerSecond=150.0, testDuration=30.0); `BackupS3BlobCorrectness`(backupAfter=10.0, restoreStartAfterBackupFinished=30.0, abortAndRestartAfter=0.0, stopDifferentialAfter=0.0, performRestore=True, backupRangesCount=5, backupRangeLengthMax=10, skipDirtyRestore=False).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupS3BlobBulkLoadRestoreMultiRange: useDB=True, clearAfterTest=False, simBackupAgents='BackupToFile', waitForQuiescence=False, waitForQuiescenceEnd=False, runConsistencyCheck=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=7200.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000, bulkdump_job_timeout=5400, bulkload_job_timeout=5400; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; backup agents/modes: BackupToFile, blobstore.

## Risks
bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreMultiRange.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreWithChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreWithChaos.toml

## Purpose
Runs BulkDump/BulkLoad restore through MockS3 with very light injected S3 errors, throttling, and delays.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupS3BlobBulkLoadRestoreWithChaos. Workload entry points are `Cycle`, `BackupS3BlobCorrectness`. Configuration keys include testClass='Backup', configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, generateFearless=True, simpleConfig=False, minimumRegions=2, extraMachineCountDC=3, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False, faultInjection=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=200, transactionsPerSecond=150.0, testDuration=30.0); `BackupS3BlobCorrectness`(backupAfter=15.0, restoreStartAfterBackupFinished=60.0, abortAndRestartAfter=0.0, stopDifferentialAfter=0.0, performRestore=True, backupRangesCount=-1, skipDirtyRestore=False, backupURL='blobstore://mocks3:mocksecret:mocktoken@127.0.0.1:8080/backup_container?bucket=backup_bucket&region=us-east-1&secure_connection=0&cwpf=1&cu=1').

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupS3BlobBulkLoadRestoreWithChaos: useDB=True, clearAfterTest=False, simBackupAgents='BackupToFile', waitForQuiescence=False, waitForQuiescenceEnd=False, runConsistencyCheck=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=7200.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000, bulkdump_job_timeout=5400, bulkload_job_timeout=5400; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=600, blobstore_request_timeout_min=600, blobstore_request_tries=20, blobstore_connect_tries=20, blobstore_connect_timeout=120, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; backup agents/modes: BackupToFile, blobstore.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.005, throttleRate=0.01, delayRate=0.005, corruptionRate=0.0, maxDelay=0.3; bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreWithChaos.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobCorrectnessHeavyChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupS3BlobCorrectnessHeavyChaos.toml

## Purpose
Runs BackupS3BlobCorrectness with aggressive S3 chaos plus network clogging and rollback workloads.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupS3BlobCorrectnessHeavyChaos. Workload entry points are `Cycle`, `BackupS3BlobCorrectness`, `RandomClogging`, `Rollback`. Configuration keys include testClass='Backup', configuration=buggify=False, faultInjection=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=30000, transactionsPerSecond=2500.0, testDuration=30.0); `BackupS3BlobCorrectness`(backupAfter=35.0, restoreStartAfterBackupFinished=30.0, abortAndRestartAfter=0.0, stopDifferentialAfter=0.0, performRestore=True, backupRangesCount=-1, skipDirtyRestore=False, backupURL='blobstore://mocks3:mocksecret:mocktoken@127.0.0.1:8080/backup_container?bucket=backup_bucket&region=us-east-1&secure_connection=0&cwpf=1&cu=1'); `RandomClogging`(testDuration=400.0); `Rollback`(meanDelay=90.0, testDuration=400.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupS3BlobCorrectnessHeavyChaos: clearAfterTest=False, simBackupAgents='BackupToFile', waitForQuiescenceEnd=False, runConsistencyCheck=False.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile, blobstore.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.25, throttleRate=0.3, delayRate=0.15, corruptionRate=0.01, maxDelay=10.0; failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobCorrectnessHeavyChaos.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3.toml -->
# sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3.toml

## Purpose
Runs BulkDumpingWorkload using blobstore transport to a mock S3 URL under deterministic bulk-load knobs.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BulkDumpingWorkloadS3. Workload entry points are `BulkDumpingWorkload`. Configuration keys include configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, generateFearless=False, simpleConfig=False, minimumRegions=1, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0).

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BulkDumpingWorkloadS3: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=3600.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; backup agents/modes: blobstore.

## Risks
bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3WithChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3WithChaos.toml

## Purpose
Runs stable, light, medium, and heavy S3 chaos variants of BulkDumpingWorkload with long-running timeouts.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): BulkDumpingS3Stable, BulkDumpingS3LightChaos, BulkDumpingS3MediumChaos, BulkDumpingS3HeavyChaos. Workload entry points are `BulkDumpingWorkload`, `BulkDumpingWorkload`, `BulkDumpingWorkload`, `BulkDumpingWorkload`. Configuration keys include configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, longRunningTest=True, generateFearless=False, simpleConfig=False, minimumRegions=1, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0); `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0, enableChaos=True, errorRate=0.03, throttleRate=0.02, delayRate=0.08, corruptionRate=0.01); `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0, enableChaos=True, errorRate=0.08, throttleRate=0.05, delayRate=0.15, corruptionRate=0.02); `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0, enableChaos=True, errorRate=0.15, throttleRate=0.1, delayRate=0.25, corruptionRate=0.03).

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BulkDumpingS3Stable: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=3600; BulkDumpingS3LightChaos: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=7200, maxDDRunTime=2400; BulkDumpingS3MediumChaos: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=10800, maxDDRunTime=3600; BulkDumpingS3HeavyChaos: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=14400, maxDDRunTime=5400.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0; client knobs: blobstore_max_delay_retryable_error=2, blobstore_max_delay_connection_failed=1; backup agents/modes: blobstore.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.03, throttleRate=0.02, delayRate=0.08, corruptionRate=0.01, maxDelay=0.5; errorRate=0.08, throttleRate=0.05, delayRate=0.15, corruptionRate=0.02, maxDelay=1.0; errorRate=0.15, throttleRate=0.1, delayRate=0.25, corruptionRate=0.03, maxDelay=2.0; bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3WithChaos.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ClogWithRollbacks.toml -->
# sources/storage-engines/foundationdb/tests/slow/ClogWithRollbacks.toml

## Purpose
Compares short Cycle scenarios with and without RandomClogging, Rollback, and Attrition to expose rollback behavior under clogged networks.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): CloggedCycleTest, UncloggedRollbackCycleTest, CloggedRollbackCycleTest, UncloggedCycleTest. Workload entry points are `Cycle`, `RandomClogging`, `RandomClogging`, `Attrition`, `Attrition`, `Cycle`, `Rollback`, `Cycle`, `RandomClogging`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Cycle`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `Cycle`(transactionsPerSecond=5000.0, testDuration=5.0); `RandomClogging`(testDuration=5.0); `RandomClogging`(testDuration=5.0, scale=0.1, clogginess=2.0); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Cycle`(transactionsPerSecond=5000.0, testDuration=5.0); `Rollback`(testDuration=5.0, multiple=False); `Cycle`(transactionsPerSecond=5000.0, testDuration=5.0); `RandomClogging`(testDuration=5.0); `RandomClogging`(testDuration=5.0, scale=0.1, clogginess=2.0); `Rollback`(testDuration=5.0, multiple=False); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Attrition`(machinesToKill=3, machinesToLeave=0, reboot=True, testDuration=5.0); `Cycle`(transactionsPerSecond=5000.0, testDuration=10.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedCycleTest: default flags; UncloggedRollbackCycleTest: default flags; CloggedRollbackCycleTest: default flags; UncloggedCycleTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ClogWithRollbacks.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CloggedCycleTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/CloggedCycleTest.toml

## Purpose
Runs Cycle traffic under two RandomClogging profiles and a coordinator ChangeConfig event.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CloggedCycleTest. Workload entry points are `Cycle`, `RandomClogging`, `RandomClogging`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=1250.0, testDuration=30.0); `RandomClogging`(testDuration=30.0); `RandomClogging`(testDuration=30.0, scale=0.1, clogginess=2.0); `ChangeConfig`(maxDelayBeforeChange=30.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedCycleTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CloggedCycleTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CloggedStorefront.toml -->
# sources/storage-engines/foundationdb/tests/slow/CloggedStorefront.toml

## Purpose
Runs the Storefront workload under network clogging and coordinator reconfiguration.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CloggedStorefrontTest. Workload entry points are `Storefront`, `RandomClogging`, `RandomClogging`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Storefront`(actorsPerClient=20, transactionsPerSecond=200, itemCount=20000, maxOrderSize=6, testDuration=30.0); `RandomClogging`(testDuration=30.0); `RandomClogging`(testDuration=30.0, scale=0.1, clogginess=2.0); `ChangeConfig`(maxDelayBeforeChange=30.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedStorefrontTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CloggedStorefront.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CommitBug.toml -->
# sources/storage-engines/foundationdb/tests/slow/CommitBug.toml

## Purpose
Targets the CommitBug workload while adding swizzled clogging, rollback, and repeated attrition.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CommitBugTest. Workload entry points are `CommitBug`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `CommitBug`; `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0).

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CommitBugTest: clearAfterTest=True, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CommitBug.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ConfigureStorageMigrationTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/ConfigureStorageMigrationTest.toml

## Purpose
Runs ConfigureDatabase with storage migration enabled under network clogging and extra machines.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CloggedConfigureDatabaseTest. Workload entry points are `ConfigureDatabase`, `RandomClogging`, `RandomClogging`. Configuration keys include configuration=extraMachineCountDC=2.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ConfigureDatabase`(testDuration=300.0, allowTestStorageMigration=True); `RandomClogging`(testDuration=300.0); `RandomClogging`(testDuration=300.0, scale=0.1, clogginess=2.0).

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedConfigureDatabaseTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ConfigureStorageMigrationTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ConfigureTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/ConfigureTest.toml

## Purpose
Runs ConfigureDatabase under random clogging to validate database reconfiguration stability.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CloggedConfigureDatabaseTest. Workload entry points are `ConfigureDatabase`, `RandomClogging`, `RandomClogging`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ConfigureDatabase`(testDuration=300.0); `RandomClogging`(testDuration=300.0); `RandomClogging`(testDuration=300.0, scale=0.1, clogginess=2.0).

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CloggedConfigureDatabaseTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ConfigureTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CycleRollbackPlain.toml -->
# sources/storage-engines/foundationdb/tests/slow/CycleRollbackPlain.toml

## Purpose
Minimal baseline for Cycle plus Rollback without clogging.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): UncloggedRollbackCycleTest. Workload entry points are `Cycle`, `Rollback`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=5000.0, testDuration=30.0); `Rollback`(testDuration=30.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: UncloggedRollbackCycleTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/CycleRollbackPlain.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemove.toml -->
# sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemove.toml

## Purpose
Stresses data distribution balancing, selectors, clogging, rollback, attrition, and safe server removal.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DDBalance_Test. Workload entry points are `DDBalance`, `BackgroundSelector`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `RemoveServersSafely`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DDBalance`(testDuration=120.0, transactionsPerSecond=250.0, binCount=1000, writesPerTransaction=5, keySpaceDriftFactor=10, moversPerClient=10, actorsPerClient=100, nodes=100000); `BackgroundSelector`(testDuration=120.0); `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `RemoveServersSafely`(minDelay=0, maxDelay=100, kill1Timeout=30, kill2Timeout=6000).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DDBalance_Test: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemove.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemoveStatus.toml -->
# sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemoveStatus.toml

## Purpose
Adds a Status workload to the DDBalanceAndRemove scenario to validate status reporting during server removal.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DDBalance_Test. Workload entry points are `DDBalance`, `BackgroundSelector`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `RemoveServersSafely`, `Status`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DDBalance`(testDuration=120.0, transactionsPerSecond=250.0, binCount=1000, writesPerTransaction=5, keySpaceDriftFactor=10, moversPerClient=10, actorsPerClient=100, nodes=100000); `BackgroundSelector`(testDuration=120.0); `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `RemoveServersSafely`(minDelay=0, maxDelay=100, kill1Timeout=30, kill2Timeout=6000); `Status`(testDuration=30.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DDBalance_Test: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
Status workload validates status reporting during the scenario; correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DDBalanceAndRemoveStatus.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DifferentClustersSameRV.toml -->
# sources/storage-engines/foundationdb/tests/slow/DifferentClustersSameRV.toml

## Purpose
Exercises read-version behavior across different clusters while switching after a configured delay.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DifferentClustersSameRV. Workload entry points are `DifferentClustersSameRV`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DifferentClustersSameRV`(testDuration=500, switchAfter=50, keyToRead='someKey', keyToWatch='anotherKey').

## State And Persistence Behavior
Persistent and simulated state touched: primarily transient workload state and simulation status.
Clear/setup flags and state controls are declared on tests as: DifferentClustersSameRV: clearAfterTest=False.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DifferentClustersSameRV.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DiskFailureCycle.toml -->
# sources/storage-engines/foundationdb/tests/slow/DiskFailureCycle.toml

## Purpose
Combines Cycle traffic with disk failure injection that stalls, throttles, and corrupts files under triple replication.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DiskFailureCycle. Workload entry points are `Cycle`, `DiskFailureInjection`. Configuration keys include configuration=buggify=False, minimumReplication=3, minimumRegions=3, logAntiQuorum=0, storageEngineExcludeTypes=['memory', 'memory-radixtree', 'ssd-rocksdb-v1', 'ssd-sharded-rocksdb'].

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=2500.0, testDuration=30.0); `DiskFailureInjection`(testDuration=120.0, verificationMode=True, startDelay=3.0, throttleDisk=True, stallInterval=5.0, stallPeriod=5.0, throttlePeriod=30.0, corruptFile=True).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DiskFailureCycle: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/DiskFailureCycle.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ExcludeIncludeStorageServers.toml -->
# sources/storage-engines/foundationdb/tests/slow/ExcludeIncludeStorageServers.toml

## Purpose
Runs ExcludeIncludeStorageServers with a data-distribution knob disabling max shards on large teams.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ExcludeIncludeStorageServers. Workload entry points are `ExcludeIncludeStorageServers`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ExcludeIncludeStorageServers`.

## State And Persistence Behavior
Persistent and simulated state touched: primarily transient workload state and simulation status.
Clear/setup flags and state controls are declared on tests as: ExcludeIncludeStorageServers: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: dd_max_shards_on_large_teams=0.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ExcludeIncludeStorageServers.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/FastTriggeredWatches.toml -->
# sources/storage-engines/foundationdb/tests/slow/FastTriggeredWatches.toml

## Purpose
Exercises FastTriggeredWatches with a long connection-failure disable window.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): FastTriggeredWatchesTest. Workload entry points are `FastTriggeredWatches`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `FastTriggeredWatches`.

## State And Persistence Behavior
Persistent and simulated state touched: primarily transient workload state and simulation status.
Clear/setup flags and state controls are declared on tests as: FastTriggeredWatchesTest: connectionFailuresDisableDuration=100000, timeout=1500.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/FastTriggeredWatches.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/GcGenerations.toml -->
# sources/storage-engines/foundationdb/tests/slow/GcGenerations.toml

## Purpose
Runs Cycle plus GcGenerations in a multi-region remote-double configuration with recovery tracking knobs.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): GcGenerations. Workload entry points are `Cycle`, `GcGenerations`. Configuration keys include configuration=generateFearless=True, processesPerMachine=1, machineCount=20, minimumRegions=2, coordinators=1, remoteConfig='remote_double'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=250.0, testDuration=300.0); `GcGenerations`(testDuration=1000.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: GcGenerations: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: max_write_transaction_life_versions=5000000, record_recover_at_in_cstate=True, track_tlog_recovery=True, cc_recovery_init_req_growth_factor=1.01.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/GcGenerations.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LongRunning.toml -->
# sources/storage-engines/foundationdb/tests/slow/LongRunning.toml

## Purpose
Long-running Cycle and Attrition scenario for sustained failure and workload pressure.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): CycleTestWithKills. Workload entry points are `Cycle`, `Attrition`. Configuration keys include configuration=longRunningTest=True.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=2500.0, testDuration=10000.0); `Attrition`(testDuration=10000.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: CycleTestWithKills: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LongRunning.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LowLatencyWithFailures.toml -->
# sources/storage-engines/foundationdb/tests/slow/LowLatencyWithFailures.toml

## Purpose
Tests LowLatency read behavior during controlled attrition while disabling a recovery fault-injection path that would violate latency expectations.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): Clogged. Workload entry points are `Cycle`, `LowLatency`, `Attrition`. Configuration keys include configuration=minimumReplication=2.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=1000.0, testDuration=300.0); `LowLatency`(testDuration=300.0, maxGRVLatency=50.0, testWrites=False); `Attrition`(machinesToKill=1, machinesToLeave=3, reboot=True, testDuration=300.0, waitForVersion=True, allowFaultInjection=False, killDc=False).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: Clogged: connectionFailuresDisableDuration=60.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: cc_recovery_init_req_allow_drop_in_sim=False.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/LowLatencyWithFailures.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/MoveKeysClean.toml -->
# sources/storage-engines/foundationdb/tests/slow/MoveKeysClean.toml

## Purpose
Moves keys while Sideband, light clogging, rollback, and coordinator changes run.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): MoveKeysNew. Workload entry points are `Sideband`, `RandomClogging`, `Rollback`, `RandomMoveKeys`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Sideband`(testDuration=300.0); `RandomClogging`(testDuration=300.0, scale=0.5, clogginess=0.1); `Rollback`(testDuration=300.0, meanDelay=150.0); `RandomMoveKeys`(testDuration=300.0, meanDelay=2); `ChangeConfig`(maxDelayBeforeChange=300.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: MoveKeysNew: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/MoveKeysClean.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/MoveKeysSideband.toml -->
# sources/storage-engines/foundationdb/tests/slow/MoveKeysSideband.toml

## Purpose
More aggressive sideband move-key scenario with swizzled clogging, repeated attrition, and peek tracker tuning.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): MoveKeysNew. Workload entry points are `Sideband`, `RandomClogging`, `Rollback`, `RandomMoveKeys`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Sideband`(testDuration=300.0); `RandomClogging`(testDuration=300.0, swizzle=1, scale=5.0, clogginess=0.5); `Rollback`(testDuration=300.0, meanDelay=10.0); `RandomMoveKeys`(testDuration=300.0, meanDelay=5); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=300.0); `ChangeConfig`(maxDelayBeforeChange=300.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: MoveKeysNew: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: peek_tracker_expiration_time=600.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/MoveKeysSideband.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/RyowCorrectness.toml -->
# sources/storage-engines/foundationdb/tests/slow/RyowCorrectness.toml

## Purpose
Runs read-your-own-writes correctness with randomized key/value sizes and multi-operation transactions.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): RyowCorrectnessTest. Workload entry points are `RyowCorrectness`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `RyowCorrectness`(numKeys=5000, onlyLowerCase=True, shortKeysRatio=0.5, minShortKeyLength=1, maxShortKeyLength=3, minLongKeyLength=1, maxLongKeyLength=128, minValueLength=1).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: RyowCorrectnessTest: clearAfterTest=True, timeout=2100, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/RyowCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3Client.toml -->
# sources/storage-engines/foundationdb/tests/slow/S3Client.toml

## Purpose
Validates S3ClientWorkload upload/download/delete against MockS3 with fault injection disabled and verbose blobstore logging.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): S3Client. Workload entry points are `S3ClientWorkload`. Configuration keys include buggify=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `S3ClientWorkload`(s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0').

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: S3Client: runFailureWorkloads=False.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: ; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, http_verbose_level=10, s3client_verbose_level=10, blobstore_verbose_level=10, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3Client.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3ClientWorkloadWithChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/S3ClientWorkloadWithChaos.toml

## Purpose
Runs S3ClientWorkload across stable, light, medium, and heavy MockS3 chaos rates.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): S3ClientWorkloadStable, S3ClientWorkloadLightChaos, S3ClientWorkloadMediumChaos, S3ClientWorkloadHeavyChaos. Workload entry points are `S3ClientWorkload`, `S3ClientWorkload`, `S3ClientWorkload`, `S3ClientWorkload`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.0, throttleRate=0.0, delayRate=0.0, corruptionRate=0.0, maxDelay=0.0); `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.05, throttleRate=0.02, delayRate=0.1, corruptionRate=0.01, maxDelay=1.0); `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.15, throttleRate=0.08, delayRate=0.2, corruptionRate=0.03, maxDelay=2.0); `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.3, throttleRate=0.15, delayRate=0.4, corruptionRate=0.05, maxDelay=3.0).

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: S3ClientWorkloadStable: default flags; S3ClientWorkloadLightChaos: default flags; S3ClientWorkloadMediumChaos: default flags; S3ClientWorkloadHeavyChaos: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.0, throttleRate=0.0, delayRate=0.0, corruptionRate=0.0, maxDelay=0.0; errorRate=0.05, throttleRate=0.02, delayRate=0.1, corruptionRate=0.01, maxDelay=1.0; errorRate=0.15, throttleRate=0.08, delayRate=0.2, corruptionRate=0.03, maxDelay=2.0; errorRate=0.3, throttleRate=0.15, delayRate=0.4, corruptionRate=0.05, maxDelay=3.0.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3ClientWorkloadWithChaos.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/Serializability.toml -->
# sources/storage-engines/foundationdb/tests/slow/Serializability.toml

## Purpose
Single-workload serializability simulation config.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): Serializability. Workload entry points are `Serializability`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Serializability`.

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: Serializability: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/Serializability.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedBackupCorrectness.toml -->
# sources/storage-engines/foundationdb/tests/slow/SharedBackupCorrectness.toml

## Purpose
Runs shared log-range backup-to-file restore alongside backup-to-DB without restore.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupAndRestore. Workload entry points are `Cycle`, `BackupAndRestoreCorrectness`, `BackupToDBCorrectness`. Configuration keys include configuration=extraDatabaseMode='LocalOrSingle'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=500.0, testDuration=30.0); `BackupAndRestoreCorrectness`(backupTag='backup1', backupAfter=10.0, restoreAfter=60.0, shareLogRange=True, performRestore=True, allowPauses=False); `BackupToDBCorrectness`(backupTag='backup2', backupPrefix='b1', backupAfter=15.0, restoreAfter=60.0, performRestore=False, shareLogRange=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupAndRestore: clearAfterTest=False, simBackupAgents='BackupToFileAndDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFileAndDB.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedBackupCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedBackupToDBCorrectness.toml -->
# sources/storage-engines/foundationdb/tests/slow/SharedBackupToDBCorrectness.toml

## Purpose
Runs shared log-range backup-to-file without restore alongside backup-to-DB restore.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupAndRestore. Workload entry points are `Cycle`, `BackupAndRestoreCorrectness`, `BackupToDBCorrectness`. Configuration keys include configuration=extraDatabaseMode='LocalOrSingle'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=500.0, testDuration=30.0); `BackupAndRestoreCorrectness`(backupTag='backup1', backupAfter=10.0, shareLogRange=True, performRestore=False, allowPauses=False); `BackupToDBCorrectness`(backupTag='backup2', backupPrefix='b2', backupAfter=15.0, restoreAfter=60.0, performRestore=True, shareLogRange=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupAndRestore: clearAfterTest=False, simBackupAgents='BackupToFileAndDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFileAndDB.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedBackupToDBCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedDefaultBackupCorrectness.toml -->
# sources/storage-engines/foundationdb/tests/slow/SharedDefaultBackupCorrectness.toml

## Purpose
Exercises default shared backups over file and DB backup agents in single extra database mode.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): SharedDefaultBackupToFileThenDB. Workload entry points are `Cycle`, `BackupAndRestoreCorrectness`, `BackupToDBCorrectness`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=500.0, testDuration=30.0); `BackupAndRestoreCorrectness`(backupTag='backup1', backupAfter=20.0, minBackupAfter=10.0, restoreAfter=60.0, shareLogRange=True, performRestore=True, allowPauses=False, defaultBackup=True); `BackupToDBCorrectness`(backupTag='backup2', backupAfter=20.0, minBackupAfter=10.0, restoreAfter=60.0, performRestore=False, shareLogRange=True, defaultBackup=True).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: SharedDefaultBackupToFileThenDB: clearAfterTest=False, simBackupAgents='BackupToFileAndDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFileAndDB.

## Risks
some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SharedDefaultBackupCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/StorefrontTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/StorefrontTest.toml

## Purpose
Runs a standalone Storefront workload with configured actors, item count, order size, and TPS.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): StorefrontTest. Workload entry points are `Storefront`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Storefront`(actorsPerClient=10, transactionsPerSecond=200, itemCount=10000, maxOrderSize=4).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: StorefrontTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/StorefrontTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledApiCorrectness.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledApiCorrectness.toml

## Purpose
Runs a smaller API correctness workload while swizzled clogging, rollback, attrition, and ChangeConfig run.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ApiCorrectnessTest. Workload entry points are `ApiCorrectness`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ApiCorrectness`(numKeys=2000, onlyLowerCase=True, shortKeysRatio=0.5, minShortKeyLength=1, maxShortKeyLength=3, minLongKeyLength=1, maxLongKeyLength=128, minValueLength=1); `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `ChangeConfig`(maxDelayBeforeChange=120.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: ApiCorrectnessTest: clearAfterTest=True, timeout=2100, runSetup=True.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledCycleTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledCycleTest.toml

## Purpose
Runs Cycle under swizzled clogging, repeated attrition, and coordinator reconfiguration.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): SwizzledCycleTest. Workload entry points are `Cycle`, `RandomClogging`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=5000.0, testDuration=30.0); `RandomClogging`(testDuration=30.0, swizzle=1); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=30.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=30.0); `ChangeConfig`(maxDelayBeforeChange=30.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: SwizzledCycleTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledCycleTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledDdBalance.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledDdBalance.toml

## Purpose
Runs DDBalance with background selectors and swizzled failure workloads.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DDBalance_Test. Workload entry points are `DDBalance`, `BackgroundSelector`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DDBalance`(testDuration=120.0, transactionsPerSecond=250.0, binCount=1000, writesPerTransaction=5, keySpaceDriftFactor=10, moversPerClient=10, actorsPerClient=100, nodes=100000); `BackgroundSelector`(testDuration=120.0); `RandomClogging`(testDuration=120.0, swizzle=1); `Rollback`(testDuration=120.0, meanDelay=10.0); `Attrition`(testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=120.0); `ChangeConfig`(maxDelayBeforeChange=120.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DDBalance_Test: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledDdBalance.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapse.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapse.toml

## Purpose
Long Cycle workload under swizzled clogging, rollback, attrition-to-zero, and coordinator changes.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): SwizzledRollbackTimeLapse. Workload entry points are `Cycle`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(transactionsPerSecond=500.0, testDuration=300.0, nodeCount=10000); `RandomClogging`(testDuration=300.0, swizzle=1); `Rollback`(testDuration=300.0, meanDelay=10.0); `Attrition`(testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `ChangeConfig`(maxDelayBeforeChange=300.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: SwizzledRollbackTimeLapse: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapse.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapseIncrement.toml -->
# sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapseIncrement.toml

## Purpose
Increment workload variant of SwizzledRollbackTimeLapse with expectedRate 0.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): SwizzledRollbackTimeLapse. Workload entry points are `Increment`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Attrition`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Increment`(transactionsPerSecond=100.0, testDuration=300.0, nodeCount=10000, expectedRate=0.0); `RandomClogging`(testDuration=300.0, swizzle=1); `Rollback`(testDuration=300.0, meanDelay=10.0); `Attrition`(testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `Attrition`(machinesToKill=10, machinesToLeave=0, reboot=True, testDuration=300.0); `ChangeConfig`(maxDelayBeforeChange=300.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: SwizzledRollbackTimeLapse: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/SwizzledRollbackTimeLapseIncrement.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampBackupToDB.toml -->
# sources/storage-engines/foundationdb/tests/slow/VersionStampBackupToDB.toml

## Purpose
Validates VersionStamp data with BackupToDB agents while aborting backup and killing/rebooting machines.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): VersionStampBackupToDB. Workload entry points are `VersionStamp`, `BackupToDBAbort`, `Attrition`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `VersionStamp`(failIfDataLost=False, validateExtraDB=True, testDuration=60.0); `BackupToDBAbort`(abortDelay=40.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: VersionStampBackupToDB: simBackupAgents='BackupToDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampBackupToDB.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampSwitchover.toml -->
# sources/storage-engines/foundationdb/tests/slow/VersionStampSwitchover.toml

## Purpose
Validates VersionStamp behavior across AtomicSwitchover and attrition in extra single database mode.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): VersionStampCorrectnessTest. Workload entry points are `VersionStamp`, `AtomicSwitchover`, `Attrition`. Configuration keys include configuration=extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `VersionStamp`(testDuration=60.0); `AtomicSwitchover`(switch1delay=20.0, switch2delay=20.0, stopDelay=20.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: VersionStampCorrectnessTest: clearAfterTest=False, simBackupAgents='BackupToDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/VersionStampSwitchover.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadAtomicRestore.toml -->
# sources/storage-engines/foundationdb/tests/slow/WriteDuringReadAtomicRestore.toml

## Purpose
Runs WriteDuringRead while AtomicRestore, clogging, rollback, and attrition interact with file backups.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): WriteDuringReadTest. Workload entry points are `WriteDuringRead`, `AtomicRestore`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`. Configuration keys include configuration=StderrSeverity=30.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `WriteDuringRead`(maximumTotalData=1000000, testDuration=240.0, slowModeStart=60.0, minNode=1, useSystemKeys=False); `AtomicRestore`(startAfter=10.0, restoreAfter=50.0, mutationLogType=0); `RandomClogging`(testDuration=60.0); `Rollback`(meanDelay=60.0, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: WriteDuringReadTest: clearAfterTest=False, simBackupAgents='BackupToFile'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToFile.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadAtomicRestore.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadSwitchover.toml -->
# sources/storage-engines/foundationdb/tests/slow/WriteDuringReadSwitchover.toml

## Purpose
Runs WriteDuringRead during AtomicSwitchover to BackupToDB plus failure workloads and Status.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): WriteDuringReadTest. Workload entry points are `WriteDuringRead`, `AtomicSwitchover`, `RandomClogging`, `Rollback`, `Attrition`, `Attrition`, `Status`. Configuration keys include configuration=StderrSeverity=30, extraDatabaseMode='Single'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `WriteDuringRead`(maximumTotalData=1000000, testDuration=240.0, slowModeStart=60.0, minNode=1); `AtomicSwitchover`; `RandomClogging`(testDuration=60.0); `Rollback`(meanDelay=60.0, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0); `Attrition`(machinesToKill=10, machinesToLeave=3, reboot=True, testDuration=60.0); `Status`(testDuration=60.0).

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: WriteDuringReadTest: clearAfterTest=False, simBackupAgents='BackupToDB'.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; backup agents/modes: BackupToDB.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
Status workload validates status reporting during the scenario; correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/WriteDuringReadSwitchover.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ddbalance.toml -->
# sources/storage-engines/foundationdb/tests/slow/ddbalance.toml

## Purpose
Baseline DDBalance with BackgroundSelector, swizzled RandomClogging, and coordinator ChangeConfig.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): DDBalance_Test. Workload entry points are `DDBalance`, `BackgroundSelector`, `RandomClogging`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `DDBalance`(testDuration=120.0, transactionsPerSecond=250.0, binCount=1000, writesPerTransaction=5, keySpaceDriftFactor=10, moversPerClient=10, actorsPerClient=100, nodes=100000); `BackgroundSelector`(testDuration=120.0); `RandomClogging`(testDuration=120.0, swizzle=1); `ChangeConfig`(maxDelayBeforeChange=120.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation, cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: DDBalance_Test: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ddbalance.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/invalid_proc_addresses.json -->
# sources/storage-engines/foundationdb/tests/status/invalid_proc_addresses.json

## Purpose
Golden FoundationDB status JSON fixture for the `invalid_proc_addresses` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='10.0.3.1:9191', reachable=False, address='10.0.3.1:9192', reachable=True, address='10.0.3.1:9193', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=healthy=True, name='healthy', processes=5, machines=5.
Configuration snapshot: coordinators_count=3, excluded_servers=[address='10.0.3.1:9191', address='10.0.3.1:9192', address='10.0.3.1:9193'], redundancy=factor='triple', storage_engine='memory'. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=none, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/invalid_proc_addresses.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/local_6_machine_no_replicas_remain.json -->
# sources/storage-engines/foundationdb/tests/status/local_6_machine_no_replicas_remain.json

## Purpose
Golden FoundationDB status JSON fixture for the `local_6_machine_no_replicas_remain` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `fault_tolerance`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=False, coordinators=coordinators=[address='10.0.3.1:9191', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=description='No replicas remain of some data', healthy=False, min_replicas_remaining=0, name='missing_data', processes=3, machines=3.
Configuration snapshot: coordinators_count=1, excluded_servers=[], redundancy=factor='triple', storage_engine='memory'. Fault tolerance snapshot: max_zone_failures_without_losing_availability=0, max_zone_failures_without_losing_data=0.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
fixture represents unhealthy/unavailable state and should not be normalized as success; data state carries scenario-specific health semantics

## Test Signals
Expected signals include availability=True, healthy=False, quorum_reachable=True, messages=none, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/local_6_machine_no_replicas_remain.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_1_of_3_coordinators_remain.json -->
# sources/storage-engines/foundationdb/tests/status/separate_1_of_3_coordinators_remain.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_1_of_3_coordinators_remain` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include none for controller-unreachable cases.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='10.0.3.1:9191', reachable=False, address='10.0.3.1:9192', reachable=False, address='10.0.3.1:9193', reachable=True], quorum_reachable=False, recovery_state=absent, data_state=absent, processes=0, machines=0.
Configuration snapshot: absent. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
cluster section is intentionally absent, so consumers must tolerate partial status documents; message names must remain stable: `client:quorum_not_reachable`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=False, messages=client:quorum_not_reachable, recovery=absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_1_of_3_coordinators_remain.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_2_of_3_coordinators_remain.json -->
# sources/storage-engines/foundationdb/tests/status/separate_2_of_3_coordinators_remain.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_2_of_3_coordinators_remain` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `fault_tolerance`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=True, coordinators=coordinators=[address='127.0.0.1:4701', reachable=True, address='127.0.0.1:4703', reachable=True, address='127.0.0.1:4704', reachable=False], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=healthy=True, name='healthy', processes=2, machines=1.
Configuration snapshot: coordinators_count=3, excluded_servers=[], redundancy=factor='single', storage_engine='memory'. Fault tolerance snapshot: max_zone_failures_without_losing_availability=0, max_zone_failures_without_losing_data=0.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
Primary risk is schema drift between generated status JSON and expected parser behavior.

## Test Signals
Expected signals include availability=True, healthy=True, quorum_reachable=True, messages=none, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_2_of_3_coordinators_remain.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_cannot_write_cluster_file.json -->
# sources/storage-engines/foundationdb/tests/status/separate_cannot_write_cluster_file.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_cannot_write_cluster_file` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `fault_tolerance`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=False, coordinators=coordinators=[address='127.0.0.1:4701', reachable=True, address='127.0.0.1:4703', reachable=True, address='127.0.0.1:4704', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=healthy=True, name='healthy', processes=3, machines=1.
Configuration snapshot: coordinators_count=2, excluded_servers=[], redundancy=factor='single', storage_engine='memory'. Fault tolerance snapshot: max_zone_failures_without_losing_availability=0, max_zone_failures_without_losing_data=0.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
message names must remain stable: `client:inconsistent_cluster_file`, `cluster:client_issues`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=True, healthy=False, quorum_reachable=True, messages=client:inconsistent_cluster_file, cluster:client_issues, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_cannot_write_cluster_file.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_idle.json -->
# sources/storage-engines/foundationdb/tests/status/separate_idle.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_idle` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=True, coordinators=coordinators=[address='127.0.0.1:4991', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=healthy=True, name='healthy', processes=1, machines=1.
Configuration snapshot: coordinators_count=1, excluded_servers=[], redundancy=factor='single', storage_engine='memory'. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
Primary risk is schema drift between generated status JSON and expected parser behavior.

## Test Signals
Expected signals include availability=True, healthy=True, quorum_reachable=True, messages=none, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_idle.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_initializing.json -->
# sources/storage-engines/foundationdb/tests/status/separate_initializing.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_initializing` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=True, coordinators=coordinators=[address='127.0.0.1:4991', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=description='(Re)initializing automatic data distribution.', name='initializing', processes=1, machines=1.
Configuration snapshot: coordinators_count=1, excluded_servers=[], redundancy=factor='single', storage_engine='memory'. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
data state carries scenario-specific health semantics

## Test Signals
Expected signals include availability=True, healthy=True, quorum_reachable=True, messages=none, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_initializing.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_coordinators.json -->
# sources/storage-engines/foundationdb/tests/status/separate_no_coordinators.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_no_coordinators` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include none for controller-unreachable cases.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='127.0.0.1:4991', reachable=False], quorum_reachable=False, recovery_state=absent, data_state=absent, processes=0, machines=0.
Configuration snapshot: absent. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
cluster section is intentionally absent, so consumers must tolerate partial status documents; message names must remain stable: `client:no_cluster_controller`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=False, messages=client:no_cluster_controller, recovery=absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_coordinators.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_database.json -->
# sources/storage-engines/foundationdb/tests/status/separate_no_database.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_no_database` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `fault_tolerance`, `machines`, `messages`, `processes`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='127.0.0.1:4701', reachable=True, address='127.0.0.1:4703', reachable=True, address='127.0.0.1:4704', reachable=True], quorum_reachable=True, recovery_state=description='The coordinator(s) have no record of this database. Either the coordinator addresses are incorrect, the coordination state on those machines is missing, or no database has been created.', name='configuration_never_created', data_state=absent, processes=3, machines=1.
Configuration snapshot: coordinators_count=3, excluded_servers=[]. Fault tolerance snapshot: max_zone_failures_without_losing_availability=0, max_zone_failures_without_losing_data=0.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
message names must remain stable: `cluster:unreadable_configuration`, `cluster:transaction_start_timeout`, `cluster:commit_timeout`, `cluster:status_incomplete`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=cluster:unreadable_configuration, cluster:transaction_start_timeout, cluster:commit_timeout, cluster:status_incomplete, recovery=configuration_never_created.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_database.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_servers.json -->
# sources/storage-engines/foundationdb/tests/status/separate_no_servers.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_no_servers` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include none for controller-unreachable cases.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='127.0.0.1:4991', reachable=True], quorum_reachable=True, recovery_state=absent, data_state=absent, processes=0, machines=0.
Configuration snapshot: absent. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
cluster section is intentionally absent, so consumers must tolerate partial status documents; message names must remain stable: `client:no_cluster_controller`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=client:no_cluster_controller, recovery=absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_servers.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_not_enough_servers.json -->
# sources/storage-engines/foundationdb/tests/status/separate_not_enough_servers.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_not_enough_servers` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='127.0.0.1:4991', reachable=True], quorum_reachable=True, recovery_state=description='Recruiting new transaction servers.', name='recruiting_transaction_servers', required_logs=3, required_commit_proxies=1, required_grv_proxies=1, required_resolvers=1, data_state=healthy=True, name='healthy', processes=1, machines=1.
Configuration snapshot: coordinators_count=1, excluded_servers=[]. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
message names must remain stable: `cluster:unreadable_configuration`, `cluster:transaction_start_timeout`, `cluster:commit_timeout`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=cluster:unreadable_configuration, cluster:transaction_start_timeout, cluster:commit_timeout, recovery=recruiting_transaction_servers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_not_enough_servers.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/single_process_too_many_config_params.json -->
# sources/storage-engines/foundationdb/tests/status/single_process_too_many_config_params.json

## Purpose
Golden FoundationDB status JSON fixture for the `single_process_too_many_config_params` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='10.0.3.1:9191', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=healthy=True, name='healthy', processes=1, machines=1.
Configuration snapshot: coordinators_count=1, excluded_servers=[]. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
message names must remain stable: `cluster:status_incomplete`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=cluster:status_incomplete, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/single_process_too_many_config_params.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/versions.target.cmake -->
# sources/storage-engines/foundationdb/versions.target.cmake

## Purpose
CMake fragment listing FoundationDB restart/upgrade target versions used by build or test orchestration.

## Important APIs, Types, And Functions
Defines `FDB_RESTARTER_VERSION_LIST` with values parsed from `set(...)`: <?xml version="1.0"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <Version>${FDB_VERSION}</Version>
    <PackageName>${FDB_MAJOR}.${FDB_MINOR}</PackageName>
  </PropertyGroup>
</Project>.

## Control Flow
No runtime control flow. CMake evaluates this file and exposes the version list to callers that generate restart/upgrade tests or targets.

## State And Persistence Behavior
No persistent state beyond the configured CMake variable in the build directory.

## Dependencies And Integration Points
Integrated with FoundationDB CMake logic that consumes restart target versions, especially upgrade/restarting test generation.

## Risks
The version list must stay aligned with available restart fixtures and supported upgrade paths; stale values can generate missing or irrelevant test targets.

## Test Signals
CMake configure/generation and restart test target discovery are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/versions.target.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/.github/workflows/build.yml -->
# sources/storage-engines/leveldb/.github/workflows/build.yml

## Purpose
GitHub Actions CI matrix for LevelDB across Linux/macOS/Windows, clang/gcc/msvc, and Debug/RelWithDebInfo builds.

## Important APIs, Types, And Functions
Workflow keys include `on: [push, pull_request]`, read-only contents permission, one `build-and-test` job, matrix `compiler`, `os`, and `optimized`, and environment variables for CMake build type/path and executable suffix.

## Control Flow
Checkout submodules, install Linux dependencies, configure CMake with an install prefix, build, run `ctest`, run LevelDB benchmarks, conditionally run SQLite/Kyoto Cabinet benchmarks, then test the install target.

## State And Persistence Behavior
Persists only CI build artifacts in `${{ github.workspace }}/build` and an install test prefix under `${{ runner.temp }}`. Matrix exclusions encode platform/compiler support.

## Dependencies And Integration Points
Depends on GitHub Actions hosted runners, CMake, submodules, libkyotocabinet-dev, libsnappy-dev, and libsqlite3-dev on Linux. Directly validates `CMakeLists.txt`, benchmark targets, unit tests, and install/package rules used by downstream consumers.

## Risks
Actions use `checkout@v2`; Linux package availability can affect Kyoto/SQLite benchmark coverage; Windows skips SQLite and Kyoto Cabinet benchmarks.

## Test Signals
The workflow itself is the test signal: `ctest --verbose`, `db_bench`, `db_bench_sqlite3` off Windows, `db_bench_tree_db` on Linux clang, and install target build.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/.github/workflows/build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/CMakeLists.txt -->
# sources/storage-engines/leveldb/CMakeLists.txt

## Purpose
Top-level CMake build definition for LevelDB 1.23.0, covering library, utility, tests, benchmarks, feature detection, optional third-party links, and install exports.

## Important APIs, Types, And Functions
Defines options `LEVELDB_BUILD_TESTS`, `LEVELDB_BUILD_BENCHMARKS`, `LEVELDB_INSTALL`; target `leveldb`; executable `leveldbutil`; helper functions `leveldb_test()` and `leveldb_benchmark()`; exported package namespace `leveldb::`.

## Control Flow
Sets C/C++ standards, detects platform/features/libraries, configures `port_config.h`, builds core sources and public headers into `leveldb`, conditionally adds platform env implementation, links optional crc32c/snappy/zstd/tcmalloc, adds tests/benchmarks, and installs targets plus CMake package files.

## State And Persistence Behavior
Build state is generated into `${PROJECT_BINARY_DIR}` including configured headers and package config files. Install state copies public headers and target exports to GNU install dirs.

## Dependencies And Integration Points
Uses CMake modules for include/library/symbol/compiler checks, Threads, googletest, google benchmark, optional sqlite3 and kyotocabinet, plus project source trees under db/table/util/helpers. Central integration point for all LevelDB C++ and C APIs, tests, benchmarks, CI workflow, and downstream `find_package(leveldb)` usage.

## Risks
Build behavior changes with detected optional libraries; shared builds hide symbols except exported API; some tests/benchmarks are skipped in shared builds or without optional dependencies.

## Test Signals
Adds aggregate `leveldb_tests`, C API test, platform env tests, and benchmark executables when enabled. CI runs these through CTest and benchmark steps.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench.cc -->
# sources/storage-engines/leveldb/benchmarks/db_bench.cc

## Purpose
Primary LevelDB microbenchmark executable for writes, reads, deletes, seeks, compaction, compression, CRC, stats, heap profile, threading, cache/filter/options variants.

## Important APIs, Types, And Functions
Global `FLAGS_*` tune operation list, record counts, threads, value size, cache, Bloom bits, compression, DB path, etc.; helper classes `CountComparator`, `RandomGenerator`, `KeyBuffer`, `Stats`; shared structs `SharedState`, `ThreadState`; class `Benchmark` with methods for each operation.

## Control Flow
`main()` parses flags and chooses a temp DB. `Benchmark::Run()` opens the DB, tokenizes `FLAGS_benchmarks`, maps names to member functions, resets per-run options, optionally recreates fresh DBs, and calls `RunBenchmark()` which starts synchronized threads and merges stats.

## State And Persistence Behavior
Creates/removes a LevelDB database under `FLAGS_db`, heap profile files, optional cache/filter policy objects, and per-thread deterministic random state. Fresh write benchmarks destroy/reopen the DB unless `--use_existing_db` is set.

## Dependencies And Integration Points
Depends on LevelDB DB/Env/Cache/Comparator/FilterPolicy/WriteBatch APIs, `port` compression helpers, crc32c, histogram, random/test utilities, and POSIX `/proc/cpuinfo` on Linux. Built by `leveldb_benchmark()` in CMake and run in CI. Exercises public APIs and internal performance properties such as comparator count and DB properties `leveldb.stats`/`leveldb.sstables`.

## Risks
Benchmark exits process on DB errors; random overwrite/read workloads may report misses depending on prior benchmark sequence; duplicate `readrandomsmall` branch is harmless but suspicious; results depend heavily on optional compression libraries and build flags.

## Test Signals
Produces throughput, micros/op, optional histograms, comparison counts, and explicit errors on failed DB operations. CI runs default benchmark sequence.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_log.cc -->
# sources/storage-engines/leveldb/benchmarks/db_bench_log.cc

## Purpose
Google Benchmark fixture for measuring `VersionSet::LogAndApply()` manifest update cost as base file count grows.

## Important APIs, Types, And Functions
Defines `MakeKey()`, benchmark function `BM_LogAndApply(benchmark::State&)`, and registers args 1, 100, 10000, 100000 with `BENCHMARK_MAIN()`.

## Control Flow
Creates a temp DB, opens/closes it to initialize metadata, recovers a `VersionSet`, seeds level-2 files with a `VersionEdit`, then in each benchmark iteration removes/adds a file and calls `LogAndApply()` under a mutex.

## State And Persistence Behavior
Persists a temporary LevelDB database and MANIFEST state, mutating `VersionSet` metadata with monotonically increasing file numbers.

## Dependencies And Integration Points
Uses google benchmark, gtest assertions, `VersionSet`, `VersionEdit`, `InternalKeyComparator`, `Env`, `DB`, mutex helpers, and test utilities. Targets internal version metadata scaling, complementing public `db_bench` by focusing on MANIFEST edit application.

## Risks
Manual timing is printed to stderr in addition to benchmark framework metrics; failed `LogAndApply()` inside the loop is not asserted in the hot path.

## Test Signals
Benchmark arguments provide scaling signals for manifest application with small to very large existing file counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_log.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_sqlite3.cc -->
# sources/storage-engines/leveldb/benchmarks/db_bench_sqlite3.cc

## Purpose
SQLite benchmark executable that mirrors LevelDB benchmark workloads for comparative key/value performance.

## Important APIs, Types, And Functions
Global `FLAGS_*` cover benchmark list, num/reads/value size, histogram, compression ratio for value generation, page/cache settings, existing DB, rowids, transaction, WAL, and DB path. Class `Benchmark` implements open, write, random/sequential read, and reporting.

## Control Flow
`main()` parses flags. `Benchmark::Run()` opens SQLite, tokenizes benchmark names, runs fresh/existing write or read operations, checkpointing WAL after writes. `Write()` prepares REPLACE and optional transaction statements; `Read()` prepares keyed SELECTs; `ReadSequential()` scans ordered keys.

## State And Persistence Behavior
Creates `dbbench_sqlite3-*.db` files in the LevelDB test directory, deletes old files unless reusing, manages SQLite connection and prepared statements, WAL checkpoints, cache/page PRAGMAs, and histogram counters.

## Dependencies And Integration Points
Requires sqlite3 plus LevelDB utility classes for `Env`, `Slice`, `Histogram`, `Random`, and test data generation. Optional CMake benchmark target linked to sqlite3 and run by CI on non-Windows runners for comparative performance baselines.

## Risks
Error handlers exit the process; destructor always closes `db_`; fresh benchmarks reopen DBs and skip when `--use_existing_db` conflicts; SQL statements use blob keys and optional WITHOUT ROWID, so results differ from LevelDB beyond storage engine alone.

## Test Signals
Outputs micros/op, MB/s, optional histograms, and hard exits on SQLite prepare/step/finalize failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_sqlite3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_tree_db.cc -->
# sources/storage-engines/leveldb/benchmarks/db_bench_tree_db.cc

## Purpose
Kyoto Cabinet TreeDB benchmark executable mirroring LevelDB benchmark workloads for another comparative backend.

## Important APIs, Types, And Functions
Global flags cover benchmark list, num/reads/value size, compression ratio, histogram, cache/page size, existing DB, compression, and DB path. Class `Benchmark` implements TreeDB open/write/read/reporting.

## Control Flow
`main()` parses flags. `Benchmark::Run()` opens TreeDB, tokenizes operations, dispatches write/read variants, and calls `DBSynchronize()` after writes. Fresh writes delete/reopen with tuning options before timing.

## State And Persistence Behavior
Creates `dbbench_polyDB-*.kct` files, removes old ones unless reusing, configures TreeDB page cache/page/map/compression, and maintains deterministic random/value generator state.

## Dependencies And Integration Points
Requires Kyoto Cabinet `kcpolydb.h`, LZO compressor types, and LevelDB utility classes for environment, Slice, Histogram, Random, and test data. Optional CMake benchmark target detected via C++ compile check and run by CI on Linux clang when kyotocabinet is installed.

## Risks
Open/set/close errors are printed but many do not abort; `db_num_` must advance correctly to avoid file reuse; benchmark comparability is affected by Kyoto tuning and compression choices.

## Test Signals
Produces comparative micros/op/MB/s/histogram output and exercises sequential/random/sync/100K workload variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/benchmarks/db_bench_tree_db.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/cmake/leveldbConfig.cmake.in -->
# sources/storage-engines/leveldb/cmake/leveldbConfig.cmake.in

## Purpose
CMake package config template installed for downstream `find_package(leveldb)` consumers.

## Important APIs, Types, And Functions
Uses `@PACKAGE_INIT@`, `include(CMakeFindDependencyMacro)`, `find_dependency(Threads)`, and includes installed `leveldbTargets.cmake` if `leveldb::leveldb` is not already defined.

## Control Flow
Configured by `configure_package_config_file()` during install, then loaded by consumers to restore dependencies and imported targets.

## State And Persistence Behavior
No runtime state; installed file resolves `${CMAKE_CURRENT_LIST_DIR}/leveldbTargets.cmake` at package load time.

## Dependencies And Integration Points
Depends on CMake package config helpers and Threads dependency because the exported LevelDB target links `Threads::Threads`. Completes the install/export path defined in `CMakeLists.txt`.

## Risks
Only declares Threads as a package dependency; optional libraries are linked into the exported target but not explicitly found here.

## Test Signals
CI install target build checks that this template configures and installs.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/cmake/leveldbConfig.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/autocompact_test.cc -->
# sources/storage-engines/leveldb/db/autocompact_test.cc

## Purpose
GoogleTest coverage for automatic compaction triggered by reads over deleted data ranges.

## Important APIs, Types, And Functions
Fixture `AutoCompactTest` owns DB path, tiny LRU cache, Options, and DB pointer; helpers `Key()`, `Size()`, and `DoReads(int)`; tests `ReadAll` and `ReadHalf`.

## Control Flow
Constructor opens a no-compression DB with a 100-byte cache. `DoReads()` writes ~100 MB of 200 KB values, compacts memtable, deletes all keys, compacts again, records approximate sizes, repeatedly scans the target key range until size drops by 10x, then verifies untouched range size remains close.

## State And Persistence Behavior
Creates/destroys a temp DB named `autocompact_test`; mutates on-disk tables and tombstones; uses `DBImpl::TEST_CompactMemTable()` for internal flushing.

## Dependencies And Integration Points
Depends on gtest, `DBImpl`, public DB/cache APIs, and test macros/utilities. Included in `leveldb_tests` for non-shared builds, validating interaction between reads, cache pressure, approximate sizes, and compaction scheduling.

## Risks
Uses sleep/poll loop up to 100 seconds, so slow or overloaded environments can be flaky; relies on internal DBImpl casting and approximate size heuristics.

## Test Signals
`ReadAll` and `ReadHalf` confirm read-triggered compaction reduces touched range while leaving other range approximately unchanged.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/autocompact_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.cc -->
# sources/storage-engines/leveldb/db/builder.cc

## Purpose
Implements `BuildTable()`, the compaction/flush helper that writes an iterator stream into one sorted table file and fills `FileMetaData`.

## Important APIs, Types, And Functions
Function `Status BuildTable(const std::string& dbname, Env* env, const Options& options, TableCache* table_cache, Iterator* iter, FileMetaData* meta)`.

## Control Flow
Initializes `meta->file_size` to zero, seeks iterator to first, creates `TableFileName(dbname, meta->number)` only when data exists, writes all key/value pairs through `TableBuilder`, records smallest/largest internal keys, finishes/syncs/closes file, verifies by opening through `TableCache`, checks iterator status, and removes the file on any failure or empty input.

## State And Persistence Behavior
Creates, syncs, closes, verifies, and possibly deletes an `.ldb` table file. Mutates `FileMetaData` fields `file_size`, `smallest`, and `largest`.

## Dependencies And Integration Points
Depends on internal `dbformat`, `filename`, `table_cache`, `version_edit`, public `Env`, `Iterator`, and `TableBuilder` via LevelDB DB includes. Called by DB implementation compaction/flush paths to materialize SSTables and feed metadata into version edits.

## Risks
Input iterator keys must be ordered and encoded as internal keys; file cleanup depends on `Env::RemoveFile`; verification only checks iterator status from table cache, not a full scan.

## Test Signals
Covered indirectly by DB, recovery, corruption, table, compaction, and builder-driven flush/compaction tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.h -->
# sources/storage-engines/leveldb/db/builder.h

## Purpose
Declares the internal table-building helper used by LevelDB DB implementation.

## Important APIs, Types, And Functions
Forward declares `Options`, `FileMetaData`, `Env`, `Iterator`, `TableCache`, `VersionEdit`; declares `BuildTable()` returning `Status`.

## Control Flow
Header-only contract: callers pass database name, environment, options, table cache, positioned/owned iterator, and metadata structure whose number identifies the output file.

## State And Persistence Behavior
Specifies that successful non-empty builds fill the rest of `FileMetaData`; empty iterators set file size to zero and produce no table file.

## Dependencies And Integration Points
Depends only on `leveldb/status.h` plus forward declarations to keep compile dependencies small. Included by `builder.cc` and DB implementation code that needs to emit table files during flush/compaction.

## Risks
Internal API assumes caller owns object lifetimes and provides a valid `meta->number`; misuse can delete or overwrite unintended table file names.

## Test Signals
Behavior validated through `builder.cc` call sites and DB/table tests rather than direct header tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/c.cc -->
# sources/storage-engines/leveldb/db/c.cc

## Purpose
C API implementation wrapping LevelDB C++ DB, options, iterators, write batches, snapshots, comparators, filter policies, cache, environment, and version helpers.

## Important APIs, Types, And Functions
Defines opaque structs from `leveldb/c.h`; exported functions include `leveldb_open/close`, `put/delete/write/get`, iterator navigation/access/error, snapshots, property/size/compact/destroy/repair, write batch operations, option setters, comparator/filter policy creation, Bloom filter wrapper, read/write option setters, LRU cache, default env, test directory, `leveldb_free`, and version functions.

## Control Flow
Most calls translate C pointer+length inputs into `Slice`, call the C++ API, and convert `Status` to `char** errptr` via `SaveError()`. Returned strings are heap-allocated copies for caller ownership. Custom comparator/filter structs subclass C++ virtual interfaces and dispatch to C callbacks.

## State And Persistence Behavior
Owns heap wrappers around C++ objects; DB operations mutate persistent LevelDB state; snapshots pin versions until release; write batches accumulate mutations in memory; cache/env wrappers control ownership flags.

## Dependencies And Integration Points
Depends on public LevelDB headers and C runtime allocation/string functions. Bridges to C++ APIs `DB`, `Options`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `Iterator`, `Snapshot`, `Cache`, `Env`, `FilterPolicy`, and `Comparator`. Implements the stable C ABI consumed by non-C++ bindings and `db/c_test.c`; compiled into the main LevelDB library by CMake.

## Risks
Caller must free returned buffers with `leveldb_free`; iter key/value pointers are valid only while iterator state remains; custom callback lifetimes must outlive wrappers; `CopyString()` allocates exactly value length without null terminator by design for binary values.

## Test Signals
CMake builds `db/c_test.c`; broader coverage comes from language bindings and C API consumers exercising error propagation and object lifetimes.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/c.cc -->
