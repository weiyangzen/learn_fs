<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_size.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_size.sh

Purpose: tests directory size quota limits and accounting under writes, truncates, and cleanup.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `truncate`, `dd`, `assert_equals`, `lizardfs {makesnapshot, setquota}`; drives configuration through `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setquota -d $soft $hard 0 0 dir`; `expect_failure head -c 1024 /dev/zero > dir/file_4`; `assert_equals "$(stat --format=%s dir/file_4)" 0 # file was created, but no data was written`; `expect_failure head -c $((64*1024*1024)) /dev/zero >> dir/file_1`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_dir_size.sh -->
