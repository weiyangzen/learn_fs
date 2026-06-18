<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stream_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stream_fail.c

## Purpose

Negative stream_vprintk verifier tests for NULL, scalar, and non-constant string arguments.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: stream_vprintk_null_arg, stream_vprintk_scalar_arg, stream_vprintk_string_arg. Helper and kfunc calls: bpf_stream_vprintk. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("Possibly NULL pointer passed"), __msg("R3 type=scalar expected="), __msg("arg#1 doesn't point to a const string"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `stream_vprintk_null_arg` and related routines such as `stream_vprintk_scalar_arg, stream_vprintk_string_arg`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_stream_vprintk`, and stable behavior of `stream_vprintk_null_arg, stream_vprintk_scalar_arg, stream_vprintk_string_arg` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stream_fail.c -->
