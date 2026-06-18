# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_get_current_cgroup_id.c

## Purpose
This file validates `bpf_get_current_cgroup_id` from a cgroup-attached program by comparing the BPF-observed ID with the user-space cgroup ID.

## APIs, Types, and Functions
It uses `get_cgroup_id_kern.skel.h`, `cgroup_setup_and_join`, `get_cgroup_id`, `bpf_program__attach_cgroup`, and a device operation trigger through `mknod`/`makedev` headers included for the underlying test path.

## Control Flow
The test creates and joins a test cgroup, loads the skeleton, attaches its cgroup program, triggers the hook, and asserts that the ID written by the BPF program matches `get_cgroup_id` for the current cgroup.

## State, Dependencies, and Integration
State is the cgroup membership and skeleton BSS result. Cleanup destroys the skeleton and cgroup environment. It depends on cgroup setup helpers and cgroup ID visibility.

## Risks and Test Signals
The signal is exact cgroup ID equality. Risks are mostly environmental: inability to create/join the cgroup, missing attach support, or a trigger path that does not execute the program.
