<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test_main.sh -->
# sources/distributed-fs/lizardfs/tests/tools/test_main.sh

Purpose: provides LizardFS test harness coverage for test_main.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: uses `mfsmetarestore`, `lizardfs-polonaise-server`, `mfsmount`, `mfsmaster`, `mfschunkserver`.

Control flow: The script proceeds through these visible steps: `for i in mfsmaster mfschunkserver mfsmount mfsmetarestore mfsmetalogger \`; `. $(which set_lizardfs_constants.sh)`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `valgrind`, LizardFS CLI/test helpers.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift; randomized paths need deterministic validation to avoid irreproducible failures; metadata tests risk comparing volatile fields unless output is normalized. Test signals: restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test_main.sh -->
