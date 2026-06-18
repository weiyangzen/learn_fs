<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_strncmp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_strncmp.c

Purpose: validates accepted and rejected uses of the BPF `bpf_strncmp()` helper, including return ordering semantics and verifier constraints around constant size and read-only null-terminated target strings.

Important APIs/types/functions: `trigger_strncmp()` waits for the attached program to update `cmp_ret` and normalizes sign; `strncmp_full_str_cmp()` mutates every character against rodata `target`; `test_strncmp_ret()` runs positive comparisons; three negative subtests enable bad programs and expect load failure.

Control flow: positive path opens skeleton, autoloads `do_strncmp`, loads/attaches, sets `target_pid`, checks empty string, equal string, non-null-terminated local string, and per-position less/greater comparisons. Negative paths open new skeletons, autoload one invalid program each, load, and expect an error.

State and persistence: BSS string buffer, target pid, and comparison result are transient per skeleton. Uses rodata target as immutable comparison string.

Dependencies and integration: depends on generated `strncmp_test.skel.h`, helper availability, and the attach trigger used by the BPF program. Integrated as `test_test_strncmp`.

Risks: `usleep(1)` assumes the program has run after BSS mutation. Negative verifier diagnostics are not checked, only load failure. String array sizes and null termination are central to correctness.

Test signals: comparison result assertions for many character positions and `ASSERT_ERR` load failures for non-constant size, writable target, and non-null-terminated target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_strncmp.c -->
