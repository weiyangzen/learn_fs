# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup1_hierarchy.c

## Purpose
This test validates BPF cgroup ancestor checks for cgroup v1 hierarchies, using LSM programs triggered by fentry attachment. It covers correct ancestor ID/hierarchy ID, root cgroup ID behavior, sleepable LSM behavior, and invalid ID handling.

## APIs, Types, and Functions
It uses `test_cgroup1_hierarchy.skel.h`, `setup_cgroup_environment`, `setup_classid_environment`, `join_classid`, `get_classid_cgroup_id`, `get_cgroup1_hierarchy_id`, `bpf_program__set_attach_target`, `bpf_program__attach_lsm`, and `bpf_program__attach_trace`. Helpers are `bpf_cgroup1`, `bpf_cgroup1_sleepable`, and `bpf_cgroup1_invalid_id`.

## Control Flow
The test opens the skeleton, sets `target_pid`, retargets fentry to `bpf_fentry_test1`, loads, sets up cgroup v1 net_cls hierarchy, joins it, records current cgroup and hierarchy IDs in BSS, and runs subtests. Normal and root cases expect the LSM program to block the fentry attach. The invalid-ID case expects fentry attach success because the ancestor condition should not match.

## State, Dependencies, and Integration
State includes cgroup v1/classid setup, current process membership, skeleton BSS fields, and transient LSM/fentry links. Cleanup tears down cgroup environments. It depends on cgroup v1 net_cls availability and BPF LSM/fentry support.

## Risks and Test Signals
Signals are attach success or failure in the expected direction and link destroy success. Environment risk is high on systems without cgroup v1 net_cls or required BPF attach capabilities.
