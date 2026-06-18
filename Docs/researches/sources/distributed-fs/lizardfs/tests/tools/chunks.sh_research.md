<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/chunks.sh -->
# sources/distributed-fs/lizardfs/tests/tools/chunks.sh

Purpose: provides LizardFS test harness coverage for chunks.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `goal_to_part_count`, `filesize_to_chunk_count`, `redundant_parts`, `minimum_number_of_parts`, `check_one_file_part_coverage`, and `check_one_file_replicated` encode chunk-count and replication expectations.

Control flow: The script proceeds through these visible steps: `local goal="$(lizardfs getgoal "${path}" | awk '{print $2}')"`; `local fileinfo="$(lizardfs fileinfo ${path})"`; `assert_eventually 'check_one_file_part_coverage_impl_ "${path}" "${expected_number_of_parts}"' "${replication_timeout}"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: LizardFS CLI/test helpers.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/chunks.sh -->
