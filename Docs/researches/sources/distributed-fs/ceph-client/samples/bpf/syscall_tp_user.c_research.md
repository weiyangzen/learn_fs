# sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_user.c

Purpose: userspace test harness for syscall tracepoint BPF counters.

Important APIs/types/functions: `usage`, `verify_map`, `test`, and `main`. Uses libbpf object load/attach APIs, map lookups, and repeated `open` calls against a filename.

Control flow: parses number of parallel test objects, loads and attaches the BPF object(s), performs controlled `open` syscalls, then verifies each map counter against expected values.

State and persistence: BPF objects, links, and maps live during test execution. Test files are opened and closed by the process.

Dependencies and integration: pairs with `syscall_tp_kern.c`, requires syscall tracepoints and libbpf.

Risks: concurrent system activity can add open syscalls and disturb counts if tracepoints are global and maps are not filtered. Multiple loaded objects multiply event counts.

Test signals: `verify_map` succeeds for configured `nr_tests`; failures indicate attach/load/count mismatches.
