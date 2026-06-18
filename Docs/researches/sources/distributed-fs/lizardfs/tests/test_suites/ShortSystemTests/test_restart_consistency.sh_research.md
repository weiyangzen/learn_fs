<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_restart_consistency.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_restart_consistency.sh

Purpose: generates rich metadata, restarts daemons, and compares metadata printouts to catch persistence or reload inconsistencies.

Important APIs, functions, and commands: defines `do_iteration`; uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `setfacl`, `getfacl`, `assert_success`, `assert_equals`, `assert_eventually`; drives configuration through `MESSAGE`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `LZFS_MOUNT_COMMAND`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `assert_program_installed setfacl getfacl python3`; `MESSAGE="Testing ACL support in $TEMP_DIR/" assert_success setfacl -m group:fuse:rw "$TEMP_DIR/f"`; `MFSEXPORTS_EXTRA_OPTIONS=nomasterpermcheck,ignoregid \`; `setup_local_empty_lizardfs info`; `mkdir -p "$lizdir" "$tmpdir"`; `lizardfs_master_daemon restart`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `setfacl`, `getfacl`, `python3`, environment/config variables such as `MESSAGE`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `LZFS_MOUNT_COMMAND`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_restart_consistency.sh -->
