# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arg_parsing.c

Purpose: unit tests for selftest command-line/filter parsing helpers, covering test lists, subtest filters, wildcard wrapping, duplicate coalescing, comments, whitespace, and files without final newlines.

Important APIs/types/functions: local `init_test_filter_set` and `free_test_filter_set` manage `struct test_filter_set`. `test_parse_test_list` calls `parse_test_list`; `test_parse_test_list_file` writes a temporary file and calls `parse_test_list_file`.

Control flow: list parsing tests build filter strings such as `arg_parsing,bpf_cookie`, `test/subtest`, repeated calls into the same set, non-exact wildcard mode, and duplicate subtest aggregation. File parsing creates `/tmp/bpf_arg_parsing_test.XXXXXX`, writes comments/duplicates/inline comments/no-EOF-newline records, syncs the file, parses it, and validates the resulting ordered filter set.

State and persistence behavior: parsed filters allocate test names and subtest name arrays, then `free_test_filter_set` releases them. The temporary file is removed at the end. No persistent repository state is touched.

Dependencies and integration points: depends on `test_progs.h`, `testing_helpers.h`, libc temp-file APIs, and the shared test filter parser used by the selftest runner.

Risks: temporary file path is under `/tmp`; failures before cleanup can leave a file. Assertions use `strcmp` wrapped in `ASSERT_OK`, so equality is represented by zero.

Test signals: exact counts, names, subtest counts, duplicate suppression, wildcard formatting in non-exact mode, and parser success on trimmed/commented file input.
