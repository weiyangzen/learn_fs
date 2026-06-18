<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/quota.sh -->
# sources/distributed-fs/lizardfs/tests/tools/quota.sh

Purpose: provides LizardFS quota coverage for quota.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: uses `assert_equals`, `lizardfs {repquota}`.

Control flow: The script proceeds through these visible steps: `assert_equals "$expected_limits" \`; `"$(lizardfs repquota -g $gid . | trim_hard | grep "Group $gid")" > /dev/null`; `"$(lizardfs repquota -d $directory | trim_hard | grep "Directory $directory")" > /dev/null`.

State and persistence behavior: State and persistence under test include quota counters and limits; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: LizardFS CLI/test helpers.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/quota.sh -->
