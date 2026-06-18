<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fail__incompl_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fail__incompl_ops.c

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `BPF_PROG`, `bpf_qdisc_test_enqueue`, `bpf_qdisc_test_dequeue`, `bpf_qdisc_test_reset`, `bpf_qdisc_test_destroy`
- BPF helpers/kfunc-like calls: `bpf_qdisc_skb_drop`

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_experimental.h`, `bpf_qdisc_common.h`. Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test. Helper availability and license restrictions matter for `bpf_qdisc_skb_drop`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_fail__incompl_ops.c -->
