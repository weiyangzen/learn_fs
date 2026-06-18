<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_iolimits_status.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_iolimits_status.sh

Purpose: validates lizardfs-probe iolimits-status output against configured I/O limits state.

Important APIs, functions, and commands: defines `status`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `expect_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `GLOBALIOLIMITS_FILENAME`, `GLOBALIOLIMITS_RENEGOTIATION_PERIOD_SECONDS`, `GLOBALIOLIMITS_ACCUMULATE_MS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_equals "1 150.000 30 blkio`; `lizardfs_admin_master reload-config`; `expect_equals "2 150.000 30 blkio`; `expect_equals "" "$(status)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `GLOBALIOLIMITS_FILENAME`, `GLOBALIOLIMITS_RENEGOTIATION_PERIOD_SECONDS`, `GLOBALIOLIMITS_ACCUMULATE_MS`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_iolimits_status.sh -->
