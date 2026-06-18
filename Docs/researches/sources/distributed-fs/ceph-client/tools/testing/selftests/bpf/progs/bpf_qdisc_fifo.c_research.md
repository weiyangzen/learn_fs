<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fifo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fifo.c

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops/bpf_fifo_enqueue`, `struct_ops/bpf_fifo_dequeue`, `struct_ops/bpf_fifo_init`, `struct_ops/bpf_fifo_reset`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `BPF_PROG`, `bpf_fifo_enqueue`, `bpf_fifo_dequeue`, `bpf_fifo_init`, `bpf_fifo_reset`, `bpf_fifo_destroy`
- BPF helpers/kfunc-like calls: `bpf_for`, `bpf_kfree_skb`, `bpf_kptr_xchg`, `bpf_list_pop_front`, `bpf_list_push_back`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_qdisc_bstats_update`, `bpf_qdisc_skb_drop`, `bpf_spin_lock`, `bpf_spin_unlock`
- Mutable globals/test result fields: `init_called`

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `init_called` Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_experimental.h`, `bpf_qdisc_common.h`. Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test. Helper availability and license restrictions matter for `bpf_for`, `bpf_kfree_skb`, `bpf_kptr_xchg`, `bpf_list_pop_front`, `bpf_list_push_back`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_qdisc_bstats_update`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `init_called` to confirm the exercised path ran. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fifo.c -->
