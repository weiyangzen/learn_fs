<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_basic.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_basic.sh

Purpose: validates trash retention, undel restore, metadata mount behavior, and stat preservation for deleted files.

Important APIs, functions, and commands: defines `stat_basic_info`, `only_file_in_trash`; uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`, `assert_success`, `assert_failure`, `assert_equals`, `assert_eventually`, `lizardfs {setgoal, settrashtime}`; drives configuration through `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_equals "1" "$(ls "$trash" | grep -v undel | wc -l)"`; `mkdir dir dir2`; `lizardfs setgoal 1 dir`; `lizardfs settrashtime 10000 dir dir2`; `FILE_SIZE=1M file-generate file file2`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_basic.sh -->
