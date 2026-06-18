# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_dev.c

## Purpose
This test validates cgroup device controller BPF program behavior for allowing and denying `mknod`, read, and write operations on device nodes.

## APIs, Types, and Functions
It uses `dev_cgroup.skel.h`, cgroup helpers, `mknod`, `open`, `read`, `write`, `makedev`, `bpf_program__attach_cgroup`, and skeleton BSS/rodata state. Helper routines `test_mknod`, `test_read`, and `test_write` assert return values and errno.

## Control Flow
The test joins a cgroup, loads the device cgroup skeleton, attaches `bpf_prog1`, and runs subtests that set skeleton-side access expectations before performing device operations. It checks allowed mknod/read/write and denied operations, including wrong-device-type behavior.

## State, Dependencies, and Integration
State includes a test cgroup, attached device BPF program, temporary device node paths, and skeleton variables used by the BPF program. It requires privileges for cgroup device hooks and `mknod`.

## Risks and Test Signals
Signals are syscall return values and errno matches. Risks include filesystem/device permission restrictions, missing cgroup device BPF support, and cleanup of created device nodes.
