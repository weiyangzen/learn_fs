# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_metadata.c

## Purpose
This selftest validates bpftool display of BPF program metadata stored in a `.rodata` metadata map. It covers both unused and used metadata fixtures and checks default and JSON output formats.

## Important APIs, Types, And Functions
Important elements are `struct test_desc`, static `tests[]`, `setup()`, `cleanup()`, `check_metadata()`, `run_test()`, and `test_bpftool_metadata()`. It uses `run_bpftool_command()`, `get_bpftool_command_output()`, bpffs program pinning, `prog load`, `prog show pinned`, `prog -j show pinned`, and `map show name`.

## Control Flow
For each fixture, the entry point creates `/sys/fs/bpf/test_metadata`, loads the BPF object to a pinned bpffs path using bpftool, checks human-readable `prog show` output for expected tokens, checks JSON output for the compact metadata JSON token, verifies the metadata map can be found by name, then unlinks the pin and removes the directory.

## State And Persistence Behavior
State is limited to a temporary bpffs directory, one pinned program path per subtest, static output buffer storage, and the metadata map created by loading the object. Cleanup removes the program pin and directory after each subtest.

## Dependencies And Integration Points
It depends on bpftool command helpers, bpffs, the object files `metadata_unused.bpf.o` and `metadata_used.bpf.o`, and bpftool's metadata rendering for maps named `metadata.rodata`. It integrates BPF object metadata generation with bpftool display and map discovery.

## Risks And Edge Cases
The token checks are substring-based and sensitive to formatting in bpftool output, especially JSON compactness. The setup function ignores its `test` parameter and uses a fixed directory, so stale directories from interrupted runs can cause setup failure. Output larger than 64 KiB would be truncated.

## Test Signals
Passing signals are successful bpffs directory creation, successful program load and pin, expected default-format metadata tokens for `a` and `b`, expected JSON metadata token, successful map lookup by metadata map name, and cleanup of the pinned path and directory.
