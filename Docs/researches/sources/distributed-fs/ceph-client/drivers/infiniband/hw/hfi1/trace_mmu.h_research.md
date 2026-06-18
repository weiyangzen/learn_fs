# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_mmu.h

## Purpose

`trace_mmu.h` defines tracepoints for the HFI1 MMU interval/rbtree tracking layer. These events expose registration, lookup, invalidation, eviction, and release of MMU range nodes.

## Important Events

`hfi1_mmu_rb_template` captures node address, length, and kref refcount. It instantiates `hfi1_mmu_rb_insert`, `hfi1_mmu_mem_invalidate`, `hfi1_mmu_rb_evict`, and `hfi1_mmu_release_node`. `hfi1_mmu_rb_search` records lookup address and length.

## Control Flow and State

The tracepoints observe MMU tracking operations and do not mutate state. Refcount is read with `kref_read()` to make ownership/lifetime visible in traces.

## Dependencies and Integration Points

The header depends on `struct mmu_rb_node`, krefs, and tracepoint APIs. It integrates with memory registration/invalidation code, which indirectly matters for RDMA and expected receive paths because stale or invalid memory mappings must not remain programmed in hardware.

## Risks and Test Signals

Risks are primarily diagnostic drift: if node lifetime or refcounting changes, trace output must still reflect meaningful state. Tests should exercise node insert/search/invalidate/evict/release and verify that refcounts and address ranges match expected memory-region lifetime.
