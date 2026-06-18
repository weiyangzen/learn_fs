<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf.h

## Purpose

Reusable Python stack unwinder BPF program that reads PyThreadState/PyFrameObject/PyCodeObject fields from user memory, maps symbols, captures kernel/user stack IDs, and emits perf events.

## Important APIs, Types, and Functions

Attach sections: .maps, raw_tracepoint/kfree_skb, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_PERF_EVENT_ARRAY, BPF_MAP_TYPE_STACK_TRACE. Important local functions/programs: get_frame_data, process_frame_callback, __on_event, on_event. Helper and kfunc calls: bpf_for, bpf_get_current_comm, bpf_get_current_pid_tgid, bpf_get_current_task, bpf_get_smp_processor_id, bpf_get_stackid, bpf_loop, bpf_map_lookup_elem, bpf_map_update_elem, bpf_perf_event_output, bpf_probe_read_user, bpf_probe_read_user_str. Important structs/types visible in this file: process_frame_ctx. Includes: linux/sched.h, linux/ptrace.h, stdint.h, stddef.h, stdbool.h, linux/bpf.h, bpf/bpf_helpers.h, bpf_misc.h, bpf_compiler.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `get_frame_data` and related routines such as `process_frame_callback, __on_event, on_event`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_PERF_EVENT_ARRAY, BPF_MAP_TYPE_STACK_TRACE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int PyThreadState_frame, int PyThreadState_thread, int PyFrameObject_back, int PyFrameObject_code, int PyFrameObject_lineno, int PyCodeObject_filename, int PyCodeObject_name, int String_data, int String_size, bool use_tls, and 15 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, perf-event output userspace reader. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases. Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, raw_tracepoint/kfree_skb, license` programs, helper coverage for `bpf_for, bpf_get_current_comm, bpf_get_current_pid_tgid, bpf_get_current_task, bpf_get_smp_processor_id, bpf_get_stackid, bpf_loop, bpf_map_lookup_elem, and 4 more`, and stable behavior of `get_frame_data, process_frame_callback, __on_event, on_event` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf.h -->
