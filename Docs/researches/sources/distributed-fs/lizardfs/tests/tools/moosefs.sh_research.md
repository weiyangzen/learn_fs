<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/moosefs.sh -->
# sources/distributed-fs/lizardfs/tests/tools/moosefs.sh

Purpose: provides LizardFS test harness coverage for moosefs.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `build_moosefs_or_use_cache`, `test_moosefs`, `build_moosefs`, `moosefs_chunkserver_daemon`, `moosefs_master_daemon`, `mfs`.

Control flow: The script proceeds through these visible steps: `rm -rf "$MOOSEFS_DIR"`; `mkdir -p "$MOOSEFS_DIR"`; `mkdir src`; `test -x "$MOOSEFS_DIR/sbin/mfschunkserver"`; `test -x "$MOOSEFS_DIR/sbin/mfsmaster"`; `moosefs_chunkserver_daemon() {`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `wget`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/moosefs.sh -->
