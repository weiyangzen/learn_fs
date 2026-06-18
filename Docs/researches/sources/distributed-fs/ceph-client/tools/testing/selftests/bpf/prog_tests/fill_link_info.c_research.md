
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fill_link_info.c

## Purpose

`fill_link_info.c` validates that `bpf_link_get_info_by_fd()` fills complete, type-specific metadata for perf-event links, kprobe-multi links, and uprobe-multi links. It is a user-space BPF selftest harness around `test_fill_link_info.skel.h`; the BPF programs are mostly inert trigger/attachment targets while the host test stresses link-info ABI behavior.

## Important APIs, Types, and Functions

The test centers on `struct bpf_link_info`, `bpf_link_get_info_by_fd()`, `bpf_program__attach_kprobe_opts()`, `bpf_program__attach_tracepoint_opts()`, `bpf_program__attach_perf_event_opts()`, `bpf_program__attach_uprobe_opts()`, `bpf_program__attach_kprobe_multi_opts()`, and `bpf_program__attach_uprobe_multi()`. It uses `bpf_kprobe_opts`, `bpf_tracepoint_opts`, `bpf_perf_event_opts`, `bpf_uprobe_opts`, `bpf_kprobe_multi_opts`, and `bpf_uprobe_multi_opts` with cookies, return-probe flags, symbol arrays, address arrays, and ref-counter offsets. `trace_helpers.h` supplies kallsyms and ELF symbol resolution helpers.

## Control Flow and Data Flow

`test_fill_link_info()` loads the skeleton, loads kallsyms, resolves `bpf_fentry_test1`, resolves local uprobe offsets, sorts kprobe-multi symbols, and runs subtests. Verification helpers first query only fixed-size fields, then repeat with user buffers for variable-length strings, address arrays, cookie arrays, path buffers, and ref-counter offsets. Negative helpers deliberately pass bad user pointers, missing counts, undersized arrays, and invalid lengths to assert `-EINVAL`, `-EFAULT`, or `-ENOSPC`.

## State, Dependencies, Integration Points, Risks, and Test Signals

The only persistent state is live link lifetime and the pinned kernel-side link metadata reachable through the FD; all links are destroyed before return. The test depends on perf events, tracepoints, kprobes, uprobes, kprobe-multi, uprobe-multi, kallsyms visibility, executable ELF symbols, and architecture-specific kprobe entry offsets for x86 IBT and PPC64 ftrace. Integration is the libbpf/kernel link-info ABI. Risks are kptr restrictions hiding addresses, architecture entry offset drift, missing perf/kprobe features, and exact errno regressions. Strong test signals are successful metadata round-trips for kprobe/kretprobe/tracepoint/uprobe/uretprobe/perf-event/kprobe-multi/uprobe-multi plus failure of invalid-buffer probes without corrupting zeroed fields.
