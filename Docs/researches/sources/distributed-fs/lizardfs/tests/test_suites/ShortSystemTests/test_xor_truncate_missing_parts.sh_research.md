<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_missing_parts.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_missing_parts.sh

Purpose: truncates XOR files and snapshots with missing parts to verify reconstruction and repair behavior.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `file-generate`, `file-validate`, `truncate`, `assert_success`, `lizardfs {makesnapshot, setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir xor$i`; `lizardfs setgoal xor$i xor$i`; `FILE_SIZE=$size file-generate xor$i/file_$size`; `assert_success file-validate xor$i/file_$size`; `lizardfs makesnapshot xor$i/file_$size xor$i/snapshot_$size`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_missing_parts.sh -->
