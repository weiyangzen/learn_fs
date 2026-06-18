<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_overhead.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_overhead.c

Purpose: measures relative event-processing overhead for kprobe, kretprobe, raw tracepoint, fentry, and fexit BPF hooks on task rename events.

Important APIs/types/functions: `test_task_rename()` repeatedly writes to `/proc/self/comm`, `setaffinity()` pins CPU 0, `bpf_object__open_file("./test_overhead.bpf.o")`, program lookup by names `prog1` through `prog5`, and attach helpers for kprobe/raw tracepoint/fentry/fexit.

Control flow: preserve current task comm, open and load the BPF object, find all programs, pin affinity, run a baseline loop, attach each hook type one at a time, run the same rename loop, print K events/sec, destroy the link, restore comm, and close object.

State and persistence: mutates process comm many times and restores the original 16-byte comm at cleanup. No BPF map state is inspected.

Dependencies and integration: depends on `test_overhead.bpf.o` in the working directory, kernel symbol `__set_task_comm`, raw tracepoint `task_rename`, fentry/fexit BTF support, `/proc/self/comm`, and scheduling affinity APIs.

Risks: this is a performance signal, not a deterministic correctness test. CPU frequency, scheduler noise, missing BTF, or symbol naming can alter results. A cleanup path restores comm but does not restore CPU affinity.

Test signals: load/attach assertions catch functional regressions; printed throughput lines are the primary measurement output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_overhead.c -->
