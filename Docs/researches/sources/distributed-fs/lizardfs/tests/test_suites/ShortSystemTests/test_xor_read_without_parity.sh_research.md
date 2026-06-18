<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_without_parity.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_without_parity.sh

Purpose: checks that an XOR file can be read after the parity-holding chunkserver is stopped.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_first_chunkserver_with_chunks_matching`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "$dir"`; `lizardfs setgoal xor2 "$dir"`; `FILE_SIZE=6M file-generate "$dir/file"`; `csid=$(find_first_chunkserver_with_chunks_matching 'chunk_xor_parity_of_2*')`; `lizardfs_chunkserver_daemon $csid stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_read_without_parity.sh -->
