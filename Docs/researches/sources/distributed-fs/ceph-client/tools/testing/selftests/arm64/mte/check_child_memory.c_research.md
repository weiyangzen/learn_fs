<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_child_memory.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_child_memory.c

Purpose: verifies MTE tag inheritance and fault behavior across `fork` for anonymous and file-backed mappings.

Important APIs and functions: `check_child_tag_inheritance` forks and has the child write tagged memory, compare tags across granules, and validate underflow/overflow faults. `check_child_memory_mapping` allocates anonymous tagged ranges; `check_child_file_mapping` maps temp files, inserts tags, and reuses inheritance checks.

Control flow: main initializes page-size boundary sizes, sets up MTE and SIGSEGV/SIGBUS handlers, plans 12 tests, and evaluates private/shared mappings for mmap/mprotect and sync/async modes.

State and persistence: temporary memory/file mappings and child processes. Shared `cur_mte_cxt` captures fault state in parent/child contexts. Temp files are created and closed via utilities.

Dependencies and integration: depends on MTE shared utilities, kselftest, fork/wait, and Linux memory mapping behavior.

Risks: several file-memory test labels call `check_child_memory_mapping` instead of `check_child_file_mapping` for async/mprotect cases, so label and behavior may diverge. Async fault timing can vary.

Test signals: child exits encode fault; kselftest failures print child creation, tag mismatch, or unexpected fault diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_child_memory.c -->
