<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_priv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_priv.h

## Purpose

`cma_priv.h` defines the private RDMA CMA state machine and per-ID state used internally by `cma.c` and related CMA support files. It also declares the CMA configfs hooks and the small set of CMA device accessors needed by `cma_configfs.c`.

## Important APIs, types, and functions

`enum rdma_cm_state` enumerates the internal lifecycle states: idle, address query/resolved/bound, route query/resolved, connect, disconnect, listen, device removal, destroying, and IB service address-info query/resolved. `struct rdma_id_private` embeds the public `struct rdma_cm_id` and adds bind-list membership, device/listen list nodes, multicast list, internal child-ID marker, state, node-type restriction, spinlock, QP mutex, handler mutex, completion/refcount lifetime management, backlog, SA query state, transport CM ID union, sequence number, QKey, QP number, options, SRQ/TOS/timer/reuse/AF-only flags, selected GID type, resource tracking entry, and ECE data.

The header conditionally declares or stubs `cma_configfs_init()` and `cma_configfs_exit()`. It also declares `cma_dev_get()`, `cma_dev_put()`, `cma_enum_devices_by_ibdev()`, default RoCE GID type/TOS getters and setters, and `cma_get_ib_dev()`.

## Control flow

The header itself has no runtime flow, but it is the contract for `cma.c` transitions. New IDs start at `RDMA_CM_IDLE`; bind, address, route, listen, connect, and destroy paths move through the enum with guarded compare-exchange helpers. `handler_mutex` serializes callbacks and destroy, `qp_mutex` serializes QP-related options and pointer changes, and `lock` protects state fields that can be touched outside handler context. List-node unions let the same ID storage represent either device-list membership or wildcard-listen membership and either listen-list head or child-list entry depending on ID role.

## State and persistence

All fields are in-memory runtime state. The private ID owns references to net namespaces, CMA devices, lower CM IDs, SA queries, path/service records, multicast records, and resource-tracker entries through code in `cma.c`. There is no disk persistence. The configfs stubs make CMA buildable without configfs support while preserving the same initialization call sites.

## Dependencies and integration points

The declarations depend on RDMA CM, IB verbs/GID types, SA query, resource tracking, and configfs Kconfig. `cma.c` is the main user, `cma_configfs.c` uses the device accessors, and `cma_trace.h` reads fields such as resource ID, addresses, TOS, and QP number. External drivers should not consume this header for data-path behavior; it is an RDMA core internal contract.

## Risks

Because `rdma_id_private` is shared across many asynchronous contexts, field ownership must remain clear. Reusing list-head storage through unions saves memory but makes role transitions fragile: an ID must not be placed on incompatible lists at the same time. Adding states requires auditing every `cma_comp_exch()` and event handler. Adding flags or timers requires correct locking under `qp_mutex`, the spinlock, or `handler_mutex`. The configfs stubs must stay ABI-compatible with the real hooks so `cma.c` cleanup remains simple.

## Test signals

Build coverage with configfs both enabled and disabled validates the conditional declarations. Runtime signals are mostly exercised through `cma.c`: legal state transitions succeed, invalid API ordering returns `-EINVAL`, destroy waits for outstanding refs, child listen IDs and device IDs leave all lists, and tracepoints show coherent private-state values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_priv.h -->
