<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.c

## Purpose
`testing_helpers.c` implements common user-space helpers for BPF selftests: numeric and test-name filter parsing, BPF object/program loading with test flags, kernel module load/unload wrappers, RCU synchronization trigger, translated-program retrieval, perf sample-rate reading, and BPF JIT detection.

## Important APIs, Types, And Functions
- `parse_num_list()` parses comma/range expressions into boolean selection sets.
- `parse_test_list()` and `parse_test_list_file()` populate `struct test_filter_set`, using `insert_test()` and `do_insert_test()` for test/subtest patterns.
- `link_info_prog_id()` returns the attached program ID for a libbpf link fd.
- `testing_prog_flags()` probes and caches supported test flags `BPF_F_TEST_RND_HI32` and `BPF_F_TEST_REG_INVARIANTS`.
- `bpf_prog_test_load()` opens a BPF object, sets program type/flags, loads it, and returns object plus first program fd.
- `bpf_test_load_program()` wraps `bpf_prog_load()` for raw instruction arrays.
- Module helpers wrap `finit_module`, `delete_module`, load/unload module by path/name, and specifically load/unload `bpf_testmod.ko`.
- `kern_sync_rcu()` uses `membarrier`, `get_xlated_program()` reads rewritten BPF instructions, and `is_jit_enabled()` reads `/proc/sys/net/core/bpf_jit_enable`.

## Control Flow
Parsing helpers allocate or grow arrays as they consume comma-separated input or file lines. Loading helpers configure libbpf options, probe flags once, then propagate errors to callers. Module unload first triggers kernel-side RCU synchronization and retries `delete_module()` on `EAGAIN`. Translated program retrieval performs a two-step `bpf_prog_get_info_by_fd()` to get size then fetch instructions.

## State And Persistence
The file maintains global `extra_prog_load_log_flags` and a static cached flag mask in `testing_prog_flags()`. Kernel-persistent effects include loaded BPF programs, loaded/unloaded modules, and membarrier-triggered synchronization. Allocated filter strings are owned by the caller's selector cleanup.

## Dependencies And Integration Points
It depends on libbpf, `test_progs.h`, `disasm.h`, Linux membarrier, module syscalls, and BPF syscall APIs. It is used by `test_progs.c`, `test_verifier.c`, and many standalone BPF test harnesses.

## Risks And Edge Cases
`parse_num_list()` uses `realloc(set, new_len)` for bool bytes, which relies on `sizeof(bool)==1`. `parse_test_list_file()` treats a line with only one nonspace character carefully; parser bugs can affect runner filtering. Module load/unload requires privileges and can fail if the module is absent or busy. Cached test flags assume support does not change during the process.

## Test Signals
Helper regressions show as filter parse errors, missing selected tests, BPF object load failures, verifier translated-program checks failing, inability to load `bpf_testmod.ko`, or incorrect skip behavior when JIT/test flags are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.c -->
