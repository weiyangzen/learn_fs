<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fq.c

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- BPF sections: `.struct_ops`, `license`, `.maps`, `.maps`, `struct_ops/bpf_fq_enqueue`, `struct_ops/bpf_fq_dequeue`, `struct_ops/bpf_fq_reset`, `struct_ops/bpf_fq_init`, `struct_ops`, `.struct_ops`
- Maps: `fq_nonprio_flows`, `fq_prio_flows`
- Important functions/callbacks: `bpf_kptr_xchg_back`, `skbn_tstamp_less`, `fn_time_next_packet_less`, `fq_flows_add_head`, `fq_flows_add_tail`, `fq_flows_remove_front`, `fq_flows_is_empty`, `fq_flow_set_detached`, `fq_flow_is_detached`, `sk_listener`, `fq_new_flow`, `fq_classify`, `fq_packet_beyond_horizon`, `BPF_PROG`, `fq_unset_throttled_flows`, `fq_flow_set_throttled`, `fq_check_throttled`, `fq_dequeue_nonprio_flows`, `fq_remove_flows_in_list`, `fq_gc_candidate`, `fq_remove_flows`, `fq_gc`, and 5 more
- BPF helpers/kfunc-like calls: `bpf_for`, `bpf_for_each_map_elem`, `bpf_jiffies64`, `bpf_kptr_xchg`, `bpf_kptr_xchg_back`, `bpf_ktime_get_ns`, `bpf_list_pop_front`, `bpf_list_push_back`, `bpf_list_push_front`, `bpf_loop`, `bpf_map_delete_elem`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_qdisc_bstats_update`, `bpf_qdisc_skb_drop`, `bpf_qdisc_watchdog_schedule`, `bpf_rbtree_add`, `bpf_rbtree_first`, `bpf_rbtree_remove`, `bpf_refcount_acquire`, and 3 more

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `fq_nonprio_flows`, `fq_prio_flows` Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Includes `vmlinux.h`, `errno.h`, `bpf/bpf_helpers.h`, `bpf_experimental.h`, `bpf_qdisc_common.h`. Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test. Helper availability and license restrictions matter for `bpf_for`, `bpf_for_each_map_elem`, `bpf_jiffies64`, `bpf_kptr_xchg`, `bpf_kptr_xchg_back`, `bpf_ktime_get_ns`, `bpf_list_pop_front`, `bpf_list_push_back`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `fq_nonprio_flows`, `fq_prio_flows` provide state validation. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fq.c -->
