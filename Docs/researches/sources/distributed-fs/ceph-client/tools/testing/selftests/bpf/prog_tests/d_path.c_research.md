# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/d_path.c

## Purpose
Tests `bpf_d_path` helper behavior for stat/close hooks, verifier rejection of wrong memory/type usage, and verifier-generated memory access after helper writes.

## Important APIs, types, and functions
Uses `test_d_path.skel.h`, `test_d_path_check_rdonly_mem.skel.h`, `test_d_path_check_types.skel.h`, `readlink("/proc/<pid>/fd/<fd>")`, `close_range` syscall wrapper, and file/socket/pipe triggers. `trigger_fstat_events()` opens pipe, socket, proc, dev, deleted temp file, and `/tmp` O_PATH, records expected paths, stats/closes them. `attach_and_load()` loads/attaches and sets BSS `my_pid`.

## Control flow and state
`test_d_path()` runs basic path comparison, two negative load tests, and memory-access test. Basic subtest compares BPF-captured `paths_stat` and `paths_close` plus return lengths to user-space `src.paths`. Memory-access subtest creates a deleted shm file and expects BPF to match fallocate path. State includes global expected path array, temporary files, open FDs, and skeleton BSS arrays/flags.

## Dependencies and integration points
Requires BPF trampolines/hooks for `security_inode_getattr` and `filp_close`, procfs/dev/tmp availability, close_range syscall number fallback, and helper verifier support. Integrated through subtests.

## Risks and test signals
Path strings can vary by filesystem or deleted-file formatting. Passing signals are hooks called, every expected path equal for stat and close, helper return lengths include NUL, negative skeletons rejected, and memory-access path match set.
