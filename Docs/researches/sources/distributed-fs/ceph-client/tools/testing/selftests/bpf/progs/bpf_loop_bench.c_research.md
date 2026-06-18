<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop_bench.c

## Purpose

BPF benchmark or verifier fixture for loop/map behavior, focusing on helper bounds, callback execution, map update/lookup cost, and stack safety.

## Important APIs, Types, and Functions

- BPF sections: `license`
- Important functions/callbacks: `empty_callback`, `outer_loop`, `benchmark`
- BPF helpers/kfunc-like calls: `bpf_loop`
- Mutable globals/test result fields: `nr_loops`, `hits`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `nr_loops`, `hits`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_loop`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nr_loops`, `hits` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop_bench.c -->
