<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/iotlb.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/iotlb.c

## Purpose
This file implements a generic software IOTLB mapping cache used by vhost and vringh code. It stores IOVA-to-host-address ranges in an interval tree plus an insertion-order list for optional retirement.

## Important APIs, types, and functions
Exported functions include `vhost_iotlb_map_free`, `vhost_iotlb_add_range_ctx`, `vhost_iotlb_add_range`, `vhost_iotlb_del_range`, `vhost_iotlb_init`, `vhost_iotlb_alloc`, `vhost_iotlb_reset`, `vhost_iotlb_free`, `vhost_iotlb_itree_first`, and `vhost_iotlb_itree_next`. `INTERVAL_TREE_DEFINE` creates static interval-tree helpers for `struct vhost_iotlb_map`.

## Control flow
Initialization sets an empty cached rb-root, map limit, flags, count, and list head. Add validates `last >= start`, splits the full `[0, ULONG_MAX]` range to avoid size overflow, optionally retires the oldest mapping when the limit is reached with `VHOST_IOTLB_FLAG_RETIRE`, allocates a map, inserts it into the interval tree, and appends it to the list. Delete repeatedly finds and frees overlapping mappings. Reset deletes the entire IOVA range.

## State and persistence behavior
State lives in the caller-owned or allocated `struct vhost_iotlb`: interval-tree root, FIFO list, map count, limit, and flags. Each map stores start, last, size, translated address, permissions, and opaque context. No persistence exists outside memory.

## Dependencies and integration points
The code depends on `linux/vhost_iotlb.h`, slab allocation, module exports, and Linux interval tree infrastructure. It is consumed by vhost core, vDPA, vringh, or tests that need software IOTLB lookups.

## Risks and test signals
Risks include overlapping additions not being rejected, FIFO retirement semantics surprising callers, atomic allocation failure, and full-range split correctness. Test signals include add/delete overlap queries, limit-retire behavior, reset/free idempotence, full-range mapping split into two entries, permission propagation, opaque pointer preservation, and interval iteration ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/iotlb.c -->
