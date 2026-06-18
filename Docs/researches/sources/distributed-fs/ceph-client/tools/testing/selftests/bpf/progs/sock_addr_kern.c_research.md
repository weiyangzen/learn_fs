<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_addr_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_addr_kern.c

## Purpose

Syscall BPF kfunc wrapper suite for kernel socket operations such as init, bind, connect, listen, sendmsg, getsockname, getpeername, and close.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: init_sock, close_sock, kernel_connect, kernel_bind, kernel_listen, kernel_sendmsg, sock_sendmsg, kernel_getsockname, kernel_getpeername. Helper and kfunc calls: bpf_kfunc_call_kernel_bind, bpf_kfunc_call_kernel_connect, bpf_kfunc_call_kernel_getpeername, bpf_kfunc_call_kernel_getsockname, bpf_kfunc_call_kernel_listen, bpf_kfunc_call_kernel_sendmsg, bpf_kfunc_call_sock_sendmsg, bpf_kfunc_close_sock, bpf_kfunc_init_sock. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, ../test_kmods/bpf_testmod_kfunc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `init_sock` and related routines such as `close_sock, kernel_connect, kernel_bind, kernel_listen`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_kfunc_call_kernel_bind, bpf_kfunc_call_kernel_connect, bpf_kfunc_call_kernel_getpeername, bpf_kfunc_call_kernel_getsockname, bpf_kfunc_call_kernel_listen, bpf_kfunc_call_kernel_sendmsg, bpf_kfunc_call_sock_sendmsg, bpf_kfunc_close_sock, and 1 more`, and stable behavior of `init_sock, close_sock, kernel_connect, kernel_bind, kernel_listen, kernel_sendmsg, and 3 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_addr_kern.c -->
