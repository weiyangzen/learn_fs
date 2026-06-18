<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/test_xor_consistency_utils.sh -->
# sources/distributed-fs/lizardfs/tests/test_utils/test_xor_consistency_utils.sh

Purpose: shared concurrency utilities for XOR consistency templates, spawning write, overwrite, validate, master-restart, and chunkserver-restart loops.

Important APIs, functions, and commands: defines `writing_loop_thread`, `overwriting_loop_thread`, `verifying_loop_thread`, `master_restarting_loop`, `chunkservers_restarting_loop`, `stop_master_restarting_thread`, `stop_chunkservers_restarting_thread`; uses `lizardfs_chunkserver_daemon`, `lizardfs_master_daemon`, `file-generate`, `file-overwrite`, `file-validate`; drives configuration through `BLOCK_SIZE`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `: ${MASTER_RESTARTING_LOOP_FILE:=${TEMP_DIR}/.master_restarting_loop_flag}`; `: ${CHUNKSERVERS_RESTARTING_LOOP_FILE:=${TEMP_DIR}/.chunkservers_restarting_loop_flag}`; `BLOCK_SIZE=$block_size FILE_SIZE=$file_size expect_success file-generate "$file_name"`; `MESSAGE="Overwring using block size $BLOCK_SIZE B" expect_success file-overwrite "$file"`; `expect_success file-validate "$file"`; `master_restarting_loop() {`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `BLOCK_SIZE`, `FILE_SIZE`, `MESSAGE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/test_xor_consistency_utils.sh -->
