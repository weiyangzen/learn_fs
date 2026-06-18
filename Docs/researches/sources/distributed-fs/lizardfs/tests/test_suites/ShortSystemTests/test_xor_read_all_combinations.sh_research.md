<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_all_combinations.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_all_combinations.sh

Purpose: reads a large XOR file while stopping all tested combinations of chunkservers to verify reconstruction from every available-part set.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor9 "$dir"`; `FILE_SIZE=876M file-generate "$dir/file"`; `lizardfs_chunkserver_daemon $i stop`; `if ! file-validate "$dir/file"; then`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_all_combinations.sh -->
