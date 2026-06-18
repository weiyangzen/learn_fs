# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.h

## Purpose

This header defines shared XDP ping limits and the map value used by the XDP ping client/server programs and userspace runner.

## Important APIs, Types, and Functions

It defines `XDPING_MAX_COUNT` as `10`, `XDPING_DEFAULT_COUNT` as `4`, and `struct pinginfo` with `start`, network-order `seq`, `count`, padding, and `times[XDPING_MAX_COUNT]` nanosecond RTT samples.

## Control Flow

No executable flow exists here. Userspace seeds `seq` and `count`, the BPF program records start/time samples, and userspace later iterates `times[]` until `count` samples are present.

## State and Persistence Behavior

Instances persist only as BPF map values keyed by remote IPv4 address for the duration of an xdping run.

## Dependencies and Integration Points

It is shared by `xdping.c` and the companion kernel BPF object. Its layout is an ABI between userspace and BPF.

## Risks and Test Signals

Risks include count larger than the array, endian mismatch for `seq`, and layout drift between userspace and BPF builds. Signals are populated `times[]` values and successful BPF map lookup/delete.
