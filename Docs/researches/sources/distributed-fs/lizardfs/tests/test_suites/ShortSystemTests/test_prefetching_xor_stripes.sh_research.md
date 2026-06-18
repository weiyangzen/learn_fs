<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_prefetching_xor_stripes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_prefetching_xor_stripes.sh

Purpose: measures XOR stripe prefetch behavior from debug logs to ensure reads do not over-prefetch unnecessary HDD blocks.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `FILE_SIZE`, `BLOCK_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal xor2 .`; `FILE_SIZE=129M BLOCK_SIZE=12345 file-generate file`; `file-validate file`; `assert_less_or_equal "$(grep ^chunkserver.hdd_prefetch_blocks "$TEMP_DIR"/log | wc -l)" "8"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_prefetching_xor_stripes.sh -->
