<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_mounts.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_mounts.sh

Purpose: checks list-mounts output for multiple client mounts.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `expect_equals`; drives configuration through `MOUNTS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_equals "4" $(wc -l <<< "$mounts")`; `expect_equals \`.

State and persistence behavior: State and persistence under test include client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `USE_RAMDISK`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: soft expectation accumulation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_mounts.sh -->
