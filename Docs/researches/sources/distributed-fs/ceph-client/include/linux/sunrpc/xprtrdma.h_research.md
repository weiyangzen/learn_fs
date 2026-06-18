# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtrdma.h

Purpose: exposes client RPC/RDMA transport constants and memory-registration strategy IDs, including values that form part of a kernel/user-space API.

Important APIs and types: slot table bounds are `RPCRDMA_MIN_SLOT_TABLE`, `RPCRDMA_DEF_SLOT_TABLE`, and `RPCRDMA_MAX_SLOT_TABLE`. Inline thresholds are `RPCRDMA_MIN_INLINE`, `RPCRDMA_DEF_INLINE`, and `RPCRDMA_MAX_INLINE`. `enum rpcrdma_memreg` lists registration strategies from bounce buffers through FRWR and physical mappings, ending at `RPCRDMA_LAST`.

Control flow: RPC/RDMA client setup and module parameters use these constants to size request slots, inline thresholds, and choose memory registration mode.

State and persistence: no state is stored here; selected values influence runtime transport state elsewhere.

Dependencies and integration points: included by RPC/RDMA client code and user-visible configuration paths; comments warn that memory registration strategy numbers must not be removed.

Risks and test signals: risks include breaking user-space ABI by renumbering strategies, invalid inline thresholds, and slot table values that exceed RDMA resources. Test RPC/RDMA mounts with each supported memreg mode, threshold boundary values, and module parameter compatibility.
