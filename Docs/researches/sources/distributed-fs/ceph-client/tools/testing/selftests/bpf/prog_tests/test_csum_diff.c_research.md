<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_csum_diff.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_csum_diff.c

Purpose: table-driven verifier/runtime coverage for the `bpf_csum_diff()` helper through the `csum_diff_test` skeleton. It checks push, pull, replace/diff, and edge cases over 0, odd, aligned, and full 512-byte buffers with endian-specific expected values.

Important APIs/types/functions: `struct testcase` holds `to_buff`, `from_buff`, byte lengths, seed, and expected checksum. `trigger_csum_diff()` runs `compute_checksum` with `bpf_prog_test_run_opts()`. `test_csum_diff()` mutates skeleton rodata before load, populates BSS buffers after load, and validates `skel->bss->result`. `test_test_csum_diff()` exposes four subtests.

Control flow: each testcase opens a fresh skeleton, writes length constants into rodata, loads the program, copies test data to BSS, sets seed, invokes the BPF program once, and compares the helper result. Fresh skeletons are needed because rodata lengths are load-time constants.

State and persistence: no persistent external state. BSS and rodata are per-skeleton; checksum expectations are static in the C file.

Dependencies and integration: depends on `test_progs.h`, generated `csum_diff_test.skel.h`, libbpf test-run support, and byte-order macros. It integrates with the BPF selftest harness as `test_test_csum_diff`.

Risks: expected values are tightly coupled to helper folding semantics and host endian handling for odd lengths. A failed load short-circuits the current table and destroys only the current skeleton. Edge case with 512 bytes of zero `from_buff` and full length validates kernel behavior on large zero input.

Test signals: `ASSERT_OK_PTR`, `ASSERT_EQ(err, 0)`, and `ASSERT_EQ(got, result)` report load and checksum regressions per subtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_csum_diff.c -->
