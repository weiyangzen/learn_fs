# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.h

## Purpose

`ib_srpt.h` defines SRPT target constants, command/channel state machines, and object layouts shared by SRPT connection management, RDMA I/O, MAD discovery, and target-core configfs integration.

## Important APIs, Types, and Functions

The header defines SRP target discovery constants, login flag masks, solicited-notification bits, task-management statuses, command task attributes, queue-size bounds, request/response size bounds, immediate-data limits, and default RDMA limits. Important types include `srpt_command_state`, `rdma_ch_state`, `srpt_ioctx`, `srpt_recv_ioctx`, `srpt_rw_ctx`, `srpt_send_ioctx`, `srpt_rdma_ch`, `srpt_nexus`, `srpt_port_attrib`, `srpt_tpg`, `srpt_port_id`, `srpt_port`, and `srpt_device`.

## Control Flow

The header has no executable code. Its objects define the control path used by `ib_srpt.c`: HCA add creates `srpt_device` and `srpt_port`; configfs creates `srpt_port_id` and `srpt_tpg`; login creates or finds a `srpt_nexus` and allocates `srpt_rdma_ch`; receives allocate `srpt_recv_ioctx`; accepted commands allocate `srpt_send_ioctx`; RDMA transfers allocate `srpt_rw_ctx`; target-core callbacks advance `srpt_command_state`; CM and drain paths advance `rdma_ch_state`.

## State and Persistence Behavior

`srpt_device` persists HCA-level PD, lkey, SRQ, event handler, receive buffers, and ports. `srpt_port` persists enablement, cached addressing, names, configfs IDs, attributes, nexus list, and live-channel refcount. `srpt_rdma_ch` persists QP/CQ, CM ID union, session, rings, credits, wait list, state, and release work. `srpt_send_ioctx` persists one target-core command and its RDMA context until `release_cmd`.

## Dependencies and Integration Points

It includes RDMA verbs, SA, IB CM, RDMA CM, RDMA read/write helper APIs, SCSI SRP wire definitions, and `ib_dm_mad.h`. Structures embed target-core `se_cmd`, `se_session`, `se_portal_group`, and `se_wwn` types through source includes, and are used as CM/QP/CQ contexts.

## Risks and Edge Cases

The channel state enum relies on increasing numerical order for monotonic transitions. Send and receive rings are sized from runtime limits and cache sizes; mismatches can corrupt DMA buffers. The CM ID union is selected by `using_rdma_cm`. `srpt_send_ioctx.recv_ioctx` transfers receive-buffer ownership for immediate data and must be cleared before repost. Per-port `use_srq` attributes drive per-device SRQ allocation, so multi-port expectations need care.

## Test Signals

Compile and runtime tests should cover all command and channel states, SRQ and non-SRQ modes, target-core session lifecycle, configfs port/TPG objects, direct/indirect/immediate descriptors, RDMA read/write contexts, and disconnect/free ordering.
