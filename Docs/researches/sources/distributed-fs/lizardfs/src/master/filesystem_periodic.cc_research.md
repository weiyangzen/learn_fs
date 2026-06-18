# sources/distributed-fs/lizardfs/src/master/filesystem_periodic.cc

## Purpose
`filesystem_periodic.cc` implements event-loop maintenance work for the master filesystem: async task processing, background checksum recalculation, file/chunk health scanning, defective-node reporting, trash expiry, and periodic configuration.

## Important APIs and control flow
`fs_background_task_manager_work` processes queued metadata tasks in batches and makes the next poll nonblocking while work remains. `fs_background_checksum_recalculation_a_bit` advances `gChecksumBackgroundUpdater` through nodes, xattrs, chunks, and done states, calling node/xattr/chunk checksum functions and broadcasting completion. File test logic uses `fs_periodic_file_test` and `fs_background_file_test` to scan node hash buckets over a configured loop time, count files/chunks/under-goal/missing/unavailable states, and maintain `gDefectiveNodes`. `fs_test_getdata` returns the last scan counters and a capped textual error report. `fs_get_defective_nodes_info` pages through defective nodes with requested error flags. Trash maintenance uses `fs_periodic_emptytrash`, `fs_do_emptytrash`, and deprecated apply helpers to purge expired trash entries.

## State and persistence behavior
Static counters store the last completed scan and current scan accumulators. `gFileTestLoopIndex` and `gFileTestLoopBucketLimit` implement incremental scanning with watchdog-limited slices. `gDefectiveNodes` stores inode to error-flag mappings, capped at one million entries. Empty-trash operations mutate metadata, call `fsnodes_purge`, and emit `PURGE` changelog entries in master mode; deprecated apply variants verify historical free/reserved counts.

## Dependencies and integration points
The file depends on config, event loop, loop watchdogs, checksum/xattr/chunk recalculation, node helpers, metadata globals, task manager, client broadcasts, chunk health APIs, and changelog emission. `fs_periodic_master_init` registers timers and each-loop callbacks.

## Risks and test signals
The periodic code must avoid blocking the event loop while still converging. Risks include defective-node map staleness, watchdog bucket adjustment errors, checksum recalculation never reaching done, and trash iteration invalidation after purges. Tests should simulate large node hash scans, unavailable/missing chunks, structure errors in parent vectors, expired trash with and without open sessions, task-manager backlog, checksum background completion broadcast, and config bounds for `FILE_TEST_LOOP_MIN_TIME`.
