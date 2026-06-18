
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_branch_snapshot.c

## Purpose

`get_branch_snapshot.c` verifies `bpf_get_branch_snapshot()`/LBR snapshot behavior for a module function and tracks wasted branch entries.

## Important APIs, Types, and Functions

The file uses `get_branch_snapshot.skel.h`, `perf_event_open` with `PERF_SAMPLE_BRANCH_STACK`, kallsyms lookup for `bpf_testmod_loop_test`, `trigger_module_test_read()`, and helper routines to detect hypervisors and open per-CPU perf events.

## Control Flow and Data Flow

The serial test skips under hypervisors and when no LBR-capable perf event can be opened. It loads the skeleton, sets low/high address bounds around `bpf_testmod_loop_test`, attaches, triggers the module read path, and checks BSS counters for branch entries, hits, and wasted entries.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is per-CPU perf event FDs and BSS counters. Dependencies are LBR branch sampling, non-hypervisor environment, `bpf_testmod`, kallsyms visibility, and perf permissions. Integration is the perf branch stack with BPF branch snapshot helper. Risks include address-range guesswork, module symbol ordering, and variable branch-stack depth. Test signals are at least sixteen entries, more than six hits within the module function range, and fewer than ten wasted entries.
