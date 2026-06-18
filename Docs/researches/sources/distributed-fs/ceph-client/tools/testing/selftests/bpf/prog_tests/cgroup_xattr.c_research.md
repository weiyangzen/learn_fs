# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_xattr.c

## Purpose
Tests BPF cgroup xattr reading helpers and cgroupfs xattr access from tracing programs. It validates both skeleton-driven `RUN_TESTS(cgroup_read_xattr)` coverage and an explicit parent/child cgroupfs xattr scenario.

## Important APIs, types, and functions
Uses `set_cgroup_xattr()`, `test__join_cgroup()`, `read_cgroupfs_xattr.skel.h`, and `cgroup_read_xattr.skel.h`. `test_read_cgroup_xattr()` creates `foo/` and `foo/bar/`, sets `user.bpf_test` xattrs to two values, loads and attaches the skeleton, sets `target_pid`, opens a temp file to trigger hooks, and checks BSS booleans `found_value_a` and `found_value_b`.

## Control flow and state
The test persists xattrs on temporary test cgroups and creates `/tmp/selftests_cgroup_xattr` as a trigger file. All state is cleaned by closing cgroup FDs, destroying the skeleton, and unlinking the temp file.

## Dependencies and integration points
Requires cgroupfs xattr support, generated BPF skeletons, and filesystem operations. It integrates with the selftest runner via `test_cgroup_xattr()`.

## Risks and test signals
Risks include filesystems without cgroup xattr support and trigger hook changes. Positive signals are successful xattr setup, skeleton attach, and both BSS discovery flags set after the file open trigger.
