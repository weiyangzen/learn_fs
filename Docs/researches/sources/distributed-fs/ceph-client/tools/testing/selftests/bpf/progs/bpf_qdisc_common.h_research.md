<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_common.h

## Purpose

BPF qdisc struct_ops selftest source for programmable queueing discipline callbacks, packet queue state, and scheduler behavior.

## Important APIs, Types, and Functions

- This file is primarily declarations or C type fixtures; its important API surface is the exported type/function symbols compiled into BTF.

## Control Flow and Data Flow

The qdisc core invokes struct_ops callbacks for init, enqueue, dequeue, reset, and optional helpers. Implementations allocate BPF objects, manipulate list/rbtree queues under BPF spin locks, update qdisc statistics, and release packet/object references.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Queue state persists in BPF-owned kptr objects, list/rbtree nodes, packet references, and private qdisc configuration until reset/destroy.

## Dependencies and Integration Points

Depends on experimental BPF qdisc struct_ops, kptr/list/rbtree helpers, packet drop/free helpers, and `bpf_qdisc_common.h` constants.

## Risks and Edge Cases

Packet and kptr ownership is subtle: leaks, double drops, lock misuse, or global queue sharing between instances can invalidate the qdisc test.

## Test Signals

Load/attach success and verifier log expectations are primary signals. tc/struct_ops tests should enqueue/dequeue packets, update byte/packet stats, and verify reset/destroy cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_qdisc_common.h -->
