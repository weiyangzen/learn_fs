
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stack_raw_tp.c

## Purpose

`get_stack_raw_tp.c` validates stack collection helpers from a raw tracepoint program, including raw address stacks and build-id stack data.

## Important APIs, Types, and Functions

The test loads `test_get_stack_rawtp.bpf.o` and expected-fail `test_get_stack_rawtp_err.bpf.o`, attaches to raw tracepoint `sys_enter`, uses a perf buffer map, and decodes `struct get_stack_trace_t`. It uses `load_kallsyms()`, `ksym_search()`, CPU affinity, `nanosleep()` triggers, and `perf_buffer__poll()`.

## Control Flow and Data Flow

The harness first asserts the erroneous object cannot load, then loads the valid raw tracepoint object, finds program and perf map, pins itself to CPU 0, attaches to `sys_enter`, creates a perf buffer, triggers ten syscalls, and polls until expected events arrive. The callback checks kernel stack sanity by symbol name when JIT is disabled or non-empty stacks when JIT is enabled, and validates user stack/build-id sizes.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes a raw tracepoint link, perf buffer events, and kallsyms cache. Dependencies are raw tracepoints, stack walking, build-id support, perf buffer delivery, and CPU affinity. Integration is BPF stack helper output format and perf event transport. Risks are JIT-dependent symbol validation, missing kallsyms, fewer events than expected, and stack walking limitations. Test signals are expected load failure for the bad object, valid perf samples, non-corrupt kernel stack, and user stack/build-id data present.
