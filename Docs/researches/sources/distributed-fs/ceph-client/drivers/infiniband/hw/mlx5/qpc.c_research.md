# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qpc.c

## Purpose
`qpc.c` is the mlx5 IB command and resource-tracking backend for QPs, DCTs, tracked raw SQ/RQ objects, XRCD allocation, delay-drop configuration, and QP-related asynchronous events. It provides the lower-level hardware command operations used by `qp.c`.

## Important APIs, types, and functions
- `mlx5_qpc_create_qp()`, `mlx5_core_qp_modify()`, `mlx5_core_destroy_qp()`, and `mlx5_core_qp_query()` wrap CREATE/MODIFY/DESTROY/QUERY QP firmware commands and resource registration.
- `mlx5_core_create_dct()`, `mlx5_core_destroy_dct()`, and `mlx5_core_dct_query()` manage DCT hardware objects, including drain-before-destroy.
- `mlx5_core_create_rq_tracked()`, `mlx5_core_destroy_rq_tracked()`, `mlx5_core_create_sq_tracked()`, and `mlx5_core_destroy_sq_tracked()` publish raw RQ/SQ resources into the QP table so mlx5 events can be delivered to their owners.
- `create_resource_common()`, `destroy_resource_common()`, `modify_resource_common_state()`, `mlx5_get_rsc()`, and `mlx5_core_put_rsc()` implement radix-tree resource lifetime, invalidation, refcounting, and completion-based teardown.
- `rsc_event_notifier()`, `dct_event_notifier()`, and `is_event_type_allowed()` translate mlx5 notifier events into resource callbacks while filtering unsupported event/resource-type combinations.
- `modify_qp_mbox_alloc()` and `get_ece_from_mbox()` allocate opcode-specific modify mailboxes, copy QPC data, set ECE inputs, and extract ECE outputs.
- `mlx5_core_xrcd_alloc()` and `mlx5_core_xrcd_dealloc()` wrap XRCD firmware commands.
- `mlx5_core_set_delay_drop()` programs the delay-drop timeout.

## Control flow
Device setup calls `mlx5_init_qp_table()`, which initializes the radix tree, DCT xarray, debugfs, and mlx5 notifier. QP/SQ/RQ creation executes the firmware command first, then inserts the resulting number into the resource table with a resource type encoded above `MLX5_USER_INDEX_LEN`. If resource insertion fails, the hardware object is destroyed.

Asynchronous events arrive through `rsc_event_notifier()`. DCT drained events are handled through the DCT xarray and complete the DCT's `drained` completion. QP/SQ/RQ events compute a resource number from event data plus queue type, hold the resource, validate the event type, and call the object's event handler. For QP/SQ/RQ events the handler is responsible for putting the resource.

Destroy removes or invalidates the resource from lookup before destroying hardware. RQ destroy marks the common resource invalid first because failed firmware destroy can be retried; successful destroy then removes and waits for the last event reference. DCT destroy drains the object, waits for drained completion, uses an `XA_ZERO_ENTRY` placeholder to avoid erasing a newly-created DCT that reuses the same number, and then destroys the hardware DCT.

## State and persistence
The QP table persists a radix-tree mapping from encoded QP/SQ/RQ numbers to `struct mlx5_core_rsc_common`, plus a DCT xarray. Each tracked resource owns a refcount, completion, resource type, invalid flag, UID, QPN, event callback, and creation PID. Hardware state persists in the device until destroy commands complete.

## Dependencies and integration points
This file integrates with the mlx5 command executor, mlx5 notifier events, debugfs QP tracking, xarray/radix-tree kernel containers, resource refcount completions, and RDMA device type checks. It is the implementation behind declarations in `qp.h` and is used by `qp.c` for all command-level QP operations.

## Risks
- Event delivery races with destroy; incorrect invalidation or refcount handling can cause use-after-free or lost completion.
- DCT/SRQ-number reuse is explicitly handled with `XA_ZERO_ENTRY`; changing the destroy sequence can erase a newly created object.
- `modify_qp_mbox_alloc()` has opcode-specific mailbox layouts. Missing ECE or QPC handling for a new opcode can break modify responses.
- Tracked RQ destroy can fail and be retried. Code must restore resource validity on firmware failure.
- Event type filtering depends on the encoded event queue type and resource type matching the radix-tree key.

## Test signals
- Fault-injection tests should force firmware create/destroy/modify failures and verify command unwind paths and resource-table cleanup.
- Event tests should inject or emulate path migration, communication established, SQ drained, SRQ last WQE, WQ fatal/access/request errors, and DCT drained events.
- Destroy-race tests should create/destroy QPs, RQs, SQs, and DCTs while events arrive, checking refcount completion and reuse behavior.
- ECE tests should exercise modify opcodes that return ECE values and confirm userspace sees updated options.
- Build tests should cover SMI and non-SMI RDMA device types to exercise debugfs gating.
