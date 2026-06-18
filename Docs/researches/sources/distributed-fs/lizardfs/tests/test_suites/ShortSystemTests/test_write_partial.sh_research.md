<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_write_partial.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_write_partial.sh

Purpose: checks partial writes into EC and XOR files at boundary offsets and validates resulting file contents.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `file-generate`, `file-validate`, `assert_awk_finds`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `BLOCK_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_ec_4_17`; `lizardfs setgoal -r ec_4_17 dir_ec_4_17`; `FILE_SIZE=123456789 BLOCK_SIZE=12345 file-generate dir_ec_4_17/file`; `if ! file-validate dir_ec_4_17/file; then`; `assert_awk_finds "/part $part\/21/" "$(lizardfs fileinfo dir_ec_4_17/file)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_write_partial.sh -->
