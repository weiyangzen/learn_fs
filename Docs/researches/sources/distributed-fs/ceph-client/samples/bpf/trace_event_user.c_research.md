<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/trace_event_user.c

## Purpose
`trace_event_user.c` is the userspace driver for the perf-event stack trace sample. It attaches the BPF program to several hardware, software, cache, raw, and precise perf events in all-CPU and inherited task modes, generates load, prints stack aggregates, and validates expected syscall stack content.

## Important APIs, Types, And Functions
Important routines are `print_ksym()`, `print_stack()`, `print_stacks()`, `generate_load()`, `test_perf_event_all_cpu()`, `test_perf_event_task()`, `test_bpf_perf_event()`, and `main()`. It uses `sys_perf_event_open()`, `bpf_program__attach_perf_event()`, `bpf_map_get_next_key()`, `bpf_map_lookup_elem()`, `bpf_map_delete_elem()`, `load_kallsyms()`, and `read_trace_pipe()`.

## Control Flow
Startup loads kallsyms and the BPF object, resolves `counts` and `stackmap`, forks a trace-pipe reader, then runs a suite of perf events. Each all-CPU test opens a perf event per CPU and attaches the program; each task test opens an inherited event for the process. After running `dd`, it prints and clears count and stack maps, checking that read/write kernel stack symbols were observed.

## State And Persistence
State includes perf event fds, BPF links, two map fds, a child trace-pipe reader process, and transient stack/count data. Maps are cleared between test iterations.

## Dependencies And Integration Points
It depends on libbpf, perf_event_open permissions, kallsyms access, `dd`, signal handling, and the kernel sample object. Some raw event configs are CPU-model specific.

## Risks And Edge Cases
Raw events such as Intel instruction retired and lock load may not exist on all CPUs or virtual machines. The symbol checks appear inverted in `print_ksym()` due to `!strstr()` logic and may make the sample fragile. `err_exit()` kills the child and exits, so cleanup is abrupt.

## Test Signals
The suite prints each tested perf event name and ends with `*** PASS ***` if stack maps are populated and expected syscall stack evidence is found. Failures include perf open errors, missing maps, empty stack results, or missing syscall symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_user.c -->
