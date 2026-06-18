<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_inodes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_inodes.sh

Purpose: tests user/group inode quota enforcement and reporting on the mounted filesystem.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {setquota}`; drives configuration through `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setquota -g $gid1 0 0 $softlimit $hardlimit .`; `sudo -nu lizardfstest_1 mkdir dir_$gid1`; `expect_failure sudo -nu lizardfstest_1 touch dir_$gid1/file`; `expect_failure sudo -nu lizardfstest_1 mkdir dir2_$gid1`; `expect_failure sudo -nu lizardfstest_1 ln -s dir_$gid1/4 dir_$gid1/soft2`.

State and persistence behavior: State and persistence under test include quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_inodes.sh -->
