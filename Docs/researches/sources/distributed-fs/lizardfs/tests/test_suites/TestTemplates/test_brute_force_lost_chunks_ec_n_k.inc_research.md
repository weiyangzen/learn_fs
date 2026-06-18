<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_brute_force_lost_chunks_ec_n_k.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_brute_force_lost_chunks_ec_n_k.inc

Purpose: template include that brute-forces lost data/parity part combinations for an EC(n,k) goal and validates that each selected failure pattern remains readable or fails as intended.

Important APIs, functions, and commands: defines `get_ec_chunk_part_from_filename`, `iteration`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_chunkserver_chunks`, `file-generate`, `file-validate`, `assert_eventually`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`, `MASTER_CUSTOM_GOALS`, `FILE_SIZE`, `BLOCK_SIZE`.

Control flow: The script proceeds through these visible steps: `assert_program_installed python3 tee`; `local lost_chunkservers=`; `lost_chunkservers="${lost_chunkservers} ${chunkservers[$chunk]}"`; `echo "Losing chunkservers: $lost_chunkservers"`; `for chunkserver in $lost_chunkservers; do`; `assert_eventually "lizardfs_chunkserver_daemon $chunkserver isalive" "100 seconds"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `python3`, `tee`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; lock tests risk stale owners or blocked helper processes; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_brute_force_lost_chunks_ec_n_k.inc -->
