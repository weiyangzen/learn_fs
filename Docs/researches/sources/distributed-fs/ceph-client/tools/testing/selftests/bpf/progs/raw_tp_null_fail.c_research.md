<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/raw_tp_null_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/raw_tp_null_fail.c

## Purpose

Negative nullable raw tracepoint argument test that dereferences trusted_ptr_or_null arguments without the required NULL proof.

## Important APIs, Types, and Functions

Attach sections: license, tp_btf/bpf_testmod_test_raw_tp_null_tp, tp_btf/sched_pi_setprio. Map types: none. Important local functions/programs: test_raw_tp_null_bpf_testmod_test_raw_tp_null_arg_1, test_raw_tp_null_sched_pi_setprio_arg_2. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("R1 invalid mem access 'trusted_ptr_or_null_'"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `test_raw_tp_null_bpf_testmod_test_raw_tp_null_arg_1` and related routines such as `test_raw_tp_null_sched_pi_setprio_arg_2`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, tp_btf/bpf_testmod_test_raw_tp_null_tp, tp_btf/sched_pi_setprio` programs, helper coverage for `none`, and stable behavior of `test_raw_tp_null_bpf_testmod_test_raw_tp_null_arg_1, test_raw_tp_null_sched_pi_setprio_arg_2` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/raw_tp_null_fail.c -->
