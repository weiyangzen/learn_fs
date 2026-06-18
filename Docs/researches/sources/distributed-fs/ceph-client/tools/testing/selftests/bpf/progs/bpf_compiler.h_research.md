<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_compiler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_compiler.h

## Purpose

Compiler-attribute compatibility header used by BPF selftest sources to express inline, weak, used, and other compiler-specific annotations.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Integrated through the kernel BPF selftest build and libbpf skeleton loading path.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_compiler.h -->
