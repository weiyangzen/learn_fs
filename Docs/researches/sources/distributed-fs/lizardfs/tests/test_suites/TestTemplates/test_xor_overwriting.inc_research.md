<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_overwriting.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_overwriting.inc

Purpose: stress-tests overwriting XOR files while chunkservers are stopped and restarted.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor2 "$dir"`; `master_restarting_loop &`; `chunkservers_restarting_loop $CHUNKSERVERS &`; `stop_master_restarting_thread`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `DATA_SIZE_PER_THREAD`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_xor_overwriting.inc -->
