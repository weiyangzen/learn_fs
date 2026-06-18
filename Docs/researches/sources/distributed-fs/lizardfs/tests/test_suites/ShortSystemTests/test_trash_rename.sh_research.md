<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_rename.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_rename.sh

Purpose: stress-tests renaming many trashed files through the meta mount before undel restoration.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `assert_success`, `assert_equals`, `assert_eventually`, `lizardfs {settrashtime}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs settrashtime -r 3600 dir/`; `rm -rf dir/`; `mkdir untrashed`; `assert_eventually "test -e '$trash'/*recovered_$i" # rename in trash is asynchronous!`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_META_EXTRA_OPTIONS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_trash_rename.sh -->
