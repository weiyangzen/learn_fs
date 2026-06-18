# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_raw_tp.c

Purpose: raw tracepoint version of stack map key consistency testing. It loads `stacktrace_map.bpf.o` as `BPF_PROG_TYPE_RAW_TRACEPOINT`, attaches program `oncpu` to `sched_switch`, and validates map relationships after a short run.

Control flow uses `bpf_prog_test_load`, finds the program by name, attaches raw tracepoint link, locates maps with `bpf_find_map`, sleeps, writes `control_map[0]=1`, then compares keys between `stackid_hmap` and `stackmap` in both directions. State includes the raw tracepoint link, generic `bpf_object`, three map fds, and control flag. Dependencies are `sched_switch` raw tracepoint availability and helper comparison functions. Risks are failure to find maps by name, no events during sleep, and cleanup if attach or map discovery fails. Test signals are raw tracepoint attach success and bidirectional map key comparison success.
