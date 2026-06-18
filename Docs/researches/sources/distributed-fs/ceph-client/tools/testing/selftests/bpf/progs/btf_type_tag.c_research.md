<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- BPF sections: `fentry/bpf_fentry_test1`
- Important functions/callbacks: `BPF_PROG`, `sub`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture.

## Test Signals

Load/attach success and verifier log expectations are primary signals. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag.c -->
