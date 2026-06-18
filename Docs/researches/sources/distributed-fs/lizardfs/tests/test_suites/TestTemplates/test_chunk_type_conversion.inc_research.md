<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_chunk_type_conversion.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_chunk_type_conversion.inc

Purpose: template include that converts files between standard, XOR, and EC goal types, then verifies fileinfo part layout and readability through chunkserver outages.

Important APIs, functions, and commands: defines `verify_file_goal`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `find_all_chunks`, `file-generate`, `file-validate`, `lizardfs {fileinfo, getgoal, setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`, `REDUNDANCY_LEVEL`, `CHUNKS_REBALANCING_BETWEEN_LABELS`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `goal=$(lizardfs getgoal "$file" | awk '{print $NF}')`; `lizardfs fileinfo "$file" | grep "part $i/$((level+1)) of $goal$" > /dev/null \`; `copies=$(lizardfs fileinfo "$file" | egrep 'copy.*:[a-zA-Z0-9_]+$' | sort | uniq | wc -l)`; `lizardfs fileinfo "$file"`; `test_fail "Unknown 'lizardfs getgoal $file' output: $goal"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_TIME`, `CHUNKS_LOOP_MAX_CPU`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_chunk_type_conversion.inc -->
