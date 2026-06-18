<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex5_user.c

## Purpose
`tracex5_user.c` loads the tail-call seccomp tracing sample, populates the program array with syscall-specific programs, enables a permissive seccomp filter, generates I/O, and reads trace output.

## Important APIs, Types, And Functions
Key functions are `install_accept_all_seccomp()` and `main()`. It uses classic BPF seccomp filter structures, `prctl(PR_SET_SECCOMP)`, libbpf object/program APIs, `bpf_map_update_elem()`, `bpf_program__section_name()`, `bpf_program__fd()`, `popen()`, and `read_trace_pipe()`.

## Control Flow
The program loads `<argv[0]>.bpf.o`, attaches `bpf_prog1`, finds the `progs` prog-array map, iterates all programs, parses syscall numbers from sections named `kprobe/<number>`, inserts program fds into the map, installs an allow-all seccomp filter, runs `dd`, and streams trace output.

## State And Persistence
The prog array persists while the object is loaded and maps syscall numbers to tail-call targets. The process also enters seccomp mode for the remainder of execution.

## Dependencies And Integration Points
It depends on libbpf, seccomp, the companion BPF object, `dd`, and tracefs. It integrates classic seccomp activation with eBPF kprobe observation of the seccomp path.

## Risks And Edge Cases
Once seccomp is installed it cannot be undone. Section parsing assumes numeric section names for tail-call targets. The trace read is long-running and `popen()` is not closed explicitly.

## Test Signals
Expected behavior is trace output from read/write tail-call programs after the `dd` workload, with no failures populating the prog array.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5_user.c -->
