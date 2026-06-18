<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_test_utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_test_utils.h

## Purpose

BPF selftest support source in the kernel selftests BPF program tree.

## Important APIs, Types, and Functions

- Important functions/callbacks: `clobber_regs_stack`
- BPF helpers/kfunc-like calls: `bpf_strtoul`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_strtoul`.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_test_utils.h -->
