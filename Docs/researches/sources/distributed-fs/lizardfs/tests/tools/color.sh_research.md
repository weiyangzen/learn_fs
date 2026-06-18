<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/color.sh -->
# sources/distributed-fs/lizardfs/tests/tools/color.sh

Purpose: provides LizardFS test harness coverage for color.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `col_on`, `col_off`, `msg`, `lizardfs_make_conf_for_master_dbg`, `lizardfs_make_conf_for_shadow_dbg`; uses `lizardfs_master_n`; drives configuration through `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`.

Control flow: The script proceeds through these visible steps: `lizardfs_make_conf_for_master_dbg() {`; `msg MAGENTA lizardfs_make_conf_for_master_dbg $*`; `local old_master=$(lizardfs_current_master_id)`; `echo -n "old master $old_master: "`; `lizardfs_master_n ${old_master} test | cat`; `lizardfs_make_conf_for_master "${@}"`.

State and persistence behavior: State and persistence under test include shadow-master synchronization state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/color.sh -->
