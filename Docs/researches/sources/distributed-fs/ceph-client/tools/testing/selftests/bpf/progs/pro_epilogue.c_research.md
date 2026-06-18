<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue.c

## Purpose

Struct_ops selftest for verifier-generated prologue/epilogue behavior around bpf_testmod kfunc callbacks, with syscall probes checking exact arithmetic return values.

## Important APIs, Types, and Functions

Attach sections: license, struct_ops/test_prologue, struct_ops/test_epilogue, struct_ops/test_pro_epilogue, syscall, .struct_ops.link. Map types: none. Important local functions/programs: __kfunc_btf_root, syscall_prologue, syscall_epilogue, syscall_pro_epilogue. Helper and kfunc calls: bpf_kfunc_st_ops_inc10, bpf_kfunc_st_ops_test_epilogue, bpf_kfunc_st_ops_test_pro_epilogue, bpf_kfunc_st_ops_test_prologue. Important structs/types visible in this file: bpf_testmod_st_ops. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf_misc.h, ../test_kmods/bpf_testmod.h, ../test_kmods/bpf_testmod_kfunc.h.

Verifier/test annotations present: __success, __retval(1011), __retval(20022) /* (KFUNC_INC10 + SUBPROG_A [1] + EPILOGUE_A [10000]), __retval(22022) /* (PROLOGUE_A [1000] + KFUNC_INC10 + SUBPROG_A [1] + EPILOGUE_A [10000]). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `__kfunc_btf_root` and related routines such as `syscall_prologue, syscall_epilogue, syscall_pro_epilogue`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, struct_ops/test_prologue, struct_ops/test_epilogue, struct_ops/test_pro_epilogue, syscall, .struct_ops.link` programs, helper coverage for `bpf_kfunc_st_ops_inc10, bpf_kfunc_st_ops_test_epilogue, bpf_kfunc_st_ops_test_pro_epilogue, bpf_kfunc_st_ops_test_prologue`, and stable behavior of `__kfunc_btf_root, syscall_prologue, syscall_epilogue, syscall_pro_epilogue` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue.c -->
