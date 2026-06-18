<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_unlink_loop.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_unlink_loop.sh

Purpose: runs the readdir-unlink helper loop to stress directory iteration while entries are being removed.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `assert_success`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_success readdir-unlink-test 1024`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_unlink_loop.sh -->
