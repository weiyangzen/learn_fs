<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_secondary_groups.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_secondary_groups.sh

Purpose: checks access decisions that depend on a user secondary group list rather than only primary UID/GID.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `dd`, `assert_success`, `assert_failure`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `assert_success sudo -nu lizardfstest_0 touch file1`; `assert_success sudo -nu lizardfstest_0 chmod 600 file1`; `assert_failure cat file1`; `assert_failure sudo -nu lizardfstest_3 cat file1`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_secondary_groups.sh -->
