# Research: subset-b-007637

Grouped research report for 122 LizardFS short-system tests, test templates, shared test utilities, and two utility build/assertion files. Each section preserves the source path and is split into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms_with_endangered_chunks_priority.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms_with_endangered_chunks_priority.sh

Purpose: verifies that endangered-chunk read priority keeps files readable when two of three labeled server rooms are stopped under a custom three-server-room goal.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `file-generate`, `file-validate`, `assert_success`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `ENDANGERED_CHUNKS_PRIORITY`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `lizardfs setgoal three_serverrooms "${info[mount0]}/dir"`; `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`; `assert_success lizardfs_chunkserver_daemon "$csid" stop &`; `assert_success file-validate "${info[mount0]}/dir/file_"*`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `ENDANGERED_CHUNKS_PRIORITY`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms_with_endangered_chunks_priority.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mapall.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mapall.sh

Purpose: checks export-side mapall UID/GID remapping across normal and mapall mounts, including metadata-generator output and noowner exceptions.

Important APIs, functions, and commands: defines `stat_ug`; uses `setup_local_empty_lizardfs`, `metadata_get_all_generators`, `expect_equals`, `lizardfs {geteattr}`; drives configuration through `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_EXPORTS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_equals 'lizardfstest:lizardfstest' $(stat_ug "$normal/normal")`; `expect_equals 'lizardfstest_6:lizardfstest_4' $(stat_ug "$normal/mapall")`; `expect_equals 'root:root' $(stat_ug "$mapall/normal")`; `expect_equals 'lizardfstest:lizardfstest' $(stat_ug "$mapall/mapall")`; `rm "$normal/normal"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_EXPORTS`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mapall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_noatime.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_noatime.sh

Purpose: checks that master ACCESS changelog entries are produced for reads by default and stop after NO_ATIME is enabled through a live reload.

Important APIs, functions, and commands: defines `count_accesses`; uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `assert_equals`; drives configuration through `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `MOUNT_EXTRA_CONFIG`, `NO_ATIME`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `grep -c -w ACCESS "${info[master_data_path]}"/changelog.mfs || true`; `assert_equals $((2 * i)) $(count_accesses)`; `echo "NO_ATIME = 1" >> "${info[master_cfg]}"`; `lizardfs_master_daemon reload`; `assert_eventually_matches main.reload 'cat "${TEMP_DIR}/reloads"'`.

State and persistence behavior: State and persistence under test include client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `MOUNT_EXTRA_CONFIG`, `NO_ATIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_noatime.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_stop_during_dumping.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_stop_during_dumping.sh

Purpose: ensures the master can stop cleanly while an asynchronous background metadata dump is blocked inside the configured metarestore wrapper.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_daemon`, `mfsmetarestore`, `assert_success`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mfsmetarestore "\$@"`; `assert_success lizardfs_admin_master save-metadata --async`; `assert_eventually 'test -e $TEMP_DIR/dump_started'`; `lizardfs_master_daemon stop`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_stop_during_dumping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_checksum_recalculation.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_checksum_recalculation.sh

Purpose: stress-tests metadata checksum recalculation while nodes, xattrs, chunks, and goals are being mutated concurrently.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `truncate`, `attr`, `assert_success`, `expect_eventually_prints`, `expect_awk_finds`, `lizardfs {setgoal}`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `METADATA_CHECKSUM_RECALCULATION_SPEED`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `DEBUG_LOG_FAIL_ON`.

Control flow: The script proceeds through these visible steps: `assert_program_installed attr`; `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|METADATA_CHECKSUM_RECALCULATION_SPEED = 1"`; `master_cfg+="|MAGIC_DEBUG_LOG = $TEMP_DIR/log|LOG_FLUSH_ON=DEBUG"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_FAIL_ON="master.fs.checksum.mismatch" \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, extended attributes, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `METADATA_CHECKSUM_RECALCULATION_SPEED`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `CHUNKSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; background jobs require reliable cleanup and freeze signaling; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_checksum_recalculation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_dump.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_dump.sh

Purpose: exercises foreground and background metadata dumping, metarestore handoff, checksum failure fallback, backup retention, and dump freshness across many metadata mutations.

Important APIs, functions, and commands: defines `check_backup_copies`, `check`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_first_chunkserver_with_chunks_matching`, `mfsmetarestore`, `mfsmetadump`, `file-generate`, `truncate`, `dd`, `attr`, `setfattr`, ...; drives configuration through `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, `NR`, `FILE_SIZE`, ....

Control flow: The script proceeds through these visible steps: `master_extra_config="MFSMETARESTORE_PATH = $TEMP_DIR/metarestore.sh"`; `master_extra_config+="|MAGIC_PREFER_BACKGROUND_DUMP = 1"`; `master_extra_config+="|BACK_META_KEEP_PREVIOUS = 5"`; `MASTER_EXTRA_CONFIG=$master_extra_config \`; `setup_local_empty_lizardfs info`; `mfsmetarestore "\$@" | tee $TEMP_DIR/metaout_tmp`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, active/pending file-lock records, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, `setfattr`, `setfacl`, `tee`, environment/config variables such as `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; background jobs require reliable cleanup and freeze signaling; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, soft expectation accumulation, restore exit status, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_dump.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_file_lock.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_file_lock.sh

Purpose: validates that metadata files are locked so live masters block unsafe metarestore and conflicting shadow startup, while stopped daemons allow recovery.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `mfsmetarestore`, `assert_success`, `assert_failure`; drives configuration through `USE_RAMDISK`, `MASTERSERVERS`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_failure mfsmetarestore -a -d "${info[master_data_path]}"`; `assert_success lizardfs_master_daemon kill`; `assert_success mfsmetarestore -a -d "${info[master_data_path]}"`; `assert_success lizardfs_master_daemon start`; `assert_success lizardfs_master_n 1 stop`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MASTERSERVERS`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_file_lock.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_polonaise.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_polonaise.sh

Purpose: compares metadata exposed by lizardfs-polonaise-server with native metadata printing to catch conversion or serving mismatches.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs-polonaise-server`, `metadata_print`, `metadata_get_all_generators`, `metadata_validate_files`, `assert_eventually`, `lizardfs {dirinfo}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MESSAGE`, `DISABLE_PRINTING_XATTRS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs-polonaise-server --master-host=localhost \`; `--master-port=${info[matocl]} \`; `mkdir -p "$mnt"`; `MESSAGE="Client is not available" assert_eventually 'lizardfs dirinfo "$mnt"'`; `for generator in $(metadata_get_all_generators | egrep -v "acl|xattr|trash"); do`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, extended attributes, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MESSAGE`, `DISABLE_PRINTING_XATTRS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_polonaise.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_recovery.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_recovery.sh

Purpose: kills the master after broad metadata generation, reconstructs metadata from changelogs with mfsmetarestore, and verifies printed metadata and file contents survive.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_daemon`, `lizardfs_metalogger_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `mfsmetarestore`, `metadata_print`, `metadata_generate_all`, `metadata_validate_files`, `assert_success`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `EMPTY_TRASH_PERIOD`, `EMPTY_RESERVED_INODES_PERIOD`, `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|AUTO_RECOVERY = 1"`; `master_cfg+="|EMPTY_TRASH_PERIOD = 1"`; `master_cfg+="|EMPTY_RESERVED_INODES_PERIOD = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_FAIL_ON="master.fs.checksum.mismatch" \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `EMPTY_TRASH_PERIOD`, `EMPTY_RESERVED_INODES_PERIOD`, `CHUNKSERVERS`, `MOUNTS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, metadata diff checks, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_recovery.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_save_request_min_period.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_save_request_min_period.sh

Purpose: checks shadow synchronization behavior when master save requests are throttled by METADATA_SAVE_REQUEST_MIN_PERIOD and mismatch logs should be delayed or immediate.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `truncate`, `assert_failure`, `assert_eventually`, `assert_awk_finds`, `assert_awk_finds_no`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `METADATA_SAVE_REQUEST_MIN_PERIOD`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `DEBUG_LOG_DISABLE_FAIL_ON`.

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|MAGIC_DEBUG_LOG = ${TEMP_DIR}/log|LOG_FLUSH_ON=DEBUG"`; `master_cfg+="|METADATA_SAVE_REQUEST_MIN_PERIOD = $(timeout_rescale_seconds 10)"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_DISABLE_FAIL_ON="master.mismatch" \`; `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `METADATA_SAVE_REQUEST_MIN_PERIOD`, `CHUNKSERVERS`, `MASTERSERVERS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_save_request_min_period.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_autorecovery_metadata_version.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_autorecovery_metadata_version.sh

Purpose: verifies auto-recovery preserves or reconstructs the on-disk metadata version after normal save, changelog-only recovery, and deleted metadata cases.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_probe_master`, `lizardfs_master_daemon`, `mfsmetarestore`, `file-generate`, `assert_success`, `assert_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `BACK_META_KEEP_PREVIOUS`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `changelog_file="${info[master_data_path]}/changelog.mfs"`; `FILE_SIZE=1K assert_success file-generate "${info[mount0]}"/file_${i}_{1..10}`; `assert_success lizardfs_admin_master save-metadata`; `latest_metadata_version=$(lizardfs_probe_master metadataserver-status | cut -f3)`; `on_disk_metadata_version=$(mfsmetarestore -g -d "${info[master_data_path]}")`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `BACK_META_KEEP_PREVIOUS`, `FILE_SIZE`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_autorecovery_metadata_version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_disable_metadata_checksum_verification.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_disable_metadata_checksum_verification.sh

Purpose: corrupts the metadata checksum and proves mfsmetarestore fails normally but succeeds when checksum verification is explicitly disabled.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `mfsmetarestore`, `assert_success`, `assert_failure`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `METADATA_CHECKSUM_FREQUENCY`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `changelog_file="${info[master_data_path]}/changelog.mfs"`; `lizardfs_master_daemon kill`; `assert_failure mfsmetarestore -a -d "${info[master_data_path]}"`; `assert_success mfsmetarestore -z -a -d "${info[master_data_path]}"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `METADATA_CHECKSUM_FREQUENCY`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_disable_metadata_checksum_verification.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mfsmakesnapshot.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mfsmakesnapshot.sh

Purpose: covers snapshot creation and overwrite semantics for files and directories, including goals, trailing slashes, shared chunks, and recursive goal inheritance.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_all_chunks`, `assert_success`, `expect_equals`, `assert_equals`, `assert_eventually_prints`, `lizardfs {fileinfo, getgoal, makesnapshot, setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir1`; `lizardfs setgoal $i dir1/file$i`; `assert_equals 5 $(find_all_chunks | wc -l) # First file has 2 chunks, the second one -- 3`; `assert_success lizardfs makesnapshot dir1 dir2`; `expect_equals "$(ls dir1 | sort)" "$(ls dir2 | sort)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mfsmakesnapshot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_migrating_between_labels.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_migrating_between_labels.sh

Purpose: checks chunk migration between labeled hdd/flop/ssd chunkserver groups after changing goals and restarting previously stopped servers.

Important APIs, functions, and commands: defines `count_chunks_on_chunkservers`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_all_chunks`, `find_chunkserver_chunks`, `file-generate`, `assert_eventually_prints`, `expect_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `CHUNKS_SOFT_DEL_LIMIT`, `CHUNKS_WRITE_REP_LIMIT`, `OPERATIONS_DELAY_INIT`, ....

Control flow: The script proceeds through these visible steps: `count_chunks_on_chunkservers() {`; `find_chunkserver_chunks $i`; `setup_local_empty_lizardfs info`; `lizardfs_chunkserver_daemon $i stop &`; `lizardfs_wait_for_ready_chunkservers 3`; `mkdir dir`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_migrating_between_labels.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_ec_write.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_ec_write.sh

Purpose: writes and overwrites a file while progressively stopping erasure-code data/parity chunkservers to validate EC write availability and failure boundaries.

Important APIs, functions, and commands: defines `for_chunkservers`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_first_chunkserver_with_chunks_matching`, `file-overwrite`, `file-validate`, `dd`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `REPLICATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`, `DISABLE_CHUNKS_DEL`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, ....

Control flow: The script proceeds through these visible steps: `for_chunkservers() {`; `lizardfs_chunkserver_daemon $csid "${operation}" &`; `nr_of_running_chunkservers=$((nr_of_running_chunkservers - $#))`; `nr_of_running_chunkservers=$((nr_of_running_chunkservers + $#))`; `lizardfs_wait_for_ready_chunkservers $nr_of_running_chunkservers`; `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `REPLICATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_ec_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_xor_write.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_xor_write.sh

Purpose: writes and overwrites a file while stopping XOR-goal chunkservers to validate XOR write availability and failure boundaries.

Important APIs, functions, and commands: defines `for_chunkservers`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_first_chunkserver_with_chunks_matching`, `file-overwrite`, `file-validate`, `dd`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`, `DISABLE_CHUNKS_DEL`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `for_chunkservers() {`; `lizardfs_chunkserver_daemon $csid "${operation}" &`; `nr_of_running_chunkservers=$((nr_of_running_chunkservers - $#))`; `nr_of_running_chunkservers=$((nr_of_running_chunkservers + $#))`; `lizardfs_wait_for_ready_chunkservers $nr_of_running_chunkservers`; `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_xor_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_master_promotions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_master_promotions.sh

Purpose: promotes multiple shadow masters in sequence and verifies metadata equality after each promotion/reconfiguration cycle.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `metadata_print`, `assert_eventually`; drives configuration through `MASTERSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `MASTER_RECONNECTION_DELAY`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_master_n $shadow_id start`; `assert_eventually "lizardfs_shadow_synchronized $shadow_id"`; `touch "${info[mount0]}"/"master=$loop_nr"`; `metadata=$(metadata_print "${info[mount0]}")`; `prev_master_id=$((loop_nr % metaservers_nr))`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MASTERSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `MASTER_RECONNECTION_DELAY`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_master_promotions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_truncates.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_truncates.sh

Purpose: compares repeated truncation and append behavior between local files and LizardFS files across standard and XOR goals and multiple boundary sizes.

Important APIs, functions, and commands: defines `verify_truncate`, `verify_append`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `file-generate`, `truncate`, `assert_success`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=$chunk file-generate "$real_file"`; `lizardfs setgoal "$goal" "file_$goal"`; `FILE_SIZE=$chunk file-generate "file_$goal"`; `verify_truncate() {`; `export MESSAGE="Veryfing truncate -s $size"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_truncates.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_nfs4_acl.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_nfs4_acl.sh

Purpose: verifies NFSv4 ACL storage and retrieval on files/directories/symlinks through the LizardFS mount.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `nfs4_setfacl`, `nfs4_getfacl`, `assert_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `assert_program_installed nfs4_setfacl`; `assert_program_installed nfs4_getfacl`; `setup_local_empty_lizardfs info`; `mkdir -p dir1/dir2`; `FILE_SIZE=1234567 file-generate file1`; `FILE_SIZE=2345678 file-generate dir1/file2`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `nfs4_setfacl`, `nfs4_getfacl`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_nfs4_acl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_optimizing_partial_stripes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_optimizing_partial_stripes.sh

Purpose: checks partial-stripe optimization for XOR data by observing visible size changes and read behavior during delayed operations.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `dd`, `expect_equals`, `assert_eventually_prints`, `expect_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `lizardfs setgoal xor3 "${info[mount0]}/dir"`; `expect_eventually_prints "$stripe_size" 'stat -c %s "${info[mount1]}/dir/f1"' '4 seconds'`; `expect_eventually_prints "$file_size" 'stat -c %s "${info[mount1]}/dir/f1"' '7 seconds'`; `expect_equals 0 "$(stat -c %s "${info[mount1]}/dir/f2")"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `valgrind`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_optimizing_partial_stripes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_posix_file_locks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_posix_file_locks.sh

Purpose: validates POSIX byte-range lock ordering, blocking, unlock, and close behavior with the posixlock helper.

Important APIs, functions, and commands: defines `assert_operation_performed`, `assert_operation_not_performed`, `readlock`, `writelock`, `unlock`; uses `setup_local_empty_lizardfs`, `file-generate`, `posixlockcmd`, `assert_success`, `assert_eventually_prints`; drives configuration through `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`; `function assert_operation_performed() {`; `assert_eventually_prints "$1" "sed -n ${opcount}p posixlock.log"`; `function assert_operation_not_performed() {`.

State and persistence behavior: State and persistence under test include active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_posix_file_locks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_all_disks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_all_disks.sh

Purpose: marks all disks of a chunkserver as EIO and verifies reads avoid bad replicas, chunk health reports EIO, and replication restores clean copies elsewhere.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `CHUNKSERVER_0_DISK_1`, `CHUNKSERVER_0_DISK_2`, `MOUNT_EXTRA_CONFIG`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir goal2`; `lizardfs setgoal 2 goal2`; `FILE_SIZE=1234 file-generate goal2/small_{1..30}`; `FILE_SIZE=300K file-generate goal2/medium_{1..30}`; `FILE_SIZE=2M file-generate goal2/big_{1..30}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, content validation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_all_disks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_single_disk.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_single_disk.sh

Purpose: injects read EIO on one disk of a chunkserver and verifies validation, health reporting, and replacement of affected copies.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNTS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir test`; `lizardfs setgoal 2 test`; `FILE_SIZE=1234 file-generate test/small_{1..10}`; `FILE_SIZE=300K file-generate test/medium_{1..10}`; `FILE_SIZE=10M file-generate test/big_{1..10}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNTS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, content validation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_single_disk.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_some_disks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_some_disks.sh

Purpose: injects read EIO on some chunkserver disks and checks mixed goal-1/goal-2 behavior, validation, probe reporting, and eventual copy recovery.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `find_chunkserver_chunks`, `file-generate`, `file-validate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `CHUNKSERVER_0_DISK_1`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir goal1`; `mkdir goal2`; `lizardfs setgoal 1 goal1`; `lizardfs setgoal 2 goal2`; `FILE_SIZE=1234 file-generate goal{1..2}/small_{1..10}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, content validation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_some_disks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_nonheader_in_chunkserver.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_nonheader_in_chunkserver.sh

Purpose: injects read EIO away from chunk headers and verifies small files remain unaffected while larger files trigger EIO classification and replica repair.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir goal2`; `lizardfs setgoal 2 goal2`; `FILE_SIZE=1234 file-generate goal2/small_{1..10}`; `FILE_SIZE=1M file-generate goal2/big_{1..10}`; `assert_success lizardfs_chunkserver_daemon 0 restart`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, content validation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_nonheader_in_chunkserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_prefetching_xor_stripes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_prefetching_xor_stripes.sh

Purpose: measures XOR stripe prefetch behavior from debug logs to ensure reads do not over-prefetch unnecessary HDD blocks.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `FILE_SIZE`, `BLOCK_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal xor2 .`; `FILE_SIZE=129M BLOCK_SIZE=12345 file-generate file`; `file-validate file`; `assert_less_or_equal "$(grep ^chunkserver.hdd_prefetch_blocks "$TEMP_DIR"/log | wc -l)" "8"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_prefetching_xor_stripes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health.sh

Purpose: validates lizardfs-probe chunks-health output across available, undergoal, endangered, lost, replicate, and delete classes as chunkservers are stopped.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_first_chunkserver_with_chunks_matching`, `expect_equals`, `expect_awk_finds`, `expect_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_$goal`; `lizardfs setgoal $goal dir_$goal`; `export MESSAGE="Veryfing health report with all the chunkservers up"`; `expect_equals 4 $(awk '/AVA/ {chunks += ($3 + $4 + $5)} END {print chunks}' <<< "$health4")`; `expect_awk_finds "/AVA $goal 1 0 0/" "$health4"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `MESSAGE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, probe health output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health_custom_goals.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health_custom_goals.sh

Purpose: validates lizardfs-probe chunks-health output across available, undergoal, endangered, lost, replicate, and delete classes as chunkservers are stopped.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `expect_equals`, `assert_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `USE_RAMDISK`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal $goal file_$goal`; `expect_equals "$first_output" "$(chunks-health-trimmed)"`; `lizardfs setgoal ${new_goal} file_*`; `expect_equals "${output[$new_goal]}" "$(chunks-health-trimmed)"`; `lizardfs setgoal ${old_goal} file_${old_goal}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, probe health output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health_custom_goals.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_info.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_info.sh

Purpose: checks lizardfs-probe info output for expected master/chunkserver aggregate fields.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `expect_equals`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_$goal`; `lizardfs setgoal $goal dir_$goal`; `FILE_SIZE=150K file-generate dir_$goal/file`; `rm dir_3/file`; `rm dir_xor2/file`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_info.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_iolimits_status.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_iolimits_status.sh

Purpose: validates lizardfs-probe iolimits-status output against configured I/O limits state.

Important APIs, functions, and commands: defines `status`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `expect_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `GLOBALIOLIMITS_FILENAME`, `GLOBALIOLIMITS_RENEGOTIATION_PERIOD_SECONDS`, `GLOBALIOLIMITS_ACCUMULATE_MS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_equals "1 150.000 30 blkio`; `lizardfs_admin_master reload-config`; `expect_equals "2 150.000 30 blkio`; `expect_equals "" "$(status)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `GLOBALIOLIMITS_FILENAME`, `GLOBALIOLIMITS_RENEGOTIATION_PERIOD_SECONDS`, `GLOBALIOLIMITS_ACCUMULATE_MS`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_iolimits_status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_chunkservers.sh

Purpose: checks list-chunkservers porcelain fields, labels, used space, connection state, and version reporting.

Important APIs, functions, and commands: defines `list_chunkservers`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `expect_equals`, `expect_eventually_prints`, `expect_awk_finds_no`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_$goal`; `lizardfs setgoal $goal dir_$goal`; `list_chunkservers() {`; `lizardfs-probe list-chunkservers --porcelain localhost "${info[matocl]}"`; `export MESSAGE="Veryfing chunkservers list with all the chunkservers up"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_chunkservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_disks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_disks.sh

Purpose: checks list-disks porcelain output for multiple chunkservers and disks, including labels and disk health fields.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `expect_equals`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_$goal`; `lizardfs setgoal $goal dir_$goal`; `FILE_SIZE=60M file-generate dir_$goal/file`; `expect_equals 12 $(wc -l <<< "$disks")`; `cs_data="$(grep ":${info[chunkserver${i}_port]} " <<< "$disks")"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_disks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_metadataservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_metadataservers.sh

Purpose: checks list-metadataservers output for master and shadow rows and synchronization status.

Important APIs, functions, and commands: defines `list_metadata_servers`; uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_equals`, `assert_eventually`, `assert_eventually_prints`; drives configuration through `USE_RAMDISK`, `MASTERSERVERS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `list_metadata_servers() {`; `lizardfs_probe_master list-metadataservers --porcelain`; `master_expected_state="^$ip ${info[matocl]} $host master running $meta $version\$"`; `shadow_expected_state="^$ip ${info[master1_matocl]} $host shadow connected $meta $version\$"`; `assert_matches "$master_expected_state" "$(list_metadata_servers)"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MASTERSERVERS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_metadataservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_mounts.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_mounts.sh

Purpose: checks list-mounts output for multiple client mounts.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `expect_equals`; drives configuration through `MOUNTS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_equals "4" $(wc -l <<< "$mounts")`; `expect_equals \`.

State and persistence behavior: State and persistence under test include client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `USE_RAMDISK`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: soft expectation accumulation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_mounts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_metadataserver_status.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_metadataserver_status.sh

Purpose: checks metadataserver-status porcelain output for the master version/state tuple.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `assert_equals`, `assert_eventually_prints`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_eventually_prints $'master\trunning' \`; `changelog_version=$(tail -1 "${info[master_data_path]}"/changelog.mfs | grep -o '^[0-9]*')`; `assert_equals $version "$((changelog_version + 1))"`; `lizardfs_master_n 1 start`; `assert_eventually_prints $'shadow\tconnected\t'$version \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_metadataserver_status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_in_chunkserver.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_in_chunkserver.sh

Purpose: injects write EIO and verifies writes fail or succeed as expected while chunk health and repair recover bad copies.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `ACCEPTABLE_DIFFERENCE`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_success lizardfs_chunkserver_daemon 0 restart`; `lizardfs_wait_for_all_ready_chunkservers`; `mkdir test`; `lizardfs setgoal 2 test`; `FILE_SIZE=1234 assert_success file-generate test/small_{1..10}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_in_chunkserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_nonheader_in_chunkserver.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_nonheader_in_chunkserver.sh

Purpose: injects write EIO outside chunk headers and verifies only affected large writes are classified and repaired.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `ACCEPTABLE_DIFFERENCE`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_success lizardfs_chunkserver_daemon 0 restart`; `lizardfs_wait_for_all_ready_chunkservers`; `mkdir test`; `lizardfs setgoal 2 test`; `FILE_SIZE=1234 assert_success file-generate test/small_{1..20}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_nonheader_in_chunkserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_inodes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_inodes.sh

Purpose: tests directory inode quota limits, soft/hard enforcement, accounting, and cleanup behavior.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `assert_equals`, `lizardfs {makesnapshot, repquota, setquota}`; drives configuration through `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setquota -d 0 0 $softlimit $hardlimit dir`; `lizardfs makesnapshot dir/file$i dir/snapshot_file$i`; `lizardfs makesnapshot dir/soft1 dir/snapshot_soft1`; `expect_failure touch dir/file`.

State and persistence behavior: State and persistence under test include quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_inodes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_size.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_size.sh

Purpose: tests directory size quota limits and accounting under writes, truncates, and cleanup.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `truncate`, `dd`, `assert_equals`, `lizardfs {makesnapshot, setquota}`; drives configuration through `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setquota -d $soft $hard 0 0 dir`; `expect_failure head -c 1024 /dev/zero > dir/file_4`; `assert_equals "$(stat --format=%s dir/file_4)" 0 # file was created, but no data was written`; `expect_failure head -c $((64*1024*1024)) /dev/zero >> dir/file_1`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_size.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_inodes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_inodes.sh

Purpose: tests user/group inode quota enforcement and reporting on the mounted filesystem.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {setquota}`; drives configuration through `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setquota -g $gid1 0 0 $softlimit $hardlimit .`; `sudo -nu lizardfstest_1 mkdir dir_$gid1`; `expect_failure sudo -nu lizardfstest_1 touch dir_$gid1/file`; `expect_failure sudo -nu lizardfstest_1 mkdir dir2_$gid1`; `expect_failure sudo -nu lizardfstest_1 ln -s dir_$gid1/4 dir_$gid1/soft2`.

State and persistence behavior: State and persistence under test include quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_inodes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_permissions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_permissions.sh

Purpose: checks that quota modification permissions follow export/admin rules and user identity expectations.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {repquota, setquota}`; drives configuration through `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_failure lizardfs setquota -g $gid 0 0 3 6 . # fail, permissions missing`; `expect_failure lizardfs repquota -a . # fail, permissions missing`; `expect_failure lizardfs repquota -g $gid1 . # fail, permissions missing`; `expect_failure lizardfs repquota -u $uid1 . # fail, permissions missing`; `expect_success lizardfs repquota -g $gid . # OK`.

State and persistence behavior: State and persistence under test include quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_permissions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_corrupted_file_with_goal_1.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_corrupted_file_with_goal_1.sh

Purpose: corrupts a single-copy file and verifies reads surface failure rather than silently returning invalid data.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_chunkserver_chunks`, `file-generate`, `file-validate`, `dd`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=1234567 file-generate file`; `find_chunkserver_chunks 0 | xargs -d'\n' -IXX \`; `if timeout -s KILL 3s file-validate file; then`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_corrupted_file_with_goal_1.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_only.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_only.sh

Purpose: checks read-only mount behavior across file, directory, xattr, attr, rename, unlink, truncate, and metadata-modifying operations.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_metalogger_daemon`, `file-generate`, `file-validate`, `truncate`, `dd`, `attr`, `setfattr`, `setfacl`, `metadata_print`, `metadata_generate_all`, `metadata_validate_files`, ...; drives configuration through `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_1_EXTRA_EXPORTS`, `MFSEXPORTS_EXTRA_OPTIONS`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `assert_program_installed attr`; `setup_local_empty_lizardfs info`; `lizardfs_metalogger_daemon start`; `metadata_generate_all`; `FILE_SIZE=16M file-generate rw_file`; `expect_success setfacl -m mask::r rw_file`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, `setfattr`, `setfacl`, environment/config variables such as `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_1_EXTRA_EXPORTS`, `MFSEXPORTS_EXTRA_OPTIONS`, `FILE_SIZE`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, soft expectation accumulation, content validation, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_only.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_write_during_scan.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_write_during_scan.sh

Purpose: performs reads and writes while chunk scanning is slowed to catch races between scan state and client I/O.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`, `LD_PRELOAD`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir goal3`; `lizardfs setgoal 2 goal3`; `FILE_SIZE=1K file-generate goal3/test_${file}`; `lizardfs_chunkserver_daemon 0 stop`; `lizardfs_chunkserver_daemon 1 stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_write_during_scan.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_faulty_master_parallel.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_faulty_master_parallel.sh

Purpose: runs parallel readdir workloads while the master is restarted or faulted to detect client directory-read races.

Important APIs, functions, and commands: defines `master_restarting_loop`, `thread`; uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `expect_equals`; drives configuration through `MASTER_RESTART_DELAY_SECS`, `READDIR_SLEEP_SECS`, `THREAD_COUNT`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `master_restarting_loop() {`; `expect_success lizardfs_master_daemon restart`; `mkdir -p "$dir" && cd "$dir"`; `setup_local_empty_lizardfs info`; `master_restarting_loop 1 &`; `expect_equals $files_expected $files_iterated`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `python3`, environment/config variables such as `MASTER_RESTART_DELAY_SECS`, `READDIR_SLEEP_SECS`, `THREAD_COUNT`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_faulty_master_parallel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_unlink_loop.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_unlink_loop.sh

Purpose: runs the readdir-unlink helper loop to stress directory iteration while entries are being removed.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `assert_success`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_success readdir-unlink-test 1024`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_unlink_loop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_recursive_remove.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_recursive_remove.sh

Purpose: removes a large generated tree recursively and validates metadata/chunk cleanup and command completion.

Important APIs, functions, and commands: defines `dirgenerate`; uses `setup_local_empty_lizardfs`, `assert_eventually`, `lizardfs {rremove, setgoal, settrashtime}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `MASTER_CUSTOM_GOALS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir root${level}_${suffix}`; `mkdir test`; `lizardfs setgoal ec test`; `lizardfs settrashtime 0 test`; `lizardfs rremove test`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_recursive_remove.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_redundancy_level.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_redundancy_level.sh

Purpose: checks minimum ready chunkserver requirements for standard, XOR, and EC goals as servers are stopped and restarted.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_master_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `dd`, `assert_success`, `assert_failure`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `REDUNDANCY_LEVEL`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_chunkserver_daemon 0 stop`; `mkdir ec_dir xor4_dir std5_dir xor3_dir`; `lizardfs setgoal ec32 ec_dir`; `lizardfs setgoal xor3 xor3_dir`; `lizardfs setgoal xor4 xor4_dir`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `REDUNDANCY_LEVEL`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_redundancy_level.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_bandwidth_limiting.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_bandwidth_limiting.sh

Purpose: verifies replication bandwidth limiting by measuring replication progress for many chunks under a small limit.

Important APIs, functions, and commands: defines `chunks_health`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_chunkserver_chunks`, `file-generate`, `assert_success`, `assert_equals`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `REPLICATION_BANDWIDTH_LIMIT_KBPS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `CHUNKS_WRITE_REP_LIMIT`, `CHUNKS_READ_REP_LIMIT`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal 2 dir`; `FILE_SIZE=${file_size_kb}K file-generate $(seq 1 $chunks_count)`; `assert_equals $chunks_count $(find_chunkserver_chunks 0 | wc -l)`; `lizardfs_chunkserver_daemon 0 stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `REPLICATION_BANDWIDTH_LIMIT_KBPS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, probe health output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_bandwidth_limiting.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_delay_disconnect.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_delay_disconnect.sh

Purpose: checks that delayed replication does not start too early and reacts correctly when chunkservers disconnect.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `file-generate`, `assert_equals`, `assert_eventually_prints`, `lizardfs {checkfile}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `ACCEPTABLE_DIFFERENCE`, `CHUNKS_WRITE_REP_LIMIT`, `OPERATIONS_DELAY_INIT`, `OPERATIONS_DELAY_DISCONNECT`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_chunkserver_daemon 0 stop`; `lizardfs_chunkserver_daemon 1 stop`; `lizardfs_chunkserver_daemon 2 stop`; `lizardfs_chunkserver_daemon 3 stop`; `lizardfs_chunkserver_daemon 4 stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_delay_disconnect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_with_endangered_chunks_priority.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_with_endangered_chunks_priority.sh

Purpose: verifies endangered chunks are replicated before less urgent undergoal chunks when priority is enabled.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_all_chunks`, `find_chunkserver_chunks`, `file-generate`, `assert_equals`, `assert_eventually_prints`, `lizardfs {checkfile}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `ACCEPTABLE_DIFFERENCE`, `CHUNKS_WRITE_REP_LIMIT`, `OPERATIONS_DELAY_INIT`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_chunkserver_daemon 1 stop`; `lizardfs_chunkserver_daemon 2 stop`; `lizardfs_wait_for_ready_chunkservers 2`; `FILE_SIZE=1K file-generate "${info[mount0]}"/file{1..20}`; `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 2 copies: *1' | wc -l)`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_with_endangered_chunks_priority.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_restart_consistency.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_restart_consistency.sh

Purpose: generates rich metadata, restarts daemons, and compares metadata printouts to catch persistence or reload inconsistencies.

Important APIs, functions, and commands: defines `do_iteration`; uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `setfacl`, `getfacl`, `assert_success`, `assert_equals`, `assert_eventually`; drives configuration through `MESSAGE`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `LZFS_MOUNT_COMMAND`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `assert_program_installed setfacl getfacl python3`; `MESSAGE="Testing ACL support in $TEMP_DIR/" assert_success setfacl -m group:fuse:rw "$TEMP_DIR/f"`; `MFSEXPORTS_EXTRA_OPTIONS=nomasterpermcheck,ignoregid \`; `setup_local_empty_lizardfs info`; `mkdir -p "$lizdir" "$tmpdir"`; `lizardfs_master_daemon restart`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `setfacl`, `getfacl`, `python3`, environment/config variables such as `MESSAGE`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `LZFS_MOUNT_COMMAND`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_restart_consistency.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_richacl.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_richacl.sh

Purpose: checks richacl command support and ACL persistence through LizardFS where richacl tooling is available.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `richacl`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `richacl`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_richacl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_secondary_groups.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_secondary_groups.sh

Purpose: checks access decisions that depend on a user secondary group list rather than only primary UID/GID.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `dd`, `assert_success`, `assert_failure`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `assert_success sudo -nu lizardfstest_0 touch file1`; `assert_success sudo -nu lizardfstest_0 chmod 600 file1`; `assert_failure cat file1`; `assert_failure sudo -nu lizardfstest_3 cat file1`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_secondary_groups.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_checksum_error_recovery.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_checksum_error_recovery.sh

Purpose: checks that a shadow can recover from metadata checksum error conditions and resynchronize with the master.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_success`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `sed -i 's/file/fool/g' "${info[master_data_path]}"/changelog.mfs`; `lizardfs_master_n 1 start`; `assert_eventually "lizardfs_shadow_synchronized 1"`; `assert_success awk '`; `/master.mismatch/ && i == 0 {i++; next;}`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_checksum_error_recovery.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_connects_during_dumping.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_connects_during_dumping.sh

Purpose: connects a shadow while the master is dumping metadata to verify synchronization does not race a partial dump.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `mfsmetarestore`, `assert_eventually`; drives configuration through `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `master_cfg="MFSMETARESTORE_PATH = $TEMP_DIR/metarestore.sh"`; `master_cfg+="|MAGIC_PREFER_BACKGROUND_DUMP = 1"`; `master_cfg+="|MAGIC_DISABLE_METADATA_DUMPS = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `lizardfs_admin_master save-metadata --async # Start dumping metadata`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_connects_during_dumping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_metadata_generate.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_metadata_generate.sh

Purpose: generates broad metadata while a shadow is present and verifies the shadow stays synchronized and consistent.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `metadata_print`, `metadata_generate_all`, `metadata_validate_files`, `assert_eventually`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `export CHANGELOG="${info[master_data_path]}"/changelog.mfs`; `lizardfs_master_n 1 start`; `metadata_generate_all`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_metadata_generate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_promotion_during_dumping.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_promotion_during_dumping.sh

Purpose: promotes a shadow while metadata dumping is in progress to validate promotion safety under dump races.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_shadow`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `mfsmetarestore`, `metadata_print`, `assert_eventually`; drives configuration through `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `master_cfg="MFSMETARESTORE_PATH = $TEMP_DIR/metarestore.sh"`; `master_cfg+="|MAGIC_PREFER_BACKGROUND_DUMP = 1"`; `master_cfg+="|MAGIC_DISABLE_METADATA_DUMPS = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `mfsmetarestore "\$@"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions, metadata diff checks, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_promotion_during_dumping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reconnect.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reconnect.sh

Purpose: restarts or disconnects a shadow and verifies it resynchronizes after reconnect.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_equals`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_master_n 1 start`; `assert_eventually "lizardfs_shadow_synchronized 1"`; `files_before=$(ls "${info[master1_data_path]}" | grep -v "stats.mfs" | sort)`; `shadow_pid=$(lizardfs_master_n 1 test 2>&1 | sed 's/.*: //')`; `assert_matches "^[0-9]+$" "$shadow_pid"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`, `MAGIC_DISABLE_METADATA_DUMPS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reconnect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reject.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reject.sh

Purpose: checks rejection paths for invalid or incompatible shadow-master connections.

Important APIs, functions, and commands: defines `my_client`, `run_my_client`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_shadow`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_success`, `assert_failure`, `assert_equals`, `assert_eventually`; drives configuration through `MASTERSERVERS`, `USE_RAMDISK`, `PORT`.

Control flow: The script proceeds through these visible steps: `assert_program_installed nc`; `setup_local_empty_lizardfs info`; `lizardfs_master_n 1 start`; `assert_eventually 'lizardfs_shadow_synchronized 1'`; `local PORT=${info[master${1}_${2}]}`; `assert_equals "$expected_status" `cat ${TEMP_DIR}/${ma_to_someone}_exit_status || echo 1``.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MASTERSERVERS`, `USE_RAMDISK`, `PORT`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reject.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reloading_metadata.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reloading_metadata.sh

Purpose: checks shadow behavior while metadata is reloaded and changed on the master.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `metadata_print`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_master_n 1 start`; `assert_eventually "lizardfs_shadow_synchronized 1"`; `shadow_pid=$(lizardfs_master_n 1 test 2>&1 | sed 's/.*: //')`; `assert_matches "^[0-9]+$" "$shadow_pid"`; `lizardfs_master_daemon restart`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reloading_metadata.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_sessions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_sessions.sh

Purpose: verifies client session state visible through master/shadow failover and synchronization paths.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_mount_unmount`, `lizardfs_mount_start`, `metadata_print`, `metadata_get_all_generators`, `metadata_validate_files`, `assert_success`, `assert_failure`, `assert_equals`, ...; drives configuration through `MOUNTS`, `MASTERSERVERS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_0_EXTRA_EXPORTS`, `MOUNT_1_EXTRA_EXPORTS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount1]}/subdir"`; `lizardfs_mount_unmount 1`; `lizardfs_mount_start 1`; `lizardfs_master_n 1 start`; `for generator in $(metadata_get_all_generators |grep -v metadata_generate_uids_gids); do`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `MASTERSERVERS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_0_EXTRA_EXPORTS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_sessions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_synchronization.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_synchronization.sh

Purpose: checks baseline shadow synchronization over metadata changes and chunkserver availability changes.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `metadata_generate_all`, `assert_success`, `assert_equals`, `assert_eventually`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `OPERATIONS_DELAY_INIT`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|OPERATIONS_DELAY_INIT = 1"`; `master_cfg+="|CHUNKS_LOOP_MIN_TIME = 1|CHUNKS_LOOP_MAX_CPU = 90"`; `master_cfg+="|BACK_META_KEEP_PREVIOUS = 0"`; `MASTER_0_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_FAIL_ON="master.matoml_changelog_apply_error" \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `OPERATIONS_DELAY_INIT`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; quota accounting risks off-by-one and soft/hard-limit drift; lock tests risk stale owners or blocked helper processes. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_synchronization.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_undel.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_undel.sh

Purpose: checks trash undel operations through a shadow-aware setup and verifies restored file contents.

Important APIs, functions, and commands: defines `stat_basic_info`, `only_file_in_trash`; uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `file-generate`, `file-validate`, `assert_success`, `assert_equals`, `assert_eventually`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, `MFSEXPORTS_META_EXTRA_OPTIONS`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|AUTO_RECOVERY = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `assert_equals "1" "$(ls "$trash" | grep -v undel | wc -l)"`; `changelog_file="${info[master_data_path]}"/changelog.mfs`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_undel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_small_operations.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_small_operations.sh

Purpose: runs many small filesystem operations as a smoke/stress test for ordinary file creation, writes, reads, and metadata updates.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `BLOCK_SIZE`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `BLOCK_SIZE=$block_size FILE_SIZE=500K file-generate file`; `file-validate file || test_add_failure \`; `FILE_SIZE=70M file-generate file`; `BLOCK_SIZE=$block_size file-validate file || test_add_failure \`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `BLOCK_SIZE`, `FILE_SIZE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_small_operations.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_snapshot_goal.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_snapshot_goal.sh

Purpose: checks snapshot goal behavior and chunk placement across labeled server groups and recursive snapshot scenarios.

Important APIs, functions, and commands: defines `chunks_state`; uses `setup_local_empty_lizardfs`, `find_all_chunks`, `file-generate`, `file-validate`, `assert_success`, `assert_failure`, `assert_equals`, `assert_eventually_prints`, `lizardfs {makesnapshot, setgoal, settrashtime}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `ACCEPTABLE_DIFFERENCE`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal 4 file`; `FILE_SIZE=$((1000 + LIZARDFS_CHUNK_SIZE)) file-generate file`; `assert_success file-validate file`; `assert_equals "8 standard" "$(chunks_state)"`; `lizardfs makesnapshot file file_snapshot1`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `ACCEPTABLE_DIFFERENCE`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_snapshot_goal.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_sockets_leak_check.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_sockets_leak_check.sh

Purpose: checks daemon socket descriptor counts across operations to catch socket leaks.

Important APIs, functions, and commands: defines `get_used_socket_count`; uses `setup_local_empty_lizardfs`, `dd`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `USE_RAMDISK`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_sockets_leak_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_tape_goals_read_only.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_tape_goals_read_only.sh

Purpose: checks read-only behavior for tape-style/custom goals and validates files remain readable under those constraints.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`, `dd`, `assert_success`, `assert_failure`, `expect_equals`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=1K file-generate file{1..25}`; `assert_success lizardfs setgoal -r tapegoal .`; `expect_success file-validate "$file"`; `expect_equals 2 $(lizardfs fileinfo "$file" | grep copy | wc -l)`; `assert_success chmod +r $file`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, soft expectation accumulation, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_tape_goals_read_only.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_basic.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_basic.sh

Purpose: validates trash retention, undel restore, metadata mount behavior, and stat preservation for deleted files.

Important APIs, functions, and commands: defines `stat_basic_info`, `only_file_in_trash`; uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`, `assert_success`, `assert_failure`, `assert_equals`, `assert_eventually`, `lizardfs {setgoal, settrashtime}`; drives configuration through `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_equals "1" "$(ls "$trash" | grep -v undel | wc -l)"`; `mkdir dir dir2`; `lizardfs setgoal 1 dir`; `lizardfs settrashtime 10000 dir dir2`; `FILE_SIZE=1M file-generate file file2`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_rename.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_rename.sh

Purpose: stress-tests renaming many trashed files through the meta mount before undel restoration.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `assert_success`, `assert_equals`, `assert_eventually`, `lizardfs {settrashtime}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs settrashtime -r 3600 dir/`; `rm -rf dir/`; `mkdir untrashed`; `assert_eventually "test -e '$trash'/*recovered_$i" # rename in trash is asynchronous!`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_META_EXTRA_OPTIONS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_rename.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate.sh

Purpose: checks client truncate retry behavior when the only chunkserver is temporarily unavailable and when retry time is exceeded.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `find_all_chunks`, `file-generate`, `file-validate`, `truncate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `find_all_chunks | xargs rm -f`; `lizardfs_chunkserver_daemon $i restart`; `lizardfs_wait_for_all_ready_chunkservers`; `mkdir -p tmp;`; `lizardfs setgoal $goal tmp`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_retry.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_retry.sh

Purpose: checks writes and truncates fail cleanly when an EC/XOR-style file lacks enough available parts.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `file-generate`, `file-validate`, `truncate`, `assert_failure`, `assert_equals`, `assert_awk_finds`, `assert_awk_finds_no`, `lizardfs {fileinfo}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=1234 file-generate file`; `lizardfs_chunkserver_daemon 0 stop`; `assert_awk_finds '/no valid copies/' "$(lizardfs fileinfo file)"`; `(sleep 3.1 && lizardfs_chunkserver_daemon 0 start) & truncate -s 123 file`; `assert_awk_finds '/[0-9A-F]+_00000002/' "$(lizardfs fileinfo file)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; checksum assertions can miss bugs if corruption/recalculation timing is not exercised. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_retry.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_xor_with_not_enough_copies.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_xor_with_not_enough_copies.sh

Purpose: validates truncate and append behavior around block and chunk boundaries for standard and XOR goals.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `truncate`, `dd`, `assert_success`, `assert_failure`, `assert_equals`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal ec31 dir`; `lizardfs_chunkserver_daemon 0 stop`; `lizardfs_chunkserver_daemon 1 stop`; `lizardfs_wait_for_ready_chunkservers 2`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `USE_RAMDISK`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_xor_with_not_enough_copies.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_unlink.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_unlink.sh

Purpose: tests unlink behavior for open files, replicated chunks, and metadata cleanup.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_all_chunks`, `dd`, `lizardfs {setgoal, settrashtime}`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal 3 "$file"`; `lizardfs setgoal xor3 "$xorfile"`; `lizardfs settrashtime 0 "$file" "$xorfile"`; `rm -f "$file" "$xorfile"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_unlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_whole_file_locks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_whole_file_locks.sh

Purpose: validates whole-file flock and POSIX-style lock behavior plus admin manage-locks listing and forced unlock operations.

Important APIs, functions, and commands: defines `test_locks`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_daemon`, `file-generate`, `assert_success`, `assert_equals`, `assert_eventually_prints`; drives configuration through `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`; `function assert_operation_performed() {`; `assert_eventually_prints "$1" "sed -n ${opcount}p ${logfile}"`; `assert_operation_performed "read open: $1"`.

State and persistence behavior: State and persistence under test include active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_whole_file_locks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_write_partial.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_write_partial.sh

Purpose: checks partial writes into EC and XOR files at boundary offsets and validates resulting file contents.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `file-generate`, `file-validate`, `assert_awk_finds`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `BLOCK_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_ec_4_17`; `lizardfs setgoal -r ec_4_17 dir_ec_4_17`; `FILE_SIZE=123456789 BLOCK_SIZE=12345 file-generate dir_ec_4_17/file`; `if ! file-validate dir_ec_4_17/file; then`; `assert_awk_finds "/part $part\/21/" "$(lizardfs fileinfo dir_ec_4_17/file)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_write_partial.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xattr.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xattr.sh

Purpose: checks extended attribute create/list/read/remove behavior on files, symlinks, and directories.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `attr`, `expect_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `assert_program_installed attr`; `setup_local_empty_lizardfs info`; `mkdir dir`; `name3="$(base64 -w 0 /dev/urandom | head -c 250)" # attr can't set >250B name (but doc says 256B)`; `expect_success attr -qs "$name1" -V "$value1" .`; `expect_success attr -qs "$name2" -V "$value2" file`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, extended attributes, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xattr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_goal_with_labels.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_goal_with_labels.sh

Purpose: checks XOR goal placement with chunkserver labels and goal transitions across ssd/hdd/mixed labels.

Important APIs, functions, and commands: defines `chunks_state`, `count_chunks_on_chunkservers`; uses `setup_local_empty_lizardfs`, `find_all_chunks`, `find_chunkserver_chunks`, `file-generate`, `assert_equals`, `assert_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `CHUNKS_SOFT_DEL_LIMIT`, `CHUNKS_WRITE_REP_LIMIT`, `OPERATIONS_DELAY_INIT`, ....

Control flow: The script proceeds through these visible steps: `count_chunks_on_chunkservers() {`; `find_chunkserver_chunks $i`; `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal xor2_ssd dir`; `FILE_SIZE=1K file-generate dir/file`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_goal_with_labels.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_overwriting.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_overwriting.sh

Purpose: stress-tests overwriting XOR files while chunkservers are stopped and restarted.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_first_chunkserver_with_chunks_matching`, `file-generate`, `file-validate`, `dd`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor3 "$dir"`; `FILE_SIZE=${file_size_mb}M file-generate "$tmpf"`; `if ! file-validate "$dir/file"; then`; `csid=$(find_first_chunkserver_with_chunks_matching 'chunk_xor_1_of_3*')`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_overwriting.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_parallel_writing.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_parallel_writing.sh

Purpose: stress-tests parallel writes to an XOR file while chunkserver availability changes.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_first_chunkserver_with_chunks_matching`, `file-generate`, `file-validate`, `dd`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal xor3 "$file"`; `FILE_SIZE=25M file-generate "$tmpf"`; `seq $i 10 $((25*1024-1)) | shuf | expect_success xargs -P5 -IXX \`; `MESSAGE="Data is corrupted after writing" expect_success file-validate "$file"`; `csid=$(find_first_chunkserver_with_chunks_matching 'chunk_xor_1_of_3*')`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_parallel_writing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_all_combinations.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_all_combinations.sh

Purpose: reads a large XOR file while stopping all tested combinations of chunkservers to verify reconstruction from every available-part set.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor9 "$dir"`; `FILE_SIZE=876M file-generate "$dir/file"`; `lizardfs_chunkserver_daemon $i stop`; `if ! file-validate "$dir/file"; then`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_all_combinations.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_without_parity.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_without_parity.sh

Purpose: checks that an XOR file can be read after the parity-holding chunkserver is stopped.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_first_chunkserver_with_chunks_matching`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor2 "$dir"`; `FILE_SIZE=6M file-generate "$dir/file"`; `csid=$(find_first_chunkserver_with_chunks_matching 'chunk_xor_parity_of_2*')`; `lizardfs_chunkserver_daemon $csid stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_without_parity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_atomicity.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_atomicity.sh

Purpose: checks XOR truncate operations are atomic and leave either old or new valid contents.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_all_chunks`, `file-generate`, `file-validate`, `truncate`, `dd`, `assert_success`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=200K file-generate "$source"`; `lizardfs setgoal xor$level "$file"`; `truncate -s ${i}K "${info[mount$((2 + i % 3))]}/$file"`; `MESSAGE="Testing xor level $level" assert_success file-validate "$file"`; `find_all_chunks -name "*xor_1_of*" | xargs rm -vf`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_atomicity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_missing_parts.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_missing_parts.sh

Purpose: truncates XOR files and snapshots with missing parts to verify reconstruction and repair behavior.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `file-generate`, `file-validate`, `truncate`, `assert_success`, `lizardfs {makesnapshot, setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir xor$i`; `lizardfs setgoal xor$i xor$i`; `FILE_SIZE=$size file-generate xor$i/file_$size`; `assert_success file-validate xor$i/file_$size`; `lizardfs makesnapshot xor$i/file_$size xor$i/snapshot_$size`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_missing_parts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_brute_force_lost_chunks_ec_n_k.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_brute_force_lost_chunks_ec_n_k.inc

Purpose: template include that brute-forces lost data/parity part combinations for an EC(n,k) goal and validates that each selected failure pattern remains readable or fails as intended.

Important APIs, functions, and commands: defines `get_ec_chunk_part_from_filename`, `iteration`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_chunkserver_chunks`, `file-generate`, `file-validate`, `assert_eventually`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `BLOCK_SIZE`.

Control flow: The script proceeds through these visible steps: `assert_program_installed python3 tee`; `local lost_chunkservers=`; `lost_chunkservers="${lost_chunkservers} ${chunkservers[$chunk]}"`; `echo "Losing chunkservers: $lost_chunkservers"`; `for chunkserver in $lost_chunkservers; do`; `assert_eventually "lizardfs_chunkserver_daemon $chunkserver isalive" "100 seconds"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `python3`, `tee`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; lock tests risk stale owners or blocked helper processes; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_brute_force_lost_chunks_ec_n_k.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_chunk_type_conversion.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_chunk_type_conversion.inc

Purpose: template include that converts files between standard, XOR, and EC goal types, then verifies fileinfo part layout and readability through chunkserver outages.

Important APIs, functions, and commands: defines `verify_file_goal`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `find_all_chunks`, `file-generate`, `file-validate`, `lizardfs {fileinfo, getgoal, setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`, `REDUNDANCY_LEVEL`, `CHUNKS_REBALANCING_BETWEEN_LABELS`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `goal=$(lizardfs getgoal "$file" | awk '{print $NF}')`; `lizardfs fileinfo "$file" | grep "part $i/$((level+1)) of $goal$" > /dev/null \`; `copies=$(lizardfs fileinfo "$file" | egrep 'copy.*:[a-zA-Z0-9_]+$' | sort | uniq | wc -l)`; `lizardfs fileinfo "$file"`; `test_fail "Unknown 'lizardfs getgoal $file' output: $goal"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_TIME`, `CHUNKS_LOOP_MAX_CPU`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_chunk_type_conversion.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc

Purpose: upgrade template that starts with legacy LizardFS services, overwrites files during a staged upgrade to current binaries, and validates all files after chunkserver churn.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_chunkserver_daemon`, `lizardfs_master_daemon`, `lizardfs_wait_for_ready_chunkservers`, `lizardfs_mount_unmount`, `lizardfs_mount_start`, `mfsmount`, `lizardfsXX`, `lizardfsXX_chunkserver_daemon`, `assert_success`; drives configuration through `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`, `START_WITH_LEGACY_LIZARDFS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `OPERATIONS_DELAY_INIT`, `REPLICATION_SPEED`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_lizardfsXX_services_count_equals 1 ${CHUNKSERVERS} 1`; `mkdir dir`; `assert_success lizardfsXX mfssetgoal $GOAL dir`; `assert_success generate_files_various_filesizes file_count`; `lizardfsXX_chunkserver_daemon 0 stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`, `START_WITH_LEGACY_LIZARDFS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; upgrade tests depend on external package availability and version-specific behavior. Test signals: hard assertions, probe/admin porcelain output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc

Purpose: upgrade template that creates undergoal chunks with a legacy version and validates current-version replication/recovery behavior after service upgrade.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_wait_for_all_ready_chunkservers`, `mfsmount`, `lizardfsXX`, `assert_success`; drives configuration through `CHUNKSERVERS_GOAL_COVER`, `CHUNKSERVERS_REDUNDANT`, `CHUNKSERVERS_MINIMUM`, `REPLICATION_SPEED`, `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`, `START_WITH_LEGACY_LIZARDFS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_lizardfsXX_services_count_equals 1 $CHUNKSERVERS_GOAL_COVER 1`; `stop_lizardfsXX_chunkservers_from_to $CHUNKSERVERS_MINIMUM $CHUNKSERVERS_GOAL_COVER`; `assert_lizardfsXX_services_count_equals 1 $CHUNKSERVERS_MINIMUM 1`; `mkdir dir`; `assert_success lizardfsXX mfssetgoal $GOAL dir`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS_GOAL_COVER`, `CHUNKSERVERS_REDUNDANT`, `CHUNKSERVERS_MINIMUM`, `REPLICATION_SPEED`, `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; upgrade tests depend on external package availability and version-specific behavior. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_overwriting.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_overwriting.inc

Purpose: stress-tests overwriting XOR files while chunkservers are stopped and restarted.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor2 "$dir"`; `master_restarting_loop &`; `chunkservers_restarting_loop $CHUNKSERVERS &`; `stop_master_restarting_thread`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_overwriting.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_reading_consistency.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_reading_consistency.inc

Purpose: long-running XOR consistency template for repeated validation/read workloads under master and chunkserver restarts.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor2 "$dir"`; `master_restarting_loop &`; `chunkservers_restarting_loop $CHUNKSERVERS &`; `stop_master_restarting_thread`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_reading_consistency.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_writing.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_writing.inc

Purpose: long-running XOR consistency template for repeated write workloads under master and chunkserver restarts.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor2 "$dir"`; `master_restarting_loop &`; `chunkservers_restarting_loop $CHUNKSERVERS &`; `stop_master_restarting_thread`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_writing.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/test_xor_consistency_utils.sh -->
# sources/distributed-fs/lizardfs/tests/test_utils/test_xor_consistency_utils.sh

Purpose: shared concurrency utilities for XOR consistency templates, spawning write, overwrite, validate, master-restart, and chunkserver-restart loops.

Important APIs, functions, and commands: defines `writing_loop_thread`, `overwriting_loop_thread`, `verifying_loop_thread`, `master_restarting_loop`, `chunkservers_restarting_loop`, `stop_master_restarting_thread`, `stop_chunkservers_restarting_thread`; uses `lizardfs_chunkserver_daemon`, `lizardfs_master_daemon`, `file-generate`, `file-overwrite`, `file-validate`; drives configuration through `BLOCK_SIZE`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `: ${MASTER_RESTARTING_LOOP_FILE:=${TEMP_DIR}/.master_restarting_loop_flag}`; `: ${CHUNKSERVERS_RESTARTING_LOOP_FILE:=${TEMP_DIR}/.chunkservers_restarting_loop_flag}`; `BLOCK_SIZE=$block_size FILE_SIZE=$file_size expect_success file-generate "$file_name"`; `MESSAGE="Overwring using block size $BLOCK_SIZE B" expect_success file-overwrite "$file"`; `expect_success file-validate "$file"`; `master_restarting_loop() {`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `BLOCK_SIZE`, `FILE_SIZE`, `MESSAGE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/test_xor_consistency_utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/upgrade.sh -->
# sources/distributed-fs/lizardfs/tests/test_utils/upgrade.sh

Purpose: shared upgrade-test helpers for stopping legacy services, switching to current daemons, generating deterministic files, validating fixtures, and manipulating chunkserver ranges.

Important APIs, functions, and commands: defines `generate_file`, `validate_file`; uses `lizardfs_admin_master`, `lizardfs_chunkserver_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_mount_unmount`, `lizardfs_mount_start`, `file-generate`, `file-validate`, `lizardfsXX_chunkserver_daemon`, `lizardfsXX_master_daemon`, `assert_success`, `assert_equals`; drives configuration through `SEED`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `function stop_lizardfsXX_chunkservers_from_to {`; `lizardfsXX_chunkserver_daemon $i stop`; `assert_equals 1 $mas_n # so far, we always have only 1 legacy master`; `assert_success lizardfs_mount_unmount $i`; `assert_success lizardfsXX_chunkserver_daemon $i stop`; `assert_success lizardfsXX_master_daemon stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `SEED`, `FILE_SIZE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: upgrade tests depend on external package availability and version-specific behavior. Test signals: hard assertions, content validation, probe/admin porcelain output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/upgrade.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/assert.sh -->
# sources/distributed-fs/lizardfs/tests/tools/assert.sh

Purpose: implements the shell assertion DSL used by the LizardFS system tests, generating assert, assertlocal, and expect variants from assertion templates and attaching source-location/backtrace diagnostics.

Important APIs, functions, and commands: template functions define program, file, equality, numeric, regex, AWK, diff, success/failure, and eventually assertions; a loop synthesizes `assert_*`, `assertlocal_*`, and `expect_*` wrappers with source context.

Control flow: Control flow routes each public assertion wrapper through a template with `FAIL_FUNCTION` set to assert, assertlocal, or expect semantics; eventually assertions call `wait_for`, while failures collect source context and stack traces before failing or continuing.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `ASSERT_NAME`, `ASSERT_FILE`, `ASSERT_LINE`, `FAIL_FUNCTION`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/assert.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/chunks.sh -->
# sources/distributed-fs/lizardfs/tests/tools/chunks.sh

Purpose: provides LizardFS test harness coverage for chunks.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `goal_to_part_count`, `filesize_to_chunk_count`, `redundant_parts`, `minimum_number_of_parts`, `check_one_file_part_coverage`, and `check_one_file_replicated` encode chunk-count and replication expectations.

Control flow: The script proceeds through these visible steps: `local goal="$(lizardfs getgoal "${path}" | awk '{print $2}')"`; `local fileinfo="$(lizardfs fileinfo ${path})"`; `assert_eventually 'check_one_file_part_coverage_impl_ "${path}" "${expected_number_of_parts}"' "${replication_timeout}"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: LizardFS CLI/test helpers.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/chunks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/color.sh -->
# sources/distributed-fs/lizardfs/tests/tools/color.sh

Purpose: provides LizardFS test harness coverage for color.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `col_on`, `col_off`, `msg`, `lizardfs_make_conf_for_master_dbg`, `lizardfs_make_conf_for_shadow_dbg`; uses `lizardfs_master_n`; drives configuration through `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`.

Control flow: The script proceeds through these visible steps: `lizardfs_make_conf_for_master_dbg() {`; `msg MAGENTA lizardfs_make_conf_for_master_dbg $*`; `local old_master=$(lizardfs_current_master_id)`; `echo -n "old master $old_master: "`; `lizardfs_master_n ${old_master} test | cat`; `lizardfs_make_conf_for_master "${@}"`.

State and persistence behavior: State and persistence under test include shadow-master synchronization state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/color.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/combinations.py -->
# sources/distributed-fs/lizardfs/tests/tools/combinations.py

Purpose: generates bash-readable combinations and random subset selections for erasure-code and lost-part brute-force tests.

Important APIs, functions, and commands: defines `binomial`, `ith_combination_of_fixed_size`, `random_subsets_of_fixed_size`, `all_combinations`, `selected_combinations`, `bashprint`, `print_random_subsets_of_fixed_size`, `print_all_combinations`, `print_selected_combinations`.

Control flow: Control flow parses command-line arguments, loads or computes the requested data, validates input consistency, then prints machine-readable output or exits nonzero on invalid input.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: Python standard library.

Risks and test signals: Risks: randomized paths need deterministic validation to avoid irreproducible failures. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/combinations.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/config.sh -->
# sources/distributed-fs/lizardfs/tests/tools/config.sh

Purpose: provides LizardFS test harness coverage for config.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `check_configuration`; uses `mfsmount`, `mfsmaster`, `mfschunkserver`; drives configuration through `TEMP_DIR`, `PATH`.

Control flow: The script proceeds through these visible steps: `elif [[ -f /etc/lizardfs_tests.conf ]]; then`; `echo "Using the default \"/etc/lizardfs_tests.conf\" tests configuration file"`; `. /etc/lizardfs_tests.conf`; `mkdir -p "$TEMP_DIR"`; `if ! touch "$TEMP_DIR/check_tmp_dir" || ! rm "$TEMP_DIR/check_tmp_dir"; then`; `$LIZARDFS_ROOT/sbin/{mfsmaster,mfschunkserver} \`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `TEMP_DIR`, `PATH`, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/continuous_test.sh -->
# sources/distributed-fs/lizardfs/tests/tools/continuous_test.sh

Purpose: provides LizardFS test harness coverage for continuous_test.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `continuous_test_begin`; uses `assert_success`.

Control flow: The script proceeds through these visible steps: `assert_success mfsdirinfo -h "${LIZARDFS_MOUNTPOINT:-}"`; `assert_success mkdir -p "$workspace"`.

State and persistence behavior: State and persistence under test include client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/continuous_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/filter_tests.py -->
# sources/distributed-fs/lizardfs/tests/tools/filter_tests.py

Purpose: partitions GoogleTest-style LizardFS test cases across CI nodes using stored duration data and explicit exclusions so concurrent runs have roughly balanced wall time.

Important APIs, functions, and commands: defines `get_excluded_tests_two_types`, `get_gtest_testlist`, `get_data_testlist`, `get_tests_list_with_durations`, `add_to_partition_dict`, `partition_algorithm`, `print_tests_to_run`, `get_tests_data`; uses `lizardfs {test}`.

Control flow: Control flow parses command-line arguments, loads or computes the requested data, validates input consistency, then prints machine-readable output or exits nonzero on invalid input.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`, Python standard library, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/filter_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/generate_tests_from_templates.sh -->
# sources/distributed-fs/lizardfs/tests/tools/generate_tests_from_templates.sh

Purpose: provides LizardFS test harness coverage for generate_tests_from_templates.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: drives configuration through `CMAKE_DIRECTORY`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `CMAKE_DIRECTORY`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/generate_tests_from_templates.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfs.sh -->
# sources/distributed-fs/lizardfs/tests/tools/lizardfs.sh

Purpose: provides the core shell harness for building an isolated LizardFS test installation: it writes master, shadow, metalogger, chunkserver, exports, goals, topology, and mount configs; starts daemons; exposes admin/probe shortcuts; and stores all runtime addresses and paths in the global lizardfs_info_ associative array.

Important APIs, functions, and commands: `setup_local_empty_lizardfs` is the entry point; daemon wrappers include `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_chunkserver_daemon`, and `lizardfs_metalogger_daemon`; helpers include config writers, mount control, chunk finders, `lizardfs_probe_master`, `lizardfs_admin_master`, `lizardfs_wait_for_ready_chunkservers`, and `lizardfs_shadow_synchronized`.

Control flow: Control flow starts in `setup_local_empty_lizardfs`: prepare directories, optionally install MooseFS or legacy LizardFS, write common master files, add master/shadows, start daemons, add chunkservers, mount clients, optionally add an auto shadow/CGI server, wait for readiness, and export the info array.

State and persistence behavior: State is concentrated under `$TEMP_DIR/lizardfs/etc`, `$TEMP_DIR/lizardfs/var`, `$TEMP_DIR/mnt`, ramdisk/loop disk paths, generated config files, daemon data directories, and the exported `lizardfs_info_` array. Persistent behavior under test includes metadata files, changelogs, chunk files, export passwords, goal definitions, daemon ports, and mount command state.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `PATH`, `LIZARDFSXX_DIR`, `MAGIC_DEBUG_LOG_C`, `USE_BDB_FOR_NAME_STORAGE`, `PERSONALITY`, `SYSLOG_IDENT`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; checksum assertions can miss bugs if corruption/recalculation timing is not exercised. Test signals: hard assertions, probe/admin porcelain output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfsXX.sh -->
# sources/distributed-fs/lizardfs/tests/tools/lizardfsXX.sh

Purpose: provides LizardFS test harness coverage for lizardfsXX.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `install_lizardfsXX`, `test_lizardfsXX_executables`, `lizardfsXX_chunkserver_daemon`, `lizardfsXX_master_daemon`, `lizardfsXX`, `assert_lizardfsXX_services_count_equals`, and `assert_no_lizardfsXX_services_active` encapsulate legacy-version setup and invocation.

Control flow: The script proceeds through these visible steps: `rm -rf "$LIZARDFSXX_DIR"`; `mkdir -p "$LIZARDFSXX_DIR"`; `mkdir -p ${TEMP_DIR}/apt/apt.conf.d`; `mkdir -p ${TEMP_DIR}/apt/var/lib/apt/partial`; `mkdir -p ${TEMP_DIR}/apt/var/cache/apt/archives/partial`; `mkdir -p ${TEMP_DIR}/apt/var/lib/dpkg`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `apt-get`, `dnf`, `wget`, `dpkg-deb`, `rpm2cpio`, `fakeroot`, environment/config variables such as `LIZARDFSXX_TAG`, `APT_CONFIG`, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfsXX.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/logs.sh -->
# sources/distributed-fs/lizardfs/tests/tools/logs.sh

Purpose: provides LizardFS test harness coverage for logs.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `save_oplog_to_file`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/metadata.sh -->
# sources/distributed-fs/lizardfs/tests/tools/metadata.sh

Purpose: generates and prints broad metadata fixtures used by recovery, dump, mapall, shadow, and restart-consistency tests, covering files, quotas, trash, goals, trashtime, extended attributes, ACLs, snapshots, renames, truncates, and lock metadata.

Important APIs, functions, and commands: metadata APIs include `metadata_print`, `metadata_get_version`, `metadata_generate_all`, `metadata_get_all_generators`, and focused generators for files, quotas, unlink/trash, goals, trashtime, eattrs, chunks, snapshots, xattrs, ACLs, renames, uids/gids, touch, truncate, and file locks.

Control flow: The script proceeds through these visible steps: `metadata_print() {`; `assert_program_installed getfattr`; `lizardfs fileinfo "$file" | grep -v $'^\t\t' # remove "copy N" and "no valid copies"`; `lizardfs getgoal "$file"`; `lizardfs gettrashtime "$file"`; `lizardfs geteattr "$file"`.

State and persistence behavior: State is the mounted filesystem tree plus metadata-visible attributes: chunk layout, goals, trash times, eattrs, quotas, ACLs, xattrs, stat data, symlinks, changelog-derived trash events, and optional meta-mount paths.

Dependencies and integration points: Dependencies and integration points: `attr`, `getfattr`, `setfacl`, `getfacl`, `tee`, environment/config variables such as `NR`, `FILE_SIZE`, `BLOCK_SIZE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/metadata.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/moosefs.sh -->
# sources/distributed-fs/lizardfs/tests/tools/moosefs.sh

Purpose: provides LizardFS test harness coverage for moosefs.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `build_moosefs_or_use_cache`, `test_moosefs`, `build_moosefs`, `moosefs_chunkserver_daemon`, `moosefs_master_daemon`, `mfs`.

Control flow: The script proceeds through these visible steps: `rm -rf "$MOOSEFS_DIR"`; `mkdir -p "$MOOSEFS_DIR"`; `mkdir src`; `test -x "$MOOSEFS_DIR/sbin/mfschunkserver"`; `test -x "$MOOSEFS_DIR/sbin/mfsmaster"`; `moosefs_chunkserver_daemon() {`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `wget`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/moosefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/network.sh -->
# sources/distributed-fs/lizardfs/tests/tools/network.sh

Purpose: provides LizardFS test harness coverage for network.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `get_ip_addr`, `get_next_port_number`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/network.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/permissions.sh -->
# sources/distributed-fs/lizardfs/tests/tools/permissions.sh

Purpose: provides LizardFS filesystem semantics coverage for permissions.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `describe_permissions`.

Control flow: The script proceeds through these visible steps: `('mkdir', 'os.mkdir(sys.argv[1] + "/x")'),`.

State and persistence behavior: State and persistence under test include extended attributes; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/permissions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/quota.sh -->
# sources/distributed-fs/lizardfs/tests/tools/quota.sh

Purpose: provides LizardFS quota coverage for quota.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: uses `assert_equals`, `lizardfs {repquota}`.

Control flow: The script proceeds through these visible steps: `assert_equals "$expected_limits" \`; `"$(lizardfs repquota -g $gid . | trim_hard | grep "Group $gid")" > /dev/null`; `"$(lizardfs repquota -d $directory | trim_hard | grep "Directory $directory")" > /dev/null`.

State and persistence behavior: State and persistence under test include quota counters and limits; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: LizardFS CLI/test helpers.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/quota.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/random.sh -->
# sources/distributed-fs/lizardfs/tests/tools/random.sh

Purpose: provides LizardFS test harness coverage for random.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `parse_si_suffix`, `random`, `unique_file`, `pseudorandom_init`, `prng`, `pseudorandom`, and subset helpers provide deterministic and nondeterministic data generation.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`, `tee`.

Risks and test signals: Risks: randomized paths need deterministic validation to avoid irreproducible failures. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/random.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/report.sh -->
# sources/distributed-fs/lizardfs/tests/tools/report.sh

Purpose: provides LizardFS test harness coverage for report.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `report`, `report_masters`; uses `lizardfs_master_n`; drives configuration through `REPORT`, `PERSONALITY`, `RESULT`.

Control flow: The script proceeds through these visible steps: `report_masters`; `report_masters() {`; `for ((msid_loc=0 ; msid_loc<${info[masterserver_count]}; ++msid_loc)); do`; `if [ "${msid_loc}" = "$(lizardfs_current_master_id)" ] ; then`; `RESULT=$(lizardfs_master_n ${msid_loc} test |& cat)`.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `REPORT`, `PERSONALITY`, `RESULT`, LizardFS CLI/test helpers.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/report.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/run_test_concurrently.sh -->
# sources/distributed-fs/lizardfs/tests/tools/run_test_concurrently.sh

Purpose: provides LizardFS test harness coverage for run_test_concurrently.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: uses `lizardfs {-j, directory, export}`; drives configuration through `NODES_COUNT`, `NODE_NUMBER`, `ARG_NAME`, `KEY`, `VALUE`, `WORKSPACE`, `TEST_SUITE`, `EXCLUDE_TESTS`, `RUN_UNITTESTS`, `VALGRIND`, ....

Control flow: The script proceeds through these visible steps: `make -C build/lizardfs -j$(nproc) install`; `mkdir -m 777 -p $TEST_OUTPUT_DIR`; `rm -rf "${TEST_OUTPUT_DIR:?}"/* || true`; `rm -rf /mnt/ramdisk/* || true`; `--lizardfs_tests_path "${LIZARDFS_TESTS_PATH}" \`.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`, `valgrind`, environment/config variables such as `NODES_COUNT`, `NODE_NUMBER`, `ARG_NAME`, `KEY`, `VALUE`, `WORKSPACE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/run_test_concurrently.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/stack_trace.sh -->
# sources/distributed-fs/lizardfs/tests/tools/stack_trace.sh

Purpose: provides LizardFS test harness coverage for stack_trace.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `get_stack`, `print_stack`; drives configuration through `STACK`, `IFS`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `STACK`, `IFS`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/stack_trace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/string.sh -->
# sources/distributed-fs/lizardfs/tests/tools/string.sh

Purpose: provides LizardFS test harness coverage for string.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `version_compare_gte`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/string.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/system.sh -->
# sources/distributed-fs/lizardfs/tests/tools/system.sh

Purpose: provides LizardFS test harness coverage for system.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `drop_caches`, `is_program_installed`, `system_init`, `inode_of`, `size_of`, `get_nproc_clamped_between`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/system.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test.sh -->
# sources/distributed-fs/lizardfs/tests/tools/test.sh

Purpose: provides LizardFS test harness coverage for test.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `test_begin`, `test_end`, `test_fail`, `test_add_failure`, `test_freeze_result`, `test_frozen`, `parametrize_command`, `test_cleanup`, and `catch_error_` implement the shell test lifecycle, failure accumulation, cleanup, and error trapping.

Control flow: The script proceeds through these visible steps: `rm -f "$ERROR_DIR/syslog.log"`; `'user=$(stat -c "%U" "{}"); sudo -nu $user setfacl -b "{}" ; sudo -nu $user chmod 777 "{}"' \;`; `echo "TEMP_DIR variable empty, cowardly refusing to rm -rf /*"`; `if ! rm -rf "$TEMP_DIR"/* 2>/dev/null; then`; `rm -rf "$TEMP_DIR"/*`; `if ! rm -rf "$RAMDISK_DIR"/* 2>/dev/null; then`.

State and persistence behavior: State includes the failure counter, frozen-result marker, cleanup traps, test start/end timestamps, and global shell variables consumed by the framework.

Dependencies and integration points: Dependencies and integration points: `setfacl`, `tee`, environment/config variables such as `PS4`, LizardFS CLI/test helpers.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test_main.sh -->
# sources/distributed-fs/lizardfs/tests/tools/test_main.sh

Purpose: provides LizardFS test harness coverage for test_main.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: uses `mfsmetarestore`, `lizardfs-polonaise-server`, `mfsmount`, `mfsmaster`, `mfschunkserver`.

Control flow: The script proceeds through these visible steps: `for i in mfsmaster mfschunkserver mfsmount mfsmetarestore mfsmetalogger \`; `. $(which set_lizardfs_constants.sh)`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `valgrind`, LizardFS CLI/test helpers.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift; randomized paths need deterministic validation to avoid irreproducible failures; metadata tests risk comparing volatile fields unless output is normalized. Test signals: restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test_main.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/time.sh -->
# sources/distributed-fs/lizardfs/tests/tools/time.sh

Purpose: provides LizardFS test harness coverage for time.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `timestamp`, `nanostamp`, `wait_for`, `execution_time`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/time.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/timeout.sh -->
# sources/distributed-fs/lizardfs/tests/tools/timeout.sh

Purpose: provides LizardFS test harness coverage for timeout.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `timeout_init`, `timeout_set`, `timeout_set_multiplier`, `timeout_rescale`, `timeout_rescale_seconds`, and `timeout_killer_thread` own test timeout scaling and termination.

Control flow: The script proceeds through these visible steps: `assert_program_installed python3`.

State and persistence behavior: State includes the current timeout string, scaling multiplier, and background killer process that exits or kills the test after the rescaled deadline.

Dependencies and integration points: Dependencies and integration points: `python3`, `valgrind`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/timeout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/valgrind.sh -->
# sources/distributed-fs/lizardfs/tests/tools/valgrind.sh

Purpose: provides LizardFS test harness coverage for valgrind.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `valgrind_enabled`, `valgrind_enable`, `valgrind_terminate`.

Control flow: The script proceeds through these visible steps: `assert_program_installed valgrind`; `mv "$tmpfile" "$valgrind_script_"`; `rm -f /tmp/vgdb-pipe*by-lizardfstest* || true # clean up any garbage left in /tmp`.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `valgrind`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/valgrind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/utils/CMakeLists.txt

Purpose: declares build and install rules for LizardFS test/support utilities and LD_PRELOAD libraries used by the integration suite.

Important APIs, functions, and commands: defines `add_executable`, `add_library`, `endif`, `if`, `include_directories`, `install`, `target_link_libraries`; uses `file-generate`, `file-overwrite`, `file-validate`, `file-validate-growing`, `posixlockcmd`, `flockcmd`.

Control flow: Control flow is CMake configure-time declaration: optional compiler flags are applied, libraries/executables are declared, linked where needed, and installed into the configured binary or library subdirectories.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: CMake build graph, LizardFS CLI/test helpers.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; EIO injection depends on chunk-file naming and disk health classification. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/asserts.h -->
# sources/distributed-fs/lizardfs/utils/asserts.h

Purpose: defines lightweight C/C++ assertion macros for utility binaries, reporting failed conditions or mismatched values with file and line context before aborting.

Important APIs, functions, and commands: is primarily declarative or command-oriented with no reusable functions.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/asserts.h -->
