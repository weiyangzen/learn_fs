<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_truncates.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_truncates.sh

Purpose: compares repeated truncation and append behavior between local files and LizardFS files across standard and XOR goals and multiple boundary sizes.

Important APIs, functions, and commands: defines `verify_truncate`, `verify_append`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `file-generate`, `truncate`, `assert_success`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=$chunk file-generate "$real_file"`; `lizardfs setgoal "$goal" "file_$goal"`; `FILE_SIZE=$chunk file-generate "file_$goal"`; `verify_truncate() {`; `export MESSAGE="Veryfing truncate -s $size"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`, `MESSAGE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_truncates.sh -->
