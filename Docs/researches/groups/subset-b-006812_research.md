# subset-b-006812 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_subflow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_subflow.c

## Purpose

Tests MPTCP subflow socket operations by counting subflows per MPTCP token, setting SO_MARK by subflow order, applying congestion control on the second subflow, and validating those properties from a cgroup getsockopt program.

## Important APIs, Types, and Functions

Attach sections: license, .maps, sockops, cgroup/getsockopt. Map types: BPF_MAP_TYPE_HASH. Important local functions/programs: mptcp_subflow, _check_getsockopt_subflow_mark, _check_getsockopt_subflow_cc, _getsockopt_subflow. Helper and kfunc calls: bpf_core_cast, bpf_get_current_pid_tgid, bpf_map_lookup_elem, bpf_map_update_elem, bpf_setsockopt, bpf_skc_to_mptcp_sock. Important structs/types visible in this file: none. Includes: bpf_tracing_net.h, mptcp_bpf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `mptcp_subflow` and related routines such as `_check_getsockopt_subflow_mark, _check_getsockopt_subflow_cc, _getsockopt_subflow`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_HASH for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include char cc[TCP_CA_NAME_MAX], int pid, __u32 init, int err, int i, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, sockops, cgroup/getsockopt` programs, helper coverage for `bpf_core_cast, bpf_get_current_pid_tgid, bpf_map_lookup_elem, bpf_map_update_elem, bpf_setsockopt, bpf_skc_to_mptcp_sock`, and stable behavior of `mptcp_subflow, _check_getsockopt_subflow_mark, _check_getsockopt_subflow_cc, _getsockopt_subflow` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_subflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcpify.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcpify.c

## Purpose

Uses an fmod_ret hook on update_socket_protocol to turn socket protocol selection into IPPROTO_MPTCP for the target PID, providing the minimal BPF side of the mptcpify selftest.

## Important APIs, Types, and Functions

Attach sections: license, fmod_ret/update_socket_protocol. Map types: none. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_get_current_pid_tgid. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf_tracing_net.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int pid, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, fmod_ret/update_socket_protocol` programs, helper coverage for `bpf_get_current_pid_tgid`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcpify.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_common.h

## Purpose

Shared inline helper for nested-trust tests; it deliberately calls cpumask helpers through a nested pointer expression so success and failure files can exercise verifier trust propagation.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: bpf_cpumask_test_cpu. Helper and kfunc calls: bpf_cpumask_first_zero, bpf_cpumask_test_cpu. Important structs/types visible in this file: none. Includes: stdbool.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_cpumask_test_cpu`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `bpf_cpumask_first_zero, bpf_cpumask_test_cpu`, and stable behavior of `bpf_cpumask_test_cpu` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_failure.c

## Purpose

Negative verifier test for nested trusted-pointer propagation, especially untrusted task cpus_ptr and untrusted sock storage pointers passed into helpers expecting trusted or RCU-qualified arguments.

## Important APIs, Types, and Functions

Attach sections: license, .maps, tp_btf/task_newtask, tp_btf/tcp_probe. Map types: BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_cpumask_test_cpu, bpf_sk_storage_get. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h, nested_trust_common.h.

Verifier/test annotations present: __failure, __msg("R2 must be"), __msg("R2 type=untrusted_ptr_ expected=ptr_, trusted_ptr_, rcu_ptr_"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, tp_btf/task_newtask, tp_btf/tcp_probe` programs, helper coverage for `bpf_cpumask_test_cpu, bpf_sk_storage_get`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_success.c

## Purpose

Positive verifier companion for nested trusted-pointer propagation through task and socket-storage paths, proving that accepted trusted sources can be passed to cpumask helpers.

## Important APIs, Types, and Functions

Attach sections: license, .maps, tp_btf/task_newtask, tp_btf/tcp_probe. Map types: BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_cpumask_first_zero, bpf_cpumask_test_cpu, bpf_sk_storage_get. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h, nested_trust_common.h.

Verifier/test annotations present: __success. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, tp_btf/task_newtask, tp_btf/tcp_probe` programs, helper coverage for `bpf_cpumask_first_zero, bpf_cpumask_test_cpu, bpf_sk_storage_get`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/net_timestamping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/net_timestamping.c

## Purpose

Exercises TCP transmit timestamping sockops callbacks, storing sendmsg timestamps per socket, correlating timestamp keys, checking callback ordering/delays, and asserting unsafe BPF calls are rejected in timestamp callbacks.

## Important APIs, Types, and Functions

Attach sections: .maps, fentry/tcp_sendmsg_locked, sockops, license. Map types: BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: bpf_test_sockopt, bpf_test_access_sockopt, bpf_test_access_load_hdr_opt, bpf_test_access_cb_flags_set, bpf_test_access_bpf_calls, bpf_test_delay, BPF_PROG, skops_sockopt. Helper and kfunc calls: bpf_cast_to_kern_ctx, bpf_core_cast, bpf_get_current_pid_tgid, bpf_get_socket_cookie, bpf_getsockopt, bpf_ktime_get_ns, bpf_load_hdr_opt, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem, bpf_setsockopt, bpf_sk_storage_get, bpf_skc_to_tcp_sock, bpf_sock_ops_cb_flags_set, bpf_sock_ops_enable_tx_tstamp, bpf_test_access_bpf_calls, bpf_test_access_cb_flags_set, bpf_test_access_load_hdr_opt, and 3 more. Important structs/types visible in this file: sk_stg, sk_tskey, delay_info. Includes: vmlinux.h, bpf_tracing_net.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf_misc.h, bpf_kfuncs.h, errno.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_test_sockopt` and related routines such as `bpf_test_access_sockopt, bpf_test_access_load_hdr_opt, bpf_test_access_cb_flags_set, bpf_test_access_bpf_calls`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u32 monitored_pid, int nr_active, int nr_snd, int nr_passive, int nr_sched, int nr_txsw, int nr_ack, __u64 sendmsg_ns;	/* record ts when sendmsg is called */, u64 cookie, u32 tskey, and 12 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, fentry/tcp_sendmsg_locked, sockops, license` programs, helper coverage for `bpf_cast_to_kern_ctx, bpf_core_cast, bpf_get_current_pid_tgid, bpf_get_socket_cookie, bpf_getsockopt, bpf_ktime_get_ns, bpf_load_hdr_opt, bpf_map_delete_elem, and 13 more`, and stable behavior of `bpf_test_sockopt, bpf_test_access_sockopt, bpf_test_access_load_hdr_opt, bpf_test_access_cb_flags_set, bpf_test_access_bpf_calls, bpf_test_delay, and 2 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/net_timestamping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netcnt_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netcnt_prog.c

## Purpose

Counts cgroup skb traffic in cgroup local storage and per-CPU cgroup storage, using a small next-counter helper to update packet and byte totals with timestamps.

## Important APIs, Types, and Functions

Attach sections: .maps, cgroup/skb, license. Map types: BPF_MAP_TYPE_CGROUP_STORAGE, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE. Important local functions/programs: bpf_nextcnt. Helper and kfunc calls: bpf_get_local_storage, bpf_ktime_get_ns, bpf_nextcnt. Important structs/types visible in this file: none. Includes: linux/bpf.h, linux/version.h, bpf/bpf_helpers.h, netcnt_common.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_nextcnt`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_CGROUP_STORAGE, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, cgroup/skb, license` programs, helper coverage for `bpf_get_local_storage, bpf_ktime_get_ns, bpf_nextcnt`, and stable behavior of `bpf_nextcnt` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netcnt_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netif_receive_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netif_receive_skb.c

## Purpose

BTF/raw tracepoint style netif_receive_skb test that formats skb/kernel context data, compares device names, and records which netif receive subtests ran.

## Important APIs, Types, and Functions

Attach sections: .maps, tp_btf/netif_receive_skb, license. Map types: BPF_MAP_TYPE_PERCPU_ARRAY. Important local functions/programs: __strncmp, BPF_PROG. Helper and kfunc calls: bpf_core_type_id_kernel, bpf_map_lookup_elem, bpf_printk, bpf_snprintf_btf. Important structs/types visible in this file: none. Includes: btf_ptr.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf/bpf_core_read.h, bpf_misc.h, errno.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `__strncmp` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_PERCPU_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long ret, int num_subtests, int ran_subtests, bool skip, __u64 _hflags, int _cmp;						\, __u32 key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, tp_btf/netif_receive_skb, license` programs, helper coverage for `bpf_core_type_id_kernel, bpf_map_lookup_elem, bpf_printk, bpf_snprintf_btf`, and stable behavior of `__strncmp, BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netif_receive_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netns_cookie_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netns_cookie_prog.c

## Purpose

Verifies bpf_get_netns_cookie across sockops, sk_msg, tcx ingress, and cgroup skb contexts, with sockmap and socket-storage plumbing to carry socket state.

## Important APIs, Types, and Functions

Attach sections: .maps, sockops, sk_msg, tcx/ingress, cgroup_skb/ingress, license. Map types: BPF_MAP_TYPE_SK_STORAGE, BPF_MAP_TYPE_SOCKMAP. Important local functions/programs: get_netns_cookie_sockops, get_netns_cookie_sk_msg, get_netns_cookie_tcx, get_netns_cookie_cgroup_skb. Helper and kfunc calls: bpf_get_netns_cookie, bpf_sk_storage_get, bpf_sock_map_update. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `get_netns_cookie_sockops` and related routines such as `get_netns_cookie_sk_msg, get_netns_cookie_tcx, get_netns_cookie_cgroup_skb`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE, BPF_MAP_TYPE_SOCKMAP for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u32 key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, sockops, sk_msg, tcx/ingress, cgroup_skb/ingress, license` programs, helper coverage for `bpf_get_netns_cookie, bpf_sk_storage_get, bpf_sock_map_update`, and stable behavior of `get_netns_cookie_sockops, get_netns_cookie_sk_msg, get_netns_cookie_tcx, get_netns_cookie_cgroup_skb` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netns_cookie_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/normal_map_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/normal_map_btf.c

## Purpose

Validates that a normal array map value with BTF-described spin lock and list head can own allocated list nodes through bpf_obj_new and bpf_list_push_back.

## Important APIs, Types, and Functions

Attach sections: .maps, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: add_to_list_in_array. Helper and kfunc calls: bpf_get_current_pid_tgid, bpf_list_push_back, bpf_map_lookup_elem, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, map_value. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `add_to_list_in_array`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u64 data, int pid, bool done, int zero, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, license` programs, helper coverage for `bpf_get_current_pid_tgid, bpf_list_push_back, bpf_map_lookup_elem, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `add_to_list_in_array` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/normal_map_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_array.c

## Purpose

Exercises per-CPU object allocation through array maps and cgroup local storage, including this-CPU and arbitrary-CPU access under RCU and kptr exchange cleanup.

## Important APIs, Types, and Functions

Attach sections: .maps, ?fentry/bpf_fentry_test1, ?fentry/bpf_fentry_test2, ?fentry/bpf_fentry_test3, ?fentry/bpf_fentry_test4, ?fentry.s/bpf_fentry_test1, cgroup_skb/egress, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE. Important local functions/programs: bpf_rcu_read_lock, bpf_rcu_read_unlock, BPF_PROG, cgroup_egress. Helper and kfunc calls: bpf_for, bpf_get_current_pid_tgid, bpf_get_local_storage, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_map_update_elem, bpf_per_cpu_ptr, bpf_percpu_obj_drop, bpf_percpu_obj_new, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_this_cpu_ptr. Important structs/types visible in this file: val_t, elem. Includes: bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_rcu_read_lock` and related routines such as `bpf_rcu_read_unlock, BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long sum, int index, int my_pid, u64 value, int key, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, ?fentry/bpf_fentry_test1, ?fentry/bpf_fentry_test2, ?fentry/bpf_fentry_test3, ?fentry/bpf_fentry_test4, ?fentry.s/bpf_fentry_test1, and 2 more` programs, helper coverage for `bpf_for, bpf_get_current_pid_tgid, bpf_get_local_storage, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_map_update_elem, bpf_per_cpu_ptr, bpf_percpu_obj_drop, and 4 more`, and stable behavior of `bpf_rcu_read_lock, bpf_rcu_read_unlock, BPF_PROG, cgroup_egress` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_cgrp_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_cgrp_local_storage.c

## Purpose

Exercises per-CPU object allocation stored in cgroup local storage, including kptr exchange, per-CPU pointer access, and cleanup across fentry programs.

## Important APIs, Types, and Functions

Attach sections: .maps, fentry/bpf_fentry_test1, fentry/bpf_fentry_test2, fentry/bpf_fentry_test3, license. Map types: BPF_MAP_TYPE_CGRP_STORAGE. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_cgrp_storage_get, bpf_for, bpf_get_current_pid_tgid, bpf_get_current_task_btf, bpf_kptr_xchg, bpf_per_cpu_ptr, bpf_percpu_obj_drop, bpf_percpu_obj_new. Important structs/types visible in this file: val_t, elem. Includes: bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_CGRP_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long sum, int my_pid, int i, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, fentry/bpf_fentry_test1, fentry/bpf_fentry_test2, fentry/bpf_fentry_test3, license` programs, helper coverage for `bpf_cgrp_storage_get, bpf_for, bpf_get_current_pid_tgid, bpf_get_current_task_btf, bpf_kptr_xchg, bpf_per_cpu_ptr, bpf_percpu_obj_drop, bpf_percpu_obj_new`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_cgrp_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_fail.c

## Purpose

Negative verifier suite for per-CPU allocated objects and kptrs, covering invalid drops, type mismatches, scalar misuse, and illegal stores to referenced per-CPU kptrs.

## Important APIs, Types, and Functions

Attach sections: .maps, ?fentry/bpf_fentry_test1, ?fentry.s/bpf_fentry_test1, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_percpu_obj_drop, bpf_percpu_obj_new, bpf_this_cpu_ptr. Important structs/types visible in this file: val_t, val2_t, val_with_ptr_t, val_with_rb_root_t, val_600b_t, elem. Includes: bpf_experimental.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("store to referenced kptr disallowed"), __msg("invalid kptr access, R2 type=percpu_ptr_val2_t expected=ptr_val_t"), __msg("R1 type=scalar expected=percpu_ptr_, percpu_rcu_ptr_, percpu_trusted_ptr_"), __msg("arg#0 expected for bpf_percpu_obj_drop()"), __msg("arg#0 expected for bpf_obj_drop()"), __msg("bpf_percpu_obj_new type ID argument must be of a struct of scalars"), __msg("bpf_percpu_obj_new type ID argument must not contain special fields"), and 1 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long b, char b[600], long sum, long ret, int index, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, ?fentry/bpf_fentry_test1, ?fentry.s/bpf_fentry_test1, license` programs, helper coverage for `bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_percpu_obj_drop, bpf_percpu_obj_new, bpf_this_cpu_ptr`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perf_event_stackmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perf_event_stackmap.c

## Purpose

Perf-event program that samples stack IDs and raw stacks into stack-trace/per-CPU maps, used to validate stack helpers from perf_event context.

## Important APIs, Types, and Functions

Attach sections: .maps, perf_event, license. Map types: BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_STACK_TRACE. Important local functions/programs: oncpu. Helper and kfunc calls: bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `oncpu`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_STACK_TRACE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long stackid_kernel, long stackid_user, long stack_kernel, long stack_user, __u32 key, long val, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, perf_event, license` programs, helper coverage for `bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem`, and stable behavior of `oncpu` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perf_event_stackmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perfbuf_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perfbuf_bench.c

## Purpose

Minimal perf-event-array benchmark payload producer for comparing perfbuf output throughput.

## Important APIs, Types, and Functions

Attach sections: license, .maps. Map types: BPF_MAP_TYPE_PERF_EVENT_ARRAY. Important local functions/programs: bench_perfbuf. Helper and kfunc calls: bpf_perf_event_output. Important structs/types visible in this file: none. Includes: linux/bpf.h, stdint.h, bpf/bpf_helpers.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bench_perfbuf`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_PERF_EVENT_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long sample_val, int i, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, perf-event output userspace reader. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps` programs, helper coverage for `bpf_perf_event_output`, and stable behavior of `bench_perfbuf` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perfbuf_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempt_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempt_lock.c

## Purpose

Verifier test matrix for bpf_preempt_disable/enable and guard-preempt regions, covering missing enables, subprogram balancing, and forbidden sleepable helpers or kfuncs while preemption is disabled.

## Important APIs, Types, and Functions

Attach sections: ?tc, ?syscall, license. Map types: none. Important local functions/programs: preempt_lock_missing_1, preempt_lock_missing_2, preempt_lock_missing_3, preempt_lock_missing_3_minus_2, preempt_disable, preempt_enable, preempt_lock_missing_1_subprog, preempt_lock_missing_2_subprog, preempt_lock_missing_2_minus_1_subprog, preempt_balance_subprog, preempt_sleepable_helper, preempt_sleepable_kfunc, preempt_global_subprog_test, preempt_global_sleepable_helper_subprog, and 2 more. Helper and kfunc calls: bpf_copy_from_user, bpf_copy_from_user_str, bpf_guard_preempt, bpf_preempt_disable, bpf_preempt_enable, bpf_printk. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __failure, __msg("BPF_EXIT instruction in main prog cannot be used inside bpf_preempt_disable-ed region"), __success, __msg("sleepable helper bpf_copy_from_user#"), __msg("kernel func bpf_copy_from_user_str is sleepable within non-preemptible region"), __msg("sleepable global function"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `preempt_lock_missing_1` and related routines such as `preempt_lock_missing_2, preempt_lock_missing_3, preempt_lock_missing_3_minus_2, preempt_disable`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include u32 data, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `?tc, ?syscall, license` programs, helper coverage for `bpf_copy_from_user, bpf_copy_from_user_str, bpf_guard_preempt, bpf_preempt_disable, bpf_preempt_enable, bpf_printk`, and stable behavior of `preempt_lock_missing_1, preempt_lock_missing_2, preempt_lock_missing_3, preempt_lock_missing_3_minus_2, preempt_disable, preempt_enable, and 10 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempt_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempted_bpf_ma_op.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempted_bpf_ma_op.c

## Purpose

Stress test for BPF memory allocator map operations under preemption by repeatedly deleting, allocating, and exchanging kptr array entries from fentry programs.

## Important APIs, Types, and Functions

Attach sections: .maps, license, fentry/bpf_fentry_test1, fentry/bpf_fentry_test2, fentry/bpf_fentry_test3, fentry/bpf_fentry_test4. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: del_array, add_array, del_then_add_array, BPF_PROG2. Helper and kfunc calls: bpf_kptr_xchg, bpf_loop, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new. Important structs/types visible in this file: bin_data, map_value. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `del_array` and related routines such as `add_array, del_then_add_array, BPF_PROG2`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include char data[256], bool nomem_err, int i, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, license, fentry/bpf_fentry_test1, fentry/bpf_fentry_test2, fentry/bpf_fentry_test3, fentry/bpf_fentry_test4` programs, helper coverage for `bpf_kptr_xchg, bpf_loop, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new`, and stable behavior of `del_array, add_array, del_then_add_array, BPF_PROG2` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempted_bpf_ma_op.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/prepare.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/prepare.c

## Purpose

Small fixture defining array and ringbuf maps plus a cgroup skb program, used by loader-side prepare tests to validate object/map setup.

## Important APIs, Types, and Functions

Attach sections: license, .maps, cgroup_skb/egress. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_RINGBUF. Important local functions/programs: program. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `program`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_RINGBUF for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int err, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, cgroup_skb/egress` programs, helper coverage for `none`, and stable behavior of `program` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/prepare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_freplace_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_freplace_prog.c

## Purpose

Tiny privileged-loading fixture: the map/program/freplace components are combined by user space to validate privilege checks around queues, XDP, and freplace attachment.

## Important APIs, Types, and Functions

Attach sections: license, freplace/xdp_prog1. Map types: none. Important local functions/programs: new_xdp_prog2. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `new_xdp_prog2`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, freplace/xdp_prog1` programs, helper coverage for `none`, and stable behavior of `new_xdp_prog2` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_freplace_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_map.c

## Purpose

Tiny privileged-loading fixture: the map/program/freplace components are combined by user space to validate privilege checks around queues, XDP, and freplace attachment.

## Important APIs, Types, and Functions

Attach sections: license, .maps. Map types: BPF_MAP_TYPE_QUEUE. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_QUEUE for the lifetime of the loaded object or until the user-space test deletes/updates entries.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest.
For this file specifically, useful signals include presence of `license, .maps` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_prog.c

## Purpose

Tiny privileged-loading fixture: the map/program/freplace components are combined by user space to validate privilege checks around queues, XDP, and freplace attachment.

## Important APIs, Types, and Functions

Attach sections: license, xdp. Map types: none. Important local functions/programs: xdp_prog1. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `xdp_prog1`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, xdp` programs, helper coverage for `none`, and stable behavior of `xdp_prog1` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/priv_prog.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue_goto_start.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue_goto_start.c

## Purpose

Struct_ops selftest for verifier-generated prologue/epilogue behavior around bpf_testmod kfunc callbacks, with syscall probes checking exact arithmetic return values.

## Important APIs, Types, and Functions

Attach sections: license, struct_ops/test_prologue_goto_start, struct_ops/test_epilogue_goto_start, struct_ops/test_pro_epilogue_goto_start, .struct_ops.link, syscall. Map types: none. Important local functions/programs: syscall_prologue_goto_start, syscall_epilogue_goto_start, syscall_pro_epilogue_goto_start. Helper and kfunc calls: bpf_kfunc_st_ops_test_epilogue, bpf_kfunc_st_ops_test_pro_epilogue, bpf_kfunc_st_ops_test_prologue. Important structs/types visible in this file: bpf_testmod_st_ops. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf_misc.h, ../test_kmods/bpf_testmod.h, ../test_kmods/bpf_testmod_kfunc.h.

Verifier/test annotations present: __success, __retval(0), __retval(20000) /* (EPILOGUE_A [10000]), __retval(22000) /* (PROLOGUE_A [1000] + EPILOGUE_A [10000]). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `syscall_prologue_goto_start` and related routines such as `syscall_epilogue_goto_start, syscall_pro_epilogue_goto_start`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, struct_ops/test_prologue_goto_start, struct_ops/test_epilogue_goto_start, struct_ops/test_pro_epilogue_goto_start, .struct_ops.link, syscall` programs, helper coverage for `bpf_kfunc_st_ops_test_epilogue, bpf_kfunc_st_ops_test_pro_epilogue, bpf_kfunc_st_ops_test_prologue`, and stable behavior of `syscall_prologue_goto_start, syscall_epilogue_goto_start, syscall_pro_epilogue_goto_start` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue_goto_start.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue_with_kfunc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue_with_kfunc.c

## Purpose

Struct_ops selftest for verifier-generated prologue/epilogue behavior around bpf_testmod kfunc callbacks, with syscall probes checking exact arithmetic return values.

## Important APIs, Types, and Functions

Attach sections: license, struct_ops/test_pro_epilogue, syscall, .struct_ops.link. Map types: none. Important local functions/programs: __kfunc_btf_root, syscall_pro_epilogue. Helper and kfunc calls: bpf_kfunc_st_ops_inc10, bpf_kfunc_st_ops_test_pro_epilogue. Important structs/types visible in this file: bpf_testmod_st_ops. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf_misc.h, ../test_kmods/bpf_testmod.h, ../test_kmods/bpf_testmod_kfunc.h.

Verifier/test annotations present: __success, __retval(22022) /* (PROLOGUE_A [1000] + KFUNC_INC10 + SUBPROG_A [1] + EPILOGUE_A [10000]). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `__kfunc_btf_root` and related routines such as `syscall_pro_epilogue`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, struct_ops/test_pro_epilogue, syscall, .struct_ops.link` programs, helper coverage for `bpf_kfunc_st_ops_inc10, bpf_kfunc_st_ops_test_pro_epilogue`, and stable behavior of `__kfunc_btf_root, syscall_pro_epilogue` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pro_epilogue_with_kfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.h

## Purpose

Data-contract header for profiler.inc.h, defining event payload limits, metadata structures, cgroup/file/kill/exec/fork payload layouts, and function-stat identifiers.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: ancestors_data_t, var_metadata_t, cgroup_data_t, var_sysctl_data_t, var_kill_data_t, var_exec_data_t, var_fork_data_t, var_filemod_data_t, profiler_config_struct, bpf_func_stats_data, bpf_func_stats_ctx. Includes: none.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

Global data variables include int cgroup_full_path_root_pos, char payload[MAX_SYSCTL_PAYLOAD_LEN], int kill_sig, char payload[MAX_KILL_PAYLOAD_LEN], char payload[MAX_EXEC_PAYLOAD_LEN], char payload[MAX_METADATA_PAYLOAD_LEN], char payload[MAX_FILEMOD_PAYLOAD_LEN], bool fetch_cgroups_from_bpf, bool use_variable_buffers, bool read_environ_from_exec, and 1 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.inc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.inc.h

## Purpose

Large reusable BPF profiler implementation covering kill, exec, fork, sysctl, file modification, cgroup metadata, filtering maps, perf output, and per-function stats.

## Important APIs, Types, and Functions

Attach sections: .maps, kprobe/proc_sys_write, tracepoint/syscalls/sys_enter_kill, raw_tracepoint/sched_process_exit, raw_tracepoint/sched_process_exec, kretprobe/do_file_open, kprobe/vfs_link, kprobe/vfs_symlink, raw_tracepoint/sched_process_fork, license. Map types: BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERF_EVENT_ARRAY. Important local functions/programs: IS_ERR, get_userspace_pid, is_init_process, get_var_spid_index, populate_ancestors, get_var_kill_data, trace_var_sys_kill, bpf_stats_enter, bpf_stats_exit, bpf_stats_pre_submit_var_perf_event, is_ancestor_in_allowed_inodes, is_dentry_allowed_for_filemod, tracepoint__syscalls__sys_enter_kill, raw_tracepoint__sched_process_exit, and 4 more. Helper and kfunc calls: bpf_cmp_likely, bpf_cmp_unlikely, bpf_core_enum_value, bpf_core_field_exists, bpf_core_read_str, bpf_get_current_pid_tgid, bpf_get_current_task, bpf_get_current_uid_gid, bpf_get_smp_processor_id, bpf_ktime_get_ns, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem, bpf_nop_mov, bpf_perf_event_output, bpf_probe_read_kernel, bpf_probe_read_kernel_str, bpf_stats_enter, and 2 more. Important structs/types visible in this file: var_kill_data_arr_t, kernfs_iattrs___52, kernfs_node___52. Includes: vmlinux.h, bpf/bpf_core_read.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, profiler.h, err.h, bpf_experimental.h, bpf_compiler.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `IS_ERR` and related routines such as `get_userspace_pid, is_init_process, get_var_spid_index, populate_ancestors`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERF_EVENT_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include u32 ino, u32 generation, u64 id, int cgrp_id, int subsys_id, u64 uid_gid, int zero, u32 spid, int index, u64 delta_sec, and 16 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, perf-event output userspace reader. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases. Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, kprobe/proc_sys_write, tracepoint/syscalls/sys_enter_kill, raw_tracepoint/sched_process_exit, raw_tracepoint/sched_process_exec, kretprobe/do_file_open, and 4 more` programs, helper coverage for `bpf_cmp_likely, bpf_cmp_unlikely, bpf_core_enum_value, bpf_core_field_exists, bpf_core_read_str, bpf_get_current_pid_tgid, bpf_get_current_task, bpf_get_current_uid_gid, and 12 more`, and stable behavior of `IS_ERR, get_userspace_pid, is_init_process, get_var_spid_index, populate_ancestors, get_var_kill_data, and 12 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.inc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler1.c

## Purpose

Build-variant wrapper around profiler.inc.h that selects loop unrolling and inlining behavior for verifier/compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: profiler.inc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler2.c

## Purpose

Build-variant wrapper around profiler.inc.h that selects loop unrolling and inlining behavior for verifier/compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: profiler.inc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler3.c

## Purpose

Build-variant wrapper around profiler.inc.h that selects loop unrolling and inlining behavior for verifier/compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: profiler.inc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler3.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf100.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf100.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf180.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf180.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf50.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf50.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_bpf_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_bpf_loop.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_bpf_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_iter.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_nounroll.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_nounroll.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf600_nounroll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_global.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_global.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_global.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_subprogs.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_subprogs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/raw_tp_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/raw_tp_null.c

## Purpose

Positive raw tracepoint nullable-argument test that checks a nullable task pointer before use.

## Important APIs, Types, and Functions

Attach sections: license, tp_btf/bpf_testmod_test_raw_tp_null_tp. Map types: none. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_get_current_task_btf. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int tid, int i, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, tp_btf/bpf_testmod_test_raw_tp_null_tp` programs, helper coverage for `bpf_get_current_task_btf`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/raw_tp_null.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree.c

## Purpose

Positive BPF rbtree API suite covering add, first, remove, nested roots, root arrays, callback execution, and correct object drops under spin locks.

## Important APIs, Types, and Functions

Attach sections: tc, license. Map types: none. Important local functions/programs: less, __add_three, rbtree_add_nodes, rbtree_add_nodes_nested, rbtree_add_and_remove, rbtree_add_and_remove_array, rbtree_first_and_remove, rbtree_api_release_aliasing. Helper and kfunc calls: bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, root_nested_inner, root_nested. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `__add_three, rbtree_add_nodes, rbtree_add_nodes_nested, rbtree_add_and_remove`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include long key, long data, long less_callback_ran, long removed_key, long first_data[2], long k1, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `tc, license` programs, helper coverage for `bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `less, __add_three, rbtree_add_nodes, rbtree_add_nodes_nested, rbtree_add_and_remove, rbtree_add_and_remove_array, and 2 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__add_wrong_type.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__add_wrong_type.c

## Purpose

BTF negative test proving bpf_rbtree_add rejects a node/container type that does not match the root __contains declaration.

## Important APIs, Types, and Functions

Attach sections: tc, license. Map types: none. Important local functions/programs: less2, rbtree_api_add__add_wrong_type. Helper and kfunc calls: bpf_obj_new, bpf_rbtree_add, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, node_data2. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less2` and related routines such as `rbtree_api_add__add_wrong_type`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int key, int data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `tc, license` programs, helper coverage for `bpf_obj_new, bpf_rbtree_add, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `less2, rbtree_api_add__add_wrong_type` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__add_wrong_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__wrong_node_type.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__wrong_node_type.c

## Purpose

BTF negative test proving rbtree operations reject the wrong embedded node field type for a declared root.

## Important APIs, Types, and Functions

Attach sections: tc, license. Map types: none. Important local functions/programs: rbtree_api_add__wrong_node_type. Helper and kfunc calls: bpf_obj_new, bpf_rbtree_first, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `rbtree_api_add__wrong_node_type`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int key, int data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `tc, license` programs, helper coverage for `bpf_obj_new, bpf_rbtree_first, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `rbtree_api_add__wrong_node_type` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__wrong_node_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_fail.c

## Purpose

Negative rbtree verifier suite covering missing locks, unreleased references, double insertion, unchecked remove results, escaped release-on-unlock references, and illegal callback calls.

## Important APIs, Types, and Functions

Attach sections: ?tc, license. Map types: none. Important local functions/programs: less, rbtree_api_nolock_add, rbtree_api_nolock_remove, rbtree_api_nolock_first, rbtree_api_remove_unadded_node, rbtree_api_remove_no_drop, rbtree_api_add_to_multiple_trees, rbtree_api_use_unchecked_remove_retval, rbtree_api_add_release_unlock_escape, rbtree_api_first_release_unlock_escape, less__bad_fn_call_add, less__bad_fn_call_remove, less__bad_fn_call_first_unlock_after, add_with_cb, and 3 more. Helper and kfunc calls: bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("bpf_spin_lock at off=16 must be held for bpf_rb_root"), __retval(0), __msg("Unreleased reference id=3 alloc_insn={{[0-9]+}}"), __msg("arg#1 expected pointer to allocated object"), __msg("Possibly NULL pointer passed to trusted arg1"), __msg("bpf_rbtree_remove can only take non-owning or refcounted bpf_rb_node pointer"), __msg("rbtree_remove not allowed in rbtree cb"), and 1 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `rbtree_api_nolock_add, rbtree_api_nolock_remove, rbtree_api_nolock_first, rbtree_api_remove_unadded_node`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include long key, long data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `?tc, license` programs, helper coverage for `bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `less, rbtree_api_nolock_add, rbtree_api_nolock_remove, rbtree_api_nolock_first, rbtree_api_remove_unadded_node, rbtree_api_remove_no_drop, and 11 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search.c

## Purpose

Search-oriented rbtree test that builds two trees over refcounted nodes, traverses root/left/right links, removes nodes, and checks lock requirements for search helpers.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: less0, less1, rbtree_search. Helper and kfunc calls: bpf_jiffies64, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_left, bpf_rbtree_remove, bpf_rbtree_right, bpf_rbtree_root, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __retval(0), __failure. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less0` and related routines such as `less1, rbtree_search`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int key0, int key1, int zero, long lookup_key, __u64 jiffies, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_jiffies64, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_left, bpf_rbtree_remove, bpf_rbtree_right, bpf_rbtree_root, and 3 more`, and stable behavior of `less0, less1, rbtree_search` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search_kptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search_kptr.c

## Purpose

Rbtree search test with embedded kptr payloads, validating kptr exchange from non-owning rbtree references and a negative no-lock exchange case.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: less, rbtree_search_kptr, less_r, rbtree_search_kptr_ref, non_own_ref_kptr_xchg_no_lock. Helper and kfunc calls: bpf_kptr_xchg, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_left, bpf_rbtree_remove, bpf_rbtree_right, bpf_rbtree_root, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, tree_node, tree_node_ref. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __retval(0), __failure, __msg("R1 type=scalar expected=map_value, ptr_, ptr_"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `rbtree_search_kptr, less_r, rbtree_search_kptr_ref, non_own_ref_kptr_xchg_no_lock`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int data, u64 key, int lookup_key, int lookup_data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_kptr_xchg, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_left, bpf_rbtree_remove, bpf_rbtree_right, and 4 more`, and stable behavior of `less, rbtree_search_kptr, less_r, rbtree_search_kptr_ref, non_own_ref_kptr_xchg_no_lock` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search_kptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_read_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_read_lock.c

## Purpose

Comprehensive verifier matrix for explicit bpf_rcu_read_lock/unlock, task/cgroup/key kfunc usage, sleepable versus non-sleepable contexts, subprogram balance, and RCU pointer trust.

## Important APIs, Types, and Functions

Attach sections: license, .maps, ?lsm.s/bpf. Map types: BPF_MAP_TYPE_TASK_STORAGE. Important local functions/programs: bpf_key_put, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_release, get_cgroup_id, task_succ, no_lock, two_regions, non_sleepable_1, non_sleepable_2, task_acquire, miss_lock, miss_unlock, non_sleepable_rcu_mismatch, and 23 more. Helper and kfunc calls: bpf_copy_from_user, bpf_copy_from_user_str, bpf_copy_from_user_task, bpf_get_current_cgroup_id, bpf_get_current_task_btf, bpf_get_prandom_u32, bpf_key_put, bpf_lookup_user_key, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_acquire, bpf_task_pt_regs, bpf_task_release, bpf_task_storage_get. Important structs/types visible in this file: bpf_key, task_struct. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf_tracing_net.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_key_put` and related routines such as `bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_release, get_cgroup_id`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_TASK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __s32 key_serial, long init_val, __u32 value, volatile int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, ?lsm.s/bpf` programs, helper coverage for `bpf_copy_from_user, bpf_copy_from_user_str, bpf_copy_from_user_task, bpf_get_current_cgroup_id, bpf_get_current_task_btf, bpf_get_prandom_u32, bpf_key_put, bpf_lookup_user_key, and 6 more`, and stable behavior of `bpf_key_put, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_release, get_cgroup_id, task_succ, and 31 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_read_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_tasks_trace_gp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_tasks_trace_gp.c

## Purpose

Tiny syscall program that calls the test kfunc for RCU Tasks Trace grace-period behavior.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: call_rcu_tasks_trace. Helper and kfunc calls: bpf_kfunc_call_test_call_rcu_tasks_trace. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, ../test_kmods/bpf_testmod_kfunc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `call_rcu_tasks_trace`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int done, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_kfunc_call_test_call_rcu_tasks_trace`, and stable behavior of `call_rcu_tasks_trace` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_tasks_trace_gp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_cgroupfs_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_cgroupfs_xattr.c

## Purpose

Sleepable LSM file_open program that resolves the current cgroup, iterates/read cgroupfs xattrs via dynptr, and records matching xattr results.

## Important APIs, Types, and Functions

Attach sections: license, lsm.s/file_open. Map types: none. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_cgroup_from_id, bpf_cgroup_read_xattr, bpf_cgroup_release, bpf_dynptr_from_mem, bpf_for_each, bpf_get_current_cgroup_id, bpf_get_current_pid_tgid, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_strncmp. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include char xattr_value[64], bool found_value_a, bool found_value_b, u64 cgrp_id, int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, lsm.s/file_open` programs, helper coverage for `bpf_cgroup_from_id, bpf_cgroup_read_xattr, bpf_cgroup_release, bpf_dynptr_from_mem, bpf_for_each, bpf_get_current_cgroup_id, bpf_get_current_pid_tgid, bpf_rcu_read_lock, and 2 more`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_cgroupfs_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_vsyscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_vsyscall.c

## Purpose

Helper wrapper collection for reading user, kernel, and vsyscall memory with probe_read and copy_from_user variants under a target PID gate.

## Important APIs, Types, and Functions

Attach sections: license. Map types: none. Important local functions/programs: bpf_copy_from_user_str, bpf_copy_from_user_task_str, do_probe_read, do_copy_from_user. Helper and kfunc calls: bpf_copy_from_user, bpf_copy_from_user_str, bpf_copy_from_user_task, bpf_copy_from_user_task_str, bpf_get_current_pid_tgid, bpf_get_current_task_btf, bpf_probe_read, bpf_probe_read_kernel, bpf_probe_read_kernel_str, bpf_probe_read_str, bpf_probe_read_user, bpf_probe_read_user_str. Important structs/types visible in this file: none. Includes: vmlinux.h, linux/types.h, bpf/bpf_helpers.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_copy_from_user_str` and related routines such as `bpf_copy_from_user_task_str, do_probe_read, do_copy_from_user`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int target_pid, int read_ret[10], char buf[8], which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license` programs, helper coverage for `bpf_copy_from_user, bpf_copy_from_user_str, bpf_copy_from_user_task, bpf_copy_from_user_task_str, bpf_get_current_pid_tgid, bpf_get_current_task_btf, bpf_probe_read, bpf_probe_read_kernel, and 4 more`, and stable behavior of `bpf_copy_from_user_str, bpf_copy_from_user_task_str, do_probe_read, do_copy_from_user` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_vsyscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recursion.c

## Purpose

Recursion guard fixture that attaches to htab_map_delete_elem and deletes from a hash map to validate BPF recursion handling.

## Important APIs, Types, and Functions

Attach sections: license, .maps, fentry/htab_map_delete_elem. Map types: BPF_MAP_TYPE_HASH. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_map_delete_elem. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_HASH for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int pass1, int pass2, int key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, fentry/htab_map_delete_elem` programs, helper coverage for `bpf_map_delete_elem`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recursion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg4_prog.c

## Purpose

cgroup recvmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields or Unix path and returning allow/deny status.

## Important APIs, Types, and Functions

Attach sections: cgroup/recvmsg4, license. Map types: none. Important local functions/programs: recvmsg4_prog. Helper and kfunc calls: bpf_htonl, bpf_htons. Important structs/types visible in this file: none. Includes: linux/stddef.h, linux/bpf.h, linux/in.h, sys/socket.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_sockopt_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `recvmsg4_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/recvmsg4, license` programs, helper coverage for `bpf_htonl, bpf_htons`, and stable behavior of `recvmsg4_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg4_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg6_prog.c

## Purpose

cgroup recvmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields or Unix path and returning allow/deny status.

## Important APIs, Types, and Functions

Attach sections: cgroup/recvmsg6, license. Map types: none. Important local functions/programs: recvmsg6_prog. Helper and kfunc calls: bpf_htonl, bpf_htons. Important structs/types visible in this file: none. Includes: linux/stddef.h, linux/bpf.h, linux/in6.h, sys/socket.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_sockopt_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `recvmsg6_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/recvmsg6, license` programs, helper coverage for `bpf_htonl, bpf_htons`, and stable behavior of `recvmsg6_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg6_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg_unix_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg_unix_prog.c

## Purpose

cgroup recvmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields or Unix path and returning allow/deny status.

## Important APIs, Types, and Functions

Attach sections: cgroup/recvmsg_unix, license. Map types: none. Important local functions/programs: recvmsg_unix_prog. Helper and kfunc calls: bpf_cast_to_kern_ctx, bpf_core_cast, bpf_sock_addr_set_sun_path. Important structs/types visible in this file: none. Includes: vmlinux.h, string.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_kfuncs.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `recvmsg_unix_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __u32 unaddrlen, int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/recvmsg_unix, license` programs, helper coverage for `bpf_cast_to_kern_ctx, bpf_core_cast, bpf_sock_addr_set_sun_path`, and stable behavior of `recvmsg_unix_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg_unix_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr.c

## Purpose

Large positive and mixed verifier suite for refcounted allocated nodes shared across rbtree, list, array kptr, and percpu hash map ownership paths.

## Important APIs, Types, and Functions

Attach sections: .maps, tc, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_HASH. Important local functions/programs: less, less_a, __insert_in_tree_and_list, __stash_map_insert_tree, __read_from_tree, __read_from_list, __read_from_unstash, rbtree_refcounted_node_ref_escapes, rbtree_refcounted_node_ref_escapes_owning_input, __stash_map_empty_xchg, rbtree_wrong_owner_remove_fail_a1, rbtree_wrong_owner_remove_fail_b, rbtree_wrong_owner_remove_fail_a2, BPF_PROG, and 4 more. Helper and kfunc calls: bpf_kptr_xchg, bpf_list_pop_front, bpf_list_push_back, bpf_list_push_front, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_probe_read_kernel, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, map_value, node_acquire. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __success, __retval(579), __retval(-1), __retval(84). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `less_a, __insert_in_tree_and_list, __stash_map_insert_tree, __read_from_tree`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_HASH for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long key, long list_data, long data, long res, long val, int idx, u32 refcount, int key, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, tc, license` programs, helper coverage for `bpf_kptr_xchg, bpf_list_pop_front, bpf_list_push_back, bpf_list_push_front, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_probe_read_kernel, and 8 more`, and stable behavior of `less, less_a, __insert_in_tree_and_list, __stash_map_insert_tree, __read_from_tree, __read_from_list, and 12 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr_fail.c

## Purpose

Negative companion for refcounted kptr ownership, covering leaked acquired references, maybe-NULL trusted args, and forbidden function calls while holding locks.

## Important APIs, Types, and Functions

Attach sections: ?tc, license. Map types: none. Important local functions/programs: less, rbtree_refcounted_node_ref_escapes, refcount_acquire_maybe_null, rbtree_refcounted_node_ref_escapes_owning_input, BPF_PROG. Helper and kfunc calls: bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_acquire. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("Unreleased reference id=4 alloc_insn={{[0-9]+}}"), __msg("Possibly NULL pointer passed to trusted arg0"), __msg("Unreleased reference id=3 alloc_insn={{[0-9]+}}"), __msg("function calls are not allowed while holding a lock"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `rbtree_refcounted_node_ref_escapes, refcount_acquire_maybe_null, rbtree_refcounted_node_ref_escapes_owning_input, BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include long key, long data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `?tc, license` programs, helper coverage for `bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `less, rbtree_refcounted_node_ref_escapes, refcount_acquire_maybe_null, rbtree_refcounted_node_ref_escapes_owning_input, BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock.c

## Purpose

Positive resilient spin-lock tests for map-value and global locks, lock ordering, same-lock try behavior, and held-lock capacity.

## Important APIs, Types, and Functions

Attach sections: .maps, .data.A, .data.B, tc, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: res_spin_lock_test, res_spin_lock_test_AB, res_spin_lock_test_BA, res_spin_lock_test_held_lock_max. Helper and kfunc calls: bpf_ktime_get_ns, bpf_map_lookup_elem, bpf_res_spin_lock, bpf_res_spin_unlock. Important structs/types visible in this file: arr_elem, bpf_res_spin_lock. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `res_spin_lock_test` and related routines such as `res_spin_lock_test_AB, res_spin_lock_test_BA, res_spin_lock_test_held_lock_max`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int r, int err, int ret, int key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, .data.A, .data.B, tc, license` programs, helper coverage for `bpf_ktime_get_ns, bpf_map_lookup_elem, bpf_res_spin_lock, bpf_res_spin_unlock`, and stable behavior of `res_spin_lock_test, res_spin_lock_test_AB, res_spin_lock_test_BA, res_spin_lock_test_held_lock_max` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock_fail.c

## Purpose

Negative resilient spin-lock matrix for bad arguments, AA deadlock, mismatched unlocks, IRQ-save pairing errors, out-of-order unlock, and invalid lock offsets.

## Important APIs, Types, and Functions

Attach sections: .maps, .data.A, .data.B, ?tc, .data.OO1, .data.OO2, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: res_spin_lock_arg, res_spin_lock_AA, res_spin_lock_cond_AA, res_spin_lock_mismatch_1, res_spin_lock_mismatch_2, res_spin_lock_irq_mismatch_1, res_spin_lock_irq_mismatch_2, res_spin_lock_ooo, res_spin_lock_ooo_irq, res_spin_lock_ooo_unlock, res_spin_lock_bad_off, res_spin_lock_var_off, res_spin_lock_no_lock_map, res_spin_lock_no_lock_kptr. Helper and kfunc calls: bpf_assert_range, bpf_core_cast, bpf_local_irq_save, bpf_map_lookup_elem, bpf_obj_new, bpf_res_spin_lock, bpf_res_spin_lock_irqsave, bpf_res_spin_unlock, bpf_res_spin_unlock_irqrestore, bpf_throw. Important structs/types visible in this file: arr_elem, bpf_spin_lock, bpf_res_spin_lock. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __failure, __msg("point to map value or allocated object"), __msg("AA deadlock detected"), __msg("unlock of different lock"), __success, __msg("bpf_res_spin_unlock cannot be out of order"), __msg("off 1 doesn't point to 'struct bpf_res_spin_lock' that is at 0"), __msg("R1 doesn't have constant offset. bpf_res_spin_lock has to be at the constant offset"), and 2 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `res_spin_lock_arg` and related routines such as `res_spin_lock_AA, res_spin_lock_cond_AA, res_spin_lock_mismatch_1, res_spin_lock_mismatch_2`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long value, u64 val, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, .data.A, .data.B, ?tc, .data.OO1, .data.OO2, and 1 more` programs, helper coverage for `bpf_assert_range, bpf_core_cast, bpf_local_irq_save, bpf_map_lookup_elem, bpf_obj_new, bpf_res_spin_lock, bpf_res_spin_lock_irqsave, bpf_res_spin_unlock, and 2 more`, and stable behavior of `res_spin_lock_arg, res_spin_lock_AA, res_spin_lock_cond_AA, res_spin_lock_mismatch_1, res_spin_lock_mismatch_2, res_spin_lock_irq_mismatch_1, and 8 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ringbuf_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ringbuf_bench.c

## Purpose

Ring-buffer benchmark producer that can use reserve/submit or direct output and queries ringbuf state for throughput tests.

## Important APIs, Types, and Functions

Attach sections: license, .maps. Map types: BPF_MAP_TYPE_RINGBUF. Important local functions/programs: get_flags, bench_ringbuf. Helper and kfunc calls: bpf_ringbuf_output, bpf_ringbuf_query, bpf_ringbuf_reserve, bpf_ringbuf_submit. Important structs/types visible in this file: none. Includes: stdbool.h, linux/bpf.h, stdint.h, bpf/bpf_helpers.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `get_flags` and related routines such as `bench_ringbuf`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_RINGBUF for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long sample_val, long sz, int i, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps` programs, helper coverage for `bpf_ringbuf_output, bpf_ringbuf_query, bpf_ringbuf_reserve, bpf_ringbuf_submit`, and stable behavior of `get_flags, bench_ringbuf` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ringbuf_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/security_bpf_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/security_bpf_map.c

## Purpose

Security hook fixture that observes or overrides security_bpf_map decisions and uses side maps to coordinate with fentry test programs.

## Important APIs, Types, and Functions

Attach sections: license, .maps, fmod_ret/security_bpf_map, fentry/bpf_fentry_test1. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_map_lookup_elem, bpf_map_update_elem. Important structs/types visible in this file: map. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u32 key, __u32 val1, __u32 val2, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, fmod_ret/security_bpf_map, fentry/bpf_fentry_test1` programs, helper coverage for `bpf_map_lookup_elem, bpf_map_update_elem`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/security_bpf_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg4_prog.c

## Purpose

cgroup sendmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields and including deny variants for policy tests.

## Important APIs, Types, and Functions

Attach sections: cgroup/sendmsg4, license. Map types: none. Important local functions/programs: sendmsg_v4_prog, sendmsg_v4_deny_prog. Helper and kfunc calls: bpf_htonl, bpf_htons. Important structs/types visible in this file: none. Includes: linux/stddef.h, linux/bpf.h, sys/socket.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_sockopt_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `sendmsg_v4_prog` and related routines such as `sendmsg_v4_deny_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/sendmsg4, license` programs, helper coverage for `bpf_htonl, bpf_htons`, and stable behavior of `sendmsg_v4_prog, sendmsg_v4_deny_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg4_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg6_prog.c

## Purpose

cgroup sendmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields and including deny variants for policy tests.

## Important APIs, Types, and Functions

Attach sections: cgroup/sendmsg6, license. Map types: none. Important local functions/programs: sendmsg_v6_prog, sendmsg_v6_v4mapped_prog, sendmsg_v6_wildcard_prog, sendmsg_v6_preserve_dst_prog, sendmsg_v6_deny_prog. Helper and kfunc calls: bpf_htonl, bpf_htons. Important structs/types visible in this file: none. Includes: linux/stddef.h, linux/bpf.h, sys/socket.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_sockopt_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `sendmsg_v6_prog` and related routines such as `sendmsg_v6_v4mapped_prog, sendmsg_v6_wildcard_prog, sendmsg_v6_preserve_dst_prog, sendmsg_v6_deny_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/sendmsg6, license` programs, helper coverage for `bpf_htonl, bpf_htons`, and stable behavior of `sendmsg_v6_prog, sendmsg_v6_v4mapped_prog, sendmsg_v6_wildcard_prog, sendmsg_v6_preserve_dst_prog, sendmsg_v6_deny_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg6_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg_unix_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg_unix_prog.c

## Purpose

cgroup sendmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields and including deny variants for policy tests.

## Important APIs, Types, and Functions

Attach sections: cgroup/sendmsg_unix, license. Map types: none. Important local functions/programs: sendmsg_unix_prog, sendmsg_unix_deny_prog. Helper and kfunc calls: bpf_cast_to_kern_ctx, bpf_core_cast, bpf_sock_addr_set_sun_path. Important structs/types visible in this file: none. Includes: vmlinux.h, string.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_kfuncs.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `sendmsg_unix_prog` and related routines such as `sendmsg_unix_deny_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __u32 unaddrlen, int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/sendmsg_unix, license` programs, helper coverage for `bpf_cast_to_kern_ctx, bpf_core_cast, bpf_sock_addr_set_sun_path`, and stable behavior of `sendmsg_unix_prog, sendmsg_unix_deny_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg_unix_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/set_global_vars.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/set_global_vars.c

## Purpose

Socket filter fixture driven by user-set global variables; it returns comparisons over scalar globals to test global data relocation and mutation.

## Important APIs, Types, and Functions

Attach sections: license, socket. Map types: none. Important local functions/programs: test_set_globals. Helper and kfunc calls: none. Important structs/types visible in this file: Struct, Struct3. Includes: bpf_experimental.h, bpf/bpf_helpers.h, bpf_misc.h, stdbool.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `test_set_globals`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __u16 filler, const __u16 filler2, u8 var_u8_l, u8 var_u8_h, __u16 var_u16, volatile __s8 a, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, socket` programs, helper coverage for `none`, and stable behavior of `test_set_globals` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/set_global_vars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/setget_sockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/setget_sockopt.c

## Purpose

Broad sockopt selftest program for LSM cgroup socket creation, cgroup getsockopt, and sockops callbacks across SOL_SOCKET, IP, IPv6, TCP, bind-to-device, MSS, and saved SYN options.

## Important APIs, Types, and Functions

Attach sections: lsm_cgroup/socket_post_create, cgroup/getsockopt, sockops, license. Map types: none. Important local functions/programs: sk_is_tcp, bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_socket_sockopt, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, bpf_test_tcp_sockopt, bpf_test_sockopt, binddev_test, test_tcp_maxseg, test_tcp_saved_syn, BPF_PROG, _getsockopt, skops_sockopt. Helper and kfunc calls: bpf_core_cast, bpf_getsockopt, bpf_loop, bpf_setsockopt, bpf_skc_to_tcp_sock, bpf_strncmp, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, bpf_test_socket_sockopt, bpf_test_sockopt, bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_tcp_sockopt. Important structs/types visible in this file: sockopt_test, loop_ctx. Includes: vmlinux.h, bpf_tracing_net.h, bpf/bpf_core_read.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `sk_is_tcp` and related routines such as `bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_socket_sockopt, bpf_test_ip_sockopt`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int nr_listen, int nr_passive, int nr_active, int nr_connect, int nr_binddev, int nr_socket_post_create, int nr_fin_wait1, int opt, int new, int restore, and 8 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `lsm_cgroup/socket_post_create, cgroup/getsockopt, sockops, license` programs, helper coverage for `bpf_core_cast, bpf_getsockopt, bpf_loop, bpf_setsockopt, bpf_skc_to_tcp_sock, bpf_strncmp, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, and 5 more`, and stable behavior of `sk_is_tcp, bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_socket_sockopt, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, and 8 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/setget_sockopt.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sk_storage_omem_uncharge.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sk_storage_omem_uncharge.c

## Purpose

Socket-storage memory accounting test that creates storage and observes free/destructor hooks to ensure omem uncharge behavior.

## Important APIs, Types, and Functions

Attach sections: .maps, fexit/bpf_sk_storage_free, fentry/inet6_sock_destruct, license. Map types: BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_sk_storage_get. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf_tracing_net.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf/bpf_core_read.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int cookie_found, __u64 cookie, __u32 omem, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, fexit/bpf_sk_storage_free, fentry/inet6_sock_destruct, license` programs, helper coverage for `bpf_sk_storage_get`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sk_storage_omem_uncharge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/skb_load_bytes.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/skb_load_bytes.c

## Purpose

Small tc skb helper verifier/runtime fixture for packet byte load/store behavior and packet-end bounds handling.

## Important APIs, Types, and Functions

Attach sections: license, tc. Map types: none. Important local functions/programs: skb_process. Helper and kfunc calls: bpf_skb_load_bytes. Important structs/types visible in this file: none. Includes: linux/bpf.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `skb_process`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __u32 load_offset, int test_result, char buf[16], which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, tc` programs, helper coverage for `bpf_skb_load_bytes`, and stable behavior of `skb_process` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/skb_load_bytes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/skb_pkt_end.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/skb_pkt_end.c

## Purpose

Small tc skb helper verifier/runtime fixture for packet byte load/store behavior and packet-end bounds handling.

## Important APIs, Types, and Functions

Attach sections: tc, license. Map types: none. Important local functions/programs: main_prog. Helper and kfunc calls: bpf_skb_store_bytes. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_core_read.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `main_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __u8 proto, int urg_ptr, u32 offset, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `tc, license` programs, helper coverage for `bpf_skb_store_bytes`, and stable behavior of `main_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/skb_pkt_end.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog.c

## Purpose

Socket destroy test that records target cookies, finds sockets from connect/iterator contexts, and calls bpf_sock_destroy on matching TCP/UDP IPv6 sockets.

## Important APIs, Types, and Functions

Attach sections: .maps, cgroup/connect6, iter/tcp, iter/udp, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: bpf_sock_destroy, sock_connect, iter_tcp6_client, iter_tcp6_server, iter_udp6_client, iter_udp6_server. Helper and kfunc calls: bpf_get_socket_cookie, bpf_map_lookup_elem, bpf_map_update_elem, bpf_skc_to_tcp6_sock, bpf_sock_destroy. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_tracing_net.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_sock_destroy` and related routines such as `sock_connect, iter_tcp6_client, iter_tcp6_server, iter_udp6_client`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u64 sock_cookie, int key, __u32 keyc, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, cgroup/connect6, iter/tcp, iter/udp, license` programs, helper coverage for `bpf_get_socket_cookie, bpf_map_lookup_elem, bpf_map_update_elem, bpf_skc_to_tcp6_sock, bpf_sock_destroy`, and stable behavior of `bpf_sock_destroy, sock_connect, iter_tcp6_client, iter_tcp6_server, iter_udp6_client, iter_udp6_server` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog_fail.c

## Purpose

Negative test proving bpf_sock_destroy is rejected from an unsupported tcp_destroy_sock tracepoint context.

## Important APIs, Types, and Functions

Attach sections: license, tp_btf/tcp_destroy_sock. Map types: none. Important local functions/programs: bpf_sock_destroy, BPF_PROG. Helper and kfunc calls: bpf_sock_destroy. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("calling kernel function bpf_sock_destroy is not allowed"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_sock_destroy` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, tp_btf/tcp_destroy_sock` programs, helper coverage for `bpf_sock_destroy`, and stable behavior of `bpf_sock_destroy, BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_iter_batch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_iter_batch.c

## Purpose

Socket iterator batch test for TCP/UDP sockets that writes loopback reuse data and can destroy sockets matching iterator criteria.

## Important APIs, Types, and Functions

Attach sections: iter/tcp, iter/udp, license. Map types: none. Important local functions/programs: ipv6_addr_loopback, ipv4_addr_loopback, iter_tcp_soreuse, iter_tcp_destroy, iter_udp_soreuse. Helper and kfunc calls: bpf_core_cast, bpf_get_socket_cookie, bpf_htonl, bpf_ntohl, bpf_seq_write, bpf_sock_destroy. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf/bpf_endian.h, bpf_tracing_net.h, bpf_kfuncs.h, test_jhash.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `ipv6_addr_loopback` and related routines such as `ipv4_addr_loopback, iter_tcp_soreuse, iter_tcp_destroy, iter_udp_soreuse`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include volatile const __u16 ports[2], __u64 sock_cookie, int idx, volatile const __u64 destroy_cookie, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `iter/tcp, iter/udp, license` programs, helper coverage for `bpf_core_cast, bpf_get_socket_cookie, bpf_htonl, bpf_ntohl, bpf_seq_write, bpf_sock_destroy`, and stable behavior of `ipv6_addr_loopback, ipv4_addr_loopback, iter_tcp_soreuse, iter_tcp_destroy, iter_udp_soreuse` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_iter_batch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_ops_get_sk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_ops_get_sk.c

## Purpose

Sockops context fixture exercising direct access to sk fields in multiple sockops programs.

## Important APIs, Types, and Functions

Attach sections: sockops, license. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

Global data variables include int bug_detected, int null_seen, int field_bug_detected, int field_null_seen, int diff_reg_bug_detected, int diff_reg_null_seen, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest.
For this file specifically, useful signals include presence of `sockops, license` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_ops_get_sk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/socket_cookie_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/socket_cookie_prog.c

## Purpose

Socket cookie propagation test that stores cookies in sk_storage from connect/sockops/fexit paths and validates stable bpf_get_socket_cookie values.

## Important APIs, Types, and Functions

Attach sections: .maps, cgroup/connect6, sockops, fexit/inet_stream_connect, license. Map types: BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: set_cookie, update_cookie_sockops, BPF_PROG. Helper and kfunc calls: bpf_get_socket_cookie, bpf_sk_storage_get. Important structs/types visible in this file: socket_cookie. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf/bpf_tracing.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `set_cookie` and related routines such as `update_cookie_sockops, BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u64 cookie_key, __u32 cookie_value, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, cgroup/connect6, sockops, fexit/inet_stream_connect, license` programs, helper coverage for `bpf_get_socket_cookie, bpf_sk_storage_get`, and stable behavior of `set_cookie, update_cookie_sockops, BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/socket_cookie_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_parse_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_parse_prog.c

## Purpose

Sockmap/sk_skb/sk_msg fixture for parser, verdict, and redirect tests using sockmap and array maps.

## Important APIs, Types, and Functions

Attach sections: sk_skb1, license. Map types: none. Important local functions/programs: bpf_prog1. Helper and kfunc calls: bpf_prog1, bpf_skb_pull_data. Important structs/types visible in this file: none. Includes: linux/bpf.h, bpf/bpf_helpers.h, bpf/bpf_endian.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_prog1`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int err, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `sk_skb1, license` programs, helper coverage for `bpf_prog1, bpf_skb_pull_data`, and stable behavior of `bpf_prog1` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_parse_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_tcp_msg_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_tcp_msg_prog.c

## Purpose

Sockmap/sk_skb/sk_msg fixture for parser, verdict, and redirect tests using sockmap and array maps.

## Important APIs, Types, and Functions

Attach sections: sk_msg1, license. Map types: none. Important local functions/programs: bpf_prog1. Helper and kfunc calls: bpf_prog1. Important structs/types visible in this file: none. Includes: linux/bpf.h, bpf/bpf_helpers.h, bpf/bpf_endian.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_prog1`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `sk_msg1, license` programs, helper coverage for `bpf_prog1`, and stable behavior of `bpf_prog1` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_tcp_msg_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_verdict_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_verdict_prog.c

## Purpose

Sockmap/sk_skb/sk_msg fixture for parser, verdict, and redirect tests using sockmap and array maps.

## Important APIs, Types, and Functions

Attach sections: .maps, sk_skb2, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_SOCKMAP. Important local functions/programs: bpf_prog2. Helper and kfunc calls: bpf_prog2, bpf_sk_redirect_map. Important structs/types visible in this file: none. Includes: linux/bpf.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_prog2`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_SOCKMAP for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u32 lport, __u32 rport, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, sk_skb2, license` programs, helper coverage for `bpf_prog2, bpf_sk_redirect_map`, and stable behavior of `bpf_prog2` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockmap_verdict_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_inherit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_inherit.c

## Purpose

cgroup sockopt fixture focused on getsockopt/setsockopt inheritance, multi-program ordering, QoS-to-congestion-control translation, or sk_storage-backed state.

## Important APIs, Types, and Functions

Attach sections: license, .maps, cgroup/getsockopt, cgroup/setsockopt. Map types: BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: _getsockopt, _setsockopt. Helper and kfunc calls: bpf_sk_storage_get. Important structs/types visible in this file: sockopt_inherit. Includes: linux/bpf.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `_getsockopt` and related routines such as `_setsockopt`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __s32 page_size, __u8 val, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, cgroup/getsockopt, cgroup/setsockopt` programs, helper coverage for `bpf_sk_storage_get`, and stable behavior of `_getsockopt, _setsockopt` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_inherit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_multi.c

## Purpose

cgroup sockopt fixture focused on getsockopt/setsockopt inheritance, multi-program ordering, QoS-to-congestion-control translation, or sk_storage-backed state.

## Important APIs, Types, and Functions

Attach sections: license, cgroup/getsockopt, cgroup/setsockopt. Map types: none. Important local functions/programs: _getsockopt_child, _getsockopt_parent, _setsockopt. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: netinet/in.h, linux/bpf.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `_getsockopt_child` and related routines such as `_getsockopt_parent, _setsockopt`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __s32 page_size, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, cgroup/getsockopt, cgroup/setsockopt` programs, helper coverage for `none`, and stable behavior of `_getsockopt_child, _getsockopt_parent, _setsockopt` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_qos_to_cc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_qos_to_cc.c

## Purpose

cgroup sockopt fixture focused on getsockopt/setsockopt inheritance, multi-program ordering, QoS-to-congestion-control translation, or sk_storage-backed state.

## Important APIs, Types, and Functions

Attach sections: license, cgroup/setsockopt. Map types: none. Important local functions/programs: sockopt_qos_to_cc. Helper and kfunc calls: bpf_getsockopt, bpf_setsockopt, bpf_strncmp. Important structs/types visible in this file: none. Includes: bpf_tracing_net.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `sockopt_qos_to_cc`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __s32 page_size, const char cc_reno[TCP_CA_NAME_MAX], const char cc_cubic[TCP_CA_NAME_MAX], char buf[TCP_CA_NAME_MAX], which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, cgroup/setsockopt` programs, helper coverage for `bpf_getsockopt, bpf_setsockopt, bpf_strncmp`, and stable behavior of `sockopt_qos_to_cc` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_qos_to_cc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_sk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_sk.c

## Purpose

cgroup sockopt fixture focused on getsockopt/setsockopt inheritance, multi-program ordering, QoS-to-congestion-control translation, or sk_storage-backed state.

## Important APIs, Types, and Functions

Attach sections: license, .maps, cgroup/getsockopt, cgroup/setsockopt. Map types: BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: _getsockopt, _setsockopt. Helper and kfunc calls: bpf_get_netns_cookie, bpf_getsockopt, bpf_sk_storage_get, bpf_tcp_sock. Important structs/types visible in this file: sockopt_sk. Includes: string.h, linux/tcp.h, linux/bpf.h, netinet/in.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `_getsockopt` and related routines such as `_setsockopt`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int page_size, __u8 val, char saved_syn[60], which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, cgroup/getsockopt, cgroup/setsockopt` programs, helper coverage for `bpf_get_netns_cookie, bpf_getsockopt, bpf_sk_storage_get, bpf_tcp_sock`, and stable behavior of `_getsockopt, _setsockopt` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sockopt_sk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_ips.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_ips.c

## Purpose

Stack trace map fixture for kprobe, kprobe.multi, raw tracepoint, fentry/fexit, or sched_switch contexts, recording stack IDs and stack bytes into maps.

## Important APIs, Types, and Functions

Attach sections: .maps, kprobe, kprobe.multi, raw_tp/bpf_testmod_test_read, fentry/bpf_testmod_stacktrace_test, fexit/bpf_testmod_stacktrace_test, license. Map types: BPF_MAP_TYPE_STACK_TRACE. Important local functions/programs: unused, kprobe_test, kprobe_multi_test, rawtp_test, fentry_test, fexit_test. Helper and kfunc calls: bpf_get_stackid. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `unused` and related routines such as `kprobe_test, kprobe_multi_test, rawtp_test, fentry_test`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_STACK_TRACE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u32 stack_key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, kprobe, kprobe.multi, raw_tp/bpf_testmod_test_read, fentry/bpf_testmod_stacktrace_test, fexit/bpf_testmod_stacktrace_test, and 1 more` programs, helper coverage for `bpf_get_stackid`, and stable behavior of `unused, kprobe_test, kprobe_multi_test, rawtp_test, fentry_test, fexit_test` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_ips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_map.c

## Purpose

Stack trace map fixture for kprobe, kprobe.multi, raw tracepoint, fentry/fexit, or sched_switch contexts, recording stack IDs and stack bytes into maps.

## Important APIs, Types, and Functions

Attach sections: .maps, tracepoint/sched/sched_switch, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_STACK_TRACE. Important local functions/programs: oncpu. Helper and kfunc calls: bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem, bpf_map_update_elem. Important structs/types visible in this file: sched_switch_args. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `oncpu`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_STACK_TRACE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include char prev_comm[TASK_COMM_LEN], int prev_pid, int prev_prio, char next_comm[TASK_COMM_LEN], int next_pid, int next_prio, __u32 stack_id, __u32 max_len, __u32 key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, tracepoint/sched/sched_switch, license` programs, helper coverage for `bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem, bpf_map_update_elem`, and stable behavior of `oncpu` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_map_skip.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_map_skip.c

## Purpose

Stack trace map fixture for kprobe, kprobe.multi, raw tracepoint, fentry/fexit, or sched_switch contexts, recording stack IDs and stack bytes into maps.

## Important APIs, Types, and Functions

Attach sections: .maps, tracepoint/sched/sched_switch, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_STACK_TRACE. Important local functions/programs: oncpu. Helper and kfunc calls: bpf_get_current_pid_tgid, bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem, bpf_map_update_elem. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `oncpu`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_STACK_TRACE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int pid, int control, int failed, __u32 max_len, __u32 key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, tracepoint/sched/sched_switch, license` programs, helper coverage for `bpf_get_current_pid_tgid, bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem, bpf_map_update_elem`, and stable behavior of `oncpu` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/stacktrace_map_skip.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_failure1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_failure1.c

## Purpose

String kfunc runtime-error tests for NULL arguments, expecting USER_PTR_ERR-style return values from strcmp/strstr/strlen families.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: none. Helper and kfunc calls: bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, bpf_strncasestr, bpf_strnchr, bpf_strnlen, bpf_strnstr, bpf_strrchr, bpf_strspn, bpf_strstr. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, linux/limits.h, bpf_misc.h, errno.h.

Verifier/test annotations present: __retval(USER_PTR_ERR) int test_strcmp_null1(void *ctx) { return bpf_strcmp(NULL, "hello"), __retval(USER_PTR_ERR)int test_strcmp_null2(void *ctx) { return bpf_strcmp("hello", NULL), __retval(USER_PTR_ERR) int test_strcasecmp_null1(void *ctx) { return bpf_strcasecmp(NULL, "HELLO"), __retval(USER_PTR_ERR)int test_strcasecmp_null2(void *ctx) { return bpf_strcasecmp("HELLO", NULL), __retval(USER_PTR_ERR)int test_strncasecmp_null1(void *ctx) { return bpf_strncasecmp(NULL, "HELLO", 5), __retval(USER_PTR_ERR)int test_strncasecmp_null2(void *ctx) { return bpf_strncasecmp("HELLO", NULL, 5), __retval(USER_PTR_ERR)int test_strchr_null(void *ctx) { return bpf_strchr(NULL, 'a'), __retval(USER_PTR_ERR)int test_strchrnul_null(void *ctx) { return bpf_strchrnul(NULL, 'a'), and 64 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, and 7 more`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_failure1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_failure2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_failure2.c

## Purpose

String kfunc verifier failure tests for invalid pointer classes and argument shapes across the same string helper family.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: none. Helper and kfunc calls: bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, bpf_strncasestr, bpf_strnchr, bpf_strnlen, bpf_strnstr, bpf_strrchr, bpf_strspn, bpf_strstr. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, linux/limits.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

Global data variables include char long_str[XATTR_SIZE_MAX + 1], which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics.

## Test Signals

the declared attach sections should load and attach in the owning selftest.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, and 7 more`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_failure2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_success.c

## Purpose

Positive string kfunc test table comparing expected return values for strcmp, strcasecmp, strlen, strchr, strstr, strspn, and related bounded variants.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: none. Helper and kfunc calls: bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, bpf_strncasestr, bpf_strnchr, bpf_strnlen, bpf_strnstr, bpf_strrchr, bpf_strspn, bpf_strstr. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf_misc.h, errno.h.

Verifier/test annotations present: __success, __retval(retval). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, and 7 more`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_bench.c

## Purpose

Benchmark comparing hand-written string comparison with bpf_strncmp helper on syscall tracepoints.

## Important APIs, Types, and Functions

Attach sections: license, tp/syscalls/sys_enter_getpgid. Map types: none. Important local functions/programs: local_strncmp, strncmp_no_helper, strncmp_helper. Helper and kfunc calls: bpf_strncmp. Important structs/types visible in this file: none. Includes: linux/types.h, linux/bpf.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `local_strncmp` and related routines such as `strncmp_no_helper, strncmp_helper`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include const char target[STRNCMP_STR_SZ], long hits, char str[STRNCMP_STR_SZ], int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, tp/syscalls/sys_enter_getpgid` programs, helper coverage for `bpf_strncmp`, and stable behavior of `local_strncmp, strncmp_no_helper, strncmp_helper` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_test.c

## Purpose

bpf_strncmp correctness and verifier fixture, including valid comparisons plus bad size, writable target, and non-NUL-terminated cases.

## Important APIs, Types, and Functions

Attach sections: license, ?tp/syscalls/sys_enter_nanosleep. Map types: none. Important local functions/programs: do_strncmp, strncmp_bad_not_const_str_size, strncmp_bad_writable_target, strncmp_bad_not_null_term_target. Helper and kfunc calls: bpf_get_current_pid_tgid, bpf_strncmp. Important structs/types visible in this file: none. Includes: stdbool.h, linux/types.h, linux/bpf.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `do_strncmp` and related routines such as `strncmp_bad_not_const_str_size, strncmp_bad_writable_target, strncmp_bad_not_null_term_target`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include const char target[STRNCMP_STR_SZ], char str[STRNCMP_STR_SZ], int cmp_ret, int target_pid, const char no_str_target[STRNCMP_STR_SZ], char writable_target[STRNCMP_STR_SZ], which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, ?tp/syscalls/sys_enter_nanosleep` programs, helper coverage for `bpf_get_current_pid_tgid, bpf_strncmp`, and stable behavior of `do_strncmp, strncmp_bad_not_const_str_size, strncmp_bad_writable_target, strncmp_bad_not_null_term_target` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.c

## Purpose

Configuration wrapper for strobemeta.h that sets map/string/int limits and relies on full LLVM unrolling to build the generated strobemeta BPF program.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: strobemeta.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.c -->
