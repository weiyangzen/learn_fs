<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/valgrind.sh -->
# sources/distributed-fs/lizardfs/tests/tools/valgrind.sh

Purpose: provides LizardFS test harness coverage for valgrind.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `valgrind_enabled`, `valgrind_enable`, `valgrind_terminate`.

Control flow: The script proceeds through these visible steps: `assert_program_installed valgrind`; `mv "$tmpfile" "$valgrind_script_"`; `rm -f /tmp/vgdb-pipe*by-lizardfstest* || true # clean up any garbage left in /tmp`.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `valgrind`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/valgrind.sh -->
