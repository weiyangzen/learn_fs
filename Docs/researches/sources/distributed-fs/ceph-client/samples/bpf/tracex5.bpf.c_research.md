<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex5.bpf.c

## Purpose
`tracex5.bpf.c` demonstrates BPF tail calls by dispatching from a seccomp kprobe to syscall-specific BPF programs based on syscall number.

## Important APIs, Types, And Functions
The `progs` `BPF_MAP_TYPE_PROG_ARRAY` stores syscall-number-to-program entries. Entry program `bpf_prog1()` attaches to `kprobe/__seccomp_filter`. Tail-call targets are generated with `PROG(SYS__NR_write)`, `PROG(SYS__NR_read)`, and optional mmap/mmap2 sections. It uses `bpf_tail_call()`, `bpf_core_read()`, and `bpf_trace_printk()`.

## Control Flow
The seccomp kprobe reads the syscall number from the first argument and tail-calls into `progs[sc_nr]`. If no target exists, it optionally prints a message for get/set uid/pid/gid syscalls. The read/write targets read `struct seccomp_data` from the second argument and print selected calls based on buffer size.

## State And Persistence
Persistent state is the prog-array map populated by userspace after object load. There are no data maps.

## Dependencies And Integration Points
It depends on seccomp being active, kprobe access to `__seccomp_filter`, syscall number definitions from `syscall_nrs.h`, CO-RE reads, and the userspace companion that installs a permissive seccomp filter and populates the prog array.

## Risks And Edge Cases
Kernel internal seccomp symbols and arguments are unstable. Tail-call map sizing is architecture-specific, with a larger value for MIPS. If the prog array is not populated, only fallback prints occur.

## Test Signals
After userspace populates the map and runs `dd`, trace output should include selected read/write or mmap messages from tail-called programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5.bpf.c -->
