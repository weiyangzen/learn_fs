<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_inodes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_inodes.sh

Purpose: tests directory inode quota limits, soft/hard enforcement, accounting, and cleanup behavior.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `assert_equals`, `lizardfs {makesnapshot, repquota, setquota}`; drives configuration through `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setquota -d 0 0 $softlimit $hardlimit dir`; `lizardfs makesnapshot dir/file$i dir/snapshot_file$i`; `lizardfs makesnapshot dir/soft1 dir/snapshot_soft1`; `expect_failure touch dir/file`.

State and persistence behavior: State and persistence under test include quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_inodes.sh -->
