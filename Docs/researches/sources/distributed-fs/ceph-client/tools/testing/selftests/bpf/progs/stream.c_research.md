<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stream.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stream.c

## Purpose

BPF stream printk and diagnostic output suite covering ENOSPC, loop timeout, resilient-lock deadlock reporting, arena faults, callbacks, and stack-print kfuncs.

## Important APIs, Types, and Functions

Attach sections: .maps, syscall, license. Map types: BPF_MAP_TYPE_ARENA, BPF_MAP_TYPE_ARRAY. Important local functions/programs: stream_exhaust, stream_cond_break, stream_deadlock, stream_syscall, stream_arena_write_fault, stream_arena_read_fault, subprog, stream_arena_subprog_fault, timer_cb, stream_arena_callback_fault, stream_print_stack_kfunc, stream_print_stack_invalid_id, stream_print_kfuncs_locked. Helper and kfunc calls: bpf_addr_space_cast, bpf_map_lookup_elem, bpf_repeat, bpf_res_spin_lock, bpf_res_spin_unlock, bpf_spin_lock, bpf_spin_unlock, bpf_stream_print_stack, bpf_stream_printk, bpf_timer_init, bpf_timer_set_callback, bpf_timer_start. Important structs/types visible in this file: arr_elem, elem. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h, bpf_experimental.h, bpf_arena_common.h.

Verifier/test annotations present: __success, __retval(0), __arch_x86_64, __arch_arm64, __arch_s390x, __stderr("ERROR: Timeout detected for may_goto instruction"), __stderr("CPU: {{[0-9]+}} UID: 0 PID: {{[0-9]+}} Comm: {{.*}}"), __stderr("ERROR: AA or ABBA deadlock detected for bpf_res_spin_lock"), and 4 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `stream_exhaust` and related routines such as `stream_cond_break, stream_deadlock, stream_syscall, stream_arena_write_fault`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARENA, BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int size, u64 fault_addr, u64 user_vm_start, int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, syscall, license` programs, helper coverage for `bpf_addr_space_cast, bpf_map_lookup_elem, bpf_repeat, bpf_res_spin_lock, bpf_res_spin_unlock, bpf_spin_lock, bpf_spin_unlock, bpf_stream_print_stack, and 4 more`, and stable behavior of `stream_exhaust, stream_cond_break, stream_deadlock, stream_syscall, stream_arena_write_fault, stream_arena_read_fault, and 7 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stream.c -->
