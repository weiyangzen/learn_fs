<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_parallel_writing.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_parallel_writing.sh

Purpose: stress-tests parallel writes to an XOR file while chunkserver availability changes.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_first_chunkserver_with_chunks_matching`, `file-generate`, `file-validate`, `dd`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal xor3 "$file"`; `FILE_SIZE=25M file-generate "$tmpf"`; `seq $i 10 $((25*1024-1)) | shuf | expect_success xargs -P5 -IXX \`; `MESSAGE="Data is corrupted after writing" expect_success file-validate "$file"`; `csid=$(find_first_chunkserver_with_chunks_matching 'chunk_xor_1_of_3*')`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_parallel_writing.sh -->
