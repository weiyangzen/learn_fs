<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sk_bypass_prot_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sk_bypass_prot_mem.c

## Purpose

Socket memory accounting fixture that bypasses protocol memory pressure by adjusting socket options and retval paths during TCP/UDP init and cgroup socket creation.

## Important APIs, Types, and Functions

Attach sections: fentry/tcp_init_sock, fentry/udp_init_sock, cgroup/sock_create, license. Map types: none. Important local functions/programs: drain_memory_per_cpu_fw_alloc, get_memory_allocated, fentry_init_sock, BPF_PROG, sock_create. Helper and kfunc calls: bpf_core_cast, bpf_getsockopt, bpf_loop, bpf_per_cpu_ptr, bpf_set_retval, bpf_setsockopt. Important structs/types visible in this file: sk_prot. Includes: bpf_tracing_net.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, errno.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `drain_memory_per_cpu_fw_alloc` and related routines such as `get_memory_allocated, fentry_init_sock, BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int nr_cpus, long memory_allocated, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `fentry/tcp_init_sock, fentry/udp_init_sock, cgroup/sock_create, license` programs, helper coverage for `bpf_core_cast, bpf_getsockopt, bpf_loop, bpf_per_cpu_ptr, bpf_set_retval, bpf_setsockopt`, and stable behavior of `drain_memory_per_cpu_fw_alloc, get_memory_allocated, fentry_init_sock, BPF_PROG, sock_create` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sk_bypass_prot_mem.c -->
