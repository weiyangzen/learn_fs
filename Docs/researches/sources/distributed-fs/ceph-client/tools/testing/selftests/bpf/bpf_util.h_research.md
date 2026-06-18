# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_util.h

Purpose: common user-space utility header for BPF selftests.

Important APIs and macros: `bpf_num_possible_cpus()` wraps `libbpf_num_possible_cpus()` with fatal error handling; `sized_strscpy()` and variadic `strscpy` macro provide bounded string copy; per-CPU value helpers `BPF_DECLARE_PERCPU` and `bpf_percpu`; `ARRAY_SIZE`, `sizeof_field`, `offsetofend`, `sys_gettid()`, and `ENOTSUPP` fallback.

Control flow: utility inline functions perform immediate checks/copies. `#pragma GCC poison gettid` forces tests to use the syscall fallback macro.

State and persistence: no persistent state.

Dependencies and integration points: includes libbpf, Linux args macro helpers, errno/syscall headers, and is included by many user-space test files.

Risks: `strscpy` macro depends on argument-count helpers; `bpf_num_possible_cpus()` exits the process on error; poisoning `gettid` can surprise includers.

Test signals: users should compile with the helper macros and correctly size per-CPU value arrays for map APIs.
