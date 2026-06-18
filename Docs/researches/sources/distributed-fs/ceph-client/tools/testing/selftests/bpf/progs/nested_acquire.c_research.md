<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_acquire.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_acquire.c

## Purpose

Positive kfunc acquisition test that calls nested acquire/release test kfuncs from tcp_probe tracepoints and validates zero-offset and nonzero-offset nested object acquisition.

## Important APIs, Types, and Functions

Attach sections: license, tp_btf/tcp_probe. Map types: none. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_kfunc_nested_acquire_nonzero_offset_test, bpf_kfunc_nested_acquire_zero_offset_test, bpf_kfunc_nested_release_test. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h, ../test_kmods/bpf_testmod_kfunc.h.

Verifier/test annotations present: __success. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, tp_btf/tcp_probe` programs, helper coverage for `bpf_kfunc_nested_acquire_nonzero_offset_test, bpf_kfunc_nested_acquire_zero_offset_test, bpf_kfunc_nested_release_test`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_acquire.c -->
