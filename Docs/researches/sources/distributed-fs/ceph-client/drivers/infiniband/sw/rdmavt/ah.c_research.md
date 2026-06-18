<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.c

## Purpose

Implements rdmavt address-handle validation, creation, modification, query, and destruction.

## Important APIs, Types, And Functions

`rvt_check_ah()` validates port, static rate, GRH SGID index, and delegates to an optional driver callback. `rvt_create_ah()`, `rvt_destroy_ah()`, `rvt_modify_ah()`, and `rvt_query_ah()` implement RDMA core AH ops. `rvt_check_ah` is exported for driver use.

## Control Flow

Create validates AH attrs, checks the per-device max AH count under `n_ahs_lock`, copies attributes into the rdmavt AH object, and notifies the driver if requested. Destroy decrements the count and destroys copied AH attr resources. Modify revalidates and replaces attrs. Query copies stored attrs out.

## State And Persistence Behavior

AH state is local in `struct rvt_ah`, primarily an `rdma_ah_attr` copy. Device state tracks `n_ahs_allocated`. No hardware/backend state is directly programmed here except optional driver callbacks.

## Dependencies And Integration Points

Depends on RDMA AH helpers, `ib_query_port()`, rdmavt device data, and optional driver function table hooks.

## Risks And Edge Cases

`rvt_modify_ah()` assigns `ah->attr = *ah_attr` rather than using deep-copy helper, so embedded resources must be safe for value assignment in this context. Port validity is checked after `ib_query_port()` call using `port_num`, so invalid ports depend on query behavior. Count accounting must match create/destroy paths.

## Test Signals

Test invalid port/rate/SGID index, driver callback rejection, AH max exhaustion, create/destroy count accounting, modify/query round trips, and notify_new_ah invocation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.c -->
