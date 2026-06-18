<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/permissions.sh -->
# sources/distributed-fs/lizardfs/tests/tools/permissions.sh

Purpose: provides LizardFS filesystem semantics coverage for permissions.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `describe_permissions`.

Control flow: The script proceeds through these visible steps: `('mkdir', 'os.mkdir(sys.argv[1] + "/x")'),`.

State and persistence behavior: State and persistence under test include extended attributes; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/permissions.sh -->
