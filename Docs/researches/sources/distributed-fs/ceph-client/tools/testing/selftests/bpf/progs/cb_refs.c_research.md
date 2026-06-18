<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cb_refs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cb_refs.c

## Purpose

Reference tracking verifier fixture that moves acquired kfunc references through callback paths to test leak/underflow detection.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `?tc`, `?tc`, `?tc`, `?tc`, `license`
- Maps: `array_map`
- Important functions/callbacks: `cb1`, `underflow_prog`, `cb2`, `leak_prog`, `cb`, `cb3`, `nested_cb`, `non_cb_transfer_ref`
- BPF helpers/kfunc-like calls: `bpf_for_each_map_elem`, `bpf_kfunc_call_test_acquire`, `bpf_kfunc_call_test_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `array_map`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `../test_kmods/bpf_testmod_kfunc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_for_each_map_elem`, `bpf_kfunc_call_test_acquire`, `bpf_kfunc_call_test_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `array_map` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cb_refs.c -->
