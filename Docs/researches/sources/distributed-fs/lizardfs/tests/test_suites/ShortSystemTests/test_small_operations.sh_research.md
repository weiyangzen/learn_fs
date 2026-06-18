<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_small_operations.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_small_operations.sh

Purpose: runs many small filesystem operations as a smoke/stress test for ordinary file creation, writes, reads, and metadata updates.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `file-validate`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `BLOCK_SIZE`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `BLOCK_SIZE=$block_size FILE_SIZE=500K file-generate file`; `file-validate file || test_add_failure \`; `FILE_SIZE=70M file-generate file`; `BLOCK_SIZE=$block_size file-validate file || test_add_failure \`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `BLOCK_SIZE`, `FILE_SIZE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_small_operations.sh -->
