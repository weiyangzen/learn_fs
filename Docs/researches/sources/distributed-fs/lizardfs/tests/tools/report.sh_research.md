<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/report.sh -->
# sources/distributed-fs/lizardfs/tests/tools/report.sh

Purpose: provides LizardFS test harness coverage for report.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `report`, `report_masters`; uses `lizardfs_master_n`; drives configuration through `REPORT`, `PERSONALITY`, `RESULT`.

Control flow: The script proceeds through these visible steps: `report_masters`; `report_masters() {`; `for ((msid_loc=0 ; msid_loc<${info[masterserver_count]}; ++msid_loc)); do`; `if [ "${msid_loc}" = "$(lizardfs_current_master_id)" ] ; then`; `RESULT=$(lizardfs_master_n ${msid_loc} test |& cat)`.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `REPORT`, `PERSONALITY`, `RESULT`, LizardFS CLI/test helpers.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/report.sh -->
