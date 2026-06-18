<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_tape_goals_read_only.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_tape_goals_read_only.sh

Purpose: checks read-only behavior for tape-style/custom goals and validates files remain readable under those constraints.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`, `dd`, `assert_success`, `assert_failure`, `expect_equals`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=1K file-generate file{1..25}`; `assert_success lizardfs setgoal -r tapegoal .`; `expect_success file-validate "$file"`; `expect_equals 2 $(lizardfs fileinfo "$file" | grep copy | wc -l)`; `assert_success chmod +r $file`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, soft expectation accumulation, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_tape_goals_read_only.sh -->
