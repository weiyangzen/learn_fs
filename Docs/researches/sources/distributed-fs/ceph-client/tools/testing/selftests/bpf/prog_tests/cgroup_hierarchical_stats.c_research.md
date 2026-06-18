# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_hierarchical_stats.c

## Purpose
This integration test validates hierarchical aggregation of cgroup attach counters using BPF iterators pinned in bpffs. It creates a cgroup tree, attaches processes to leaf cgroups, dumps counters through cgroup iter links, and checks parent totals.

## APIs, Types, and Functions
It uses bpffs mount helpers (`mount`, `umount`, path removal), cgroup helpers, `fork`/`waitpid`, `bpf_program__attach_iter`, `bpf_link__pin`, file reads, and `cgroup_hierarchical_stats.skel.h`. Important helpers include `setup_bpffs`, `setup_cgroups`, `attach_processes`, `setup_cgroup_iter`, `setup_progs`, and `check_attach_counters`.

## Control Flow
The test prepares bpffs and a fixed cgroup hierarchy, opens/loads the skeleton, creates one cgroup iterator link per cgroup plus root with `BPF_CGROUP_ITER_SELF_ONLY`, pins links under bpffs, attaches the BPF programs, forks child processes to join leaf cgroups, reads generated files, parses `cg_id` and `attach_counter`, and validates leaf counts and parent sums.

## State, Dependencies, and Integration
State includes mounted bpffs, pinned BPF iterator links, cgroup hierarchy, child process joins, generated bpffs files, and skeleton links. Cleanup removes pinned files, destroys skeletons, closes cgroup FDs, and unmounts bpffs when mounted by the test.

## Risks and Test Signals
Signals are parsed file format, nonzero counters, exact leaf count of three, parent-child sum equality, and root lower-bound checks. Risks are bpffs mount permissions, cgroup process accounting timing, fork failures, and stale pinned files.
