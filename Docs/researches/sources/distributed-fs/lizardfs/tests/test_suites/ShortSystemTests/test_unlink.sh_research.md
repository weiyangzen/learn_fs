<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_unlink.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_unlink.sh

Purpose: tests unlink behavior for open files, replicated chunks, and metadata cleanup.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_all_chunks`, `dd`, `lizardfs {setgoal, settrashtime}`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal 3 "$file"`; `lizardfs setgoal xor3 "$xorfile"`; `lizardfs settrashtime 0 "$file" "$xorfile"`; `rm -f "$file" "$xorfile"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_unlink.sh -->
