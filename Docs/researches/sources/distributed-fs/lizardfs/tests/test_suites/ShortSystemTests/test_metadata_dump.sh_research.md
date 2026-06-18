<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_dump.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_dump.sh

Purpose: exercises foreground and background metadata dumping, metarestore handoff, checksum failure fallback, backup retention, and dump freshness across many metadata mutations.

Important APIs, functions, and commands: defines `check_backup_copies`, `check`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_first_chunkserver_with_chunks_matching`, `mfsmetarestore`, `mfsmetadump`, `file-generate`, `truncate`, `dd`, `attr`, `setfattr`, ...; drives configuration through `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, `NR`, `FILE_SIZE`, ....

Control flow: The script proceeds through these visible steps: `master_extra_config="MFSMETARESTORE_PATH = $TEMP_DIR/metarestore.sh"`; `master_extra_config+="|MAGIC_PREFER_BACKGROUND_DUMP = 1"`; `master_extra_config+="|BACK_META_KEEP_PREVIOUS = 5"`; `MASTER_EXTRA_CONFIG=$master_extra_config \`; `setup_local_empty_lizardfs info`; `mfsmetarestore "\$@" | tee $TEMP_DIR/metaout_tmp`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, active/pending file-lock records, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, `setfattr`, `setfacl`, `tee`, environment/config variables such as `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; background jobs require reliable cleanup and freeze signaling; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, soft expectation accumulation, restore exit status, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_dump.sh -->
