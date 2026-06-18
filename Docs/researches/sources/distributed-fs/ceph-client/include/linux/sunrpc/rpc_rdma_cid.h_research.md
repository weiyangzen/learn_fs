# sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma_cid.h

Purpose: defines a shared completion identifier structure for client and server RPC/RDMA transports.

Important APIs and types: `struct rpc_rdma_cid` stores `ci_queue_id` and `ci_completion_id`, enough to correlate a completion event with a completion queue and a posted send/receive/work request.

Control flow: transport code initializes a CID before posting RDMA work and later uses it in completion handling, tracing, and error messages.

State and persistence: CID values are runtime diagnostics/correlation state; they are not persistent and are generally scoped to a transport's completion-id sequence.

Dependencies and integration points: included by RPC/RDMA client and server headers, especially `svc_rdma.h`.

Risks and test signals: risks include ID reuse ambiguity, uninitialized IDs on error completions, and queue ID mismatch after resource recreation. Test with RDMA send/recv completions, CQ teardown, error tracing, and reconnects.
