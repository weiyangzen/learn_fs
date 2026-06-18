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
