<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_veristat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_veristat.c

Purpose: black-box tests for the `veristat` command-line tool's `-G` global-variable override parser over scalar, enum, nested struct/union, array, matrix, file-based, and error cases.

Important APIs/types/functions: `struct fixture` holds temp output file, buffer, and veristat path; `init_fixture()` locates `./veristat` or `../veristat`, creates a temp file, and allocates a 1 MB output buffer; `__CHECK_STR` validates expected substrings. Tests invoke `SYS` or `SYS_FAIL`.

Control flow: success test runs `veristat set_global_vars.bpf.o` with many `-G` assignments and checks verbose output for resolved values. File-based test writes assignments to a temp file and passes `-G @file`. Failure tests check out-of-range scalar, pointer array unsupported, array index out-of-bounds, enum index resolution failure, array index on non-array, and missing array index for array/composite traversal.

State and persistence: creates temp files in `/tmp`, reads command output into fixture buffers, and removes temp files during teardown. Does not load BPF into kernel directly; invokes external binary.

Dependencies and integration: depends on `veristat` binary, `set_global_vars.bpf.o`, shell redirection, and exact diagnostic/output strings. Integrated as `test_veristat`.

Risks: strongly coupled to veristat output formatting and working directory layout. `init_fixture()` prints failure if binary is missing but still proceeds with an uninitialized path risk if not caught by harness semantics. Large output buffer is fixed at 1 MB.

Test signals: expected output substrings for successful assignments and expected stderr substrings for parser/type/range failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_veristat.c -->
