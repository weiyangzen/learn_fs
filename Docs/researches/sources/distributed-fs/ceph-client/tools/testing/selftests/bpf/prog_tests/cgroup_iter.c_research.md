# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter.c

## Purpose
This file tests cgroup BPF iterator traversal modes and parameter validation. It verifies preorder, postorder, ancestor-up, self-only, children-only, early termination, invalid cgroup specs, dead cgroup handling, and CSS task iteration.

## APIs, Types, and Functions
It uses `cgroup_iter.skel.h`, `iters_css_task.skel.h`, `bpf_program__attach_iter`, `bpf_iter_create`, `read`, `union bpf_iter_link_info`, cgroup helpers, and `kern_sync_rcu`. Static arrays track cgroup paths, FDs, IDs, and expected output text.

## Control Flow
Setup creates root, parent, and child cgroups and records IDs. `read_from_cgroup_iter` attaches an iterator with requested order, reads output, and compares with `expected_output`. Subtests cover invalid fd/id combinations, traversal orders, terminal-cgroup early termination, self-only output, children output, and reading an iterator after its target cgroup has been removed. The CSS task subtest loads a separate skeleton and verifies the current PID's CSS task count.

## State, Dependencies, and Integration
State includes cgroup hierarchy, iterator links and FDs, skeleton BSS controls such as `terminal_cgroup` and `terminate_early`, and expected string buffers. Cleanup destroys skeletons and cgroup environment.

## Risks and Test Signals
Signals are exact iterator output strings, expected attach errors, and CSS task count. Risks include RCU timing for dead cgroups, formatting changes in iterator programs, and environment support for cgroup iterators.
