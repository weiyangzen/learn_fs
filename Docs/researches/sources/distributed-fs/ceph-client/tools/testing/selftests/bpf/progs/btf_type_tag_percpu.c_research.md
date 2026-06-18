<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_percpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_percpu.c

## Purpose

BTF/BTF-dump selftest fixture that contributes source-level type shapes or BPF programs used to validate BTF encoding, C dumping, or type-tag handling.

## Important APIs, Types, and Functions

- BPF sections: `fentry/bpf_testmod_test_btf_type_tag_percpu_1`, `fentry/bpf_testmod_test_btf_type_tag_percpu_2`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `license`
- Important functions/callbacks: `BPF_PROG`, `test_percpu1`, `test_percpu2`, `test_percpu_load`, `test_percpu_helper`
- BPF helpers/kfunc-like calls: `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`
- Mutable globals/test result fields: `g`

## Control Flow and Data Flow

Most files have no runtime flow; they compile C declarations into BTF and expected-output comments. Type-tag files do attach fentry/tp_btf programs that dereference tagged kernel/user/percpu pointers and store simple results.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `g`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with pahole/clang BTF generation, libbpf BTF dump tests, and testmod/fentry targets for type-tag programs where applicable.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `g` to confirm the exercised path ran. BTF dump or BTF load comparison should match embedded expected output or type-tag dereference expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/btf_type_tag_percpu.c -->
