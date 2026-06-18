<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate.sh

Purpose: validates truncate and append behavior around block and chunk boundaries for standard and XOR goals.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `find_all_chunks`, `file-generate`, `file-validate`, `truncate`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `find_all_chunks | xargs rm -f`; `lizardfs_chunkserver_daemon $i restart`; `lizardfs_wait_for_all_ready_chunkservers`; `mkdir -p tmp;`; `lizardfs setgoal $goal tmp`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate.sh -->
