<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/timeout.sh -->
# sources/distributed-fs/lizardfs/tests/tools/timeout.sh

Purpose: provides LizardFS test harness coverage for timeout.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `timeout_init`, `timeout_set`, `timeout_set_multiplier`, `timeout_rescale`, `timeout_rescale_seconds`, and `timeout_killer_thread` own test timeout scaling and termination.

Control flow: The script proceeds through these visible steps: `assert_program_installed python3`.

State and persistence behavior: State includes the current timeout string, scaling multiplier, and background killer process that exits or kills the test after the rescaled deadline.

Dependencies and integration points: Dependencies and integration points: `python3`, `valgrind`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/timeout.sh -->
