# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq_cmd.c

## Purpose
`srq_cmd.c` is the mlx5 firmware command backend for SRQ-like receive resources. It converts `mlx5_srq_attr` into legacy SRQ, XRC SRQ, RMP, or XRQ command formats, tracks SRQs in an xarray, and routes SRQ events from mlx5 notifier callbacks.

## Important APIs, types, and functions
- `mlx5_cmd_create_srq()`, `mlx5_cmd_destroy_srq()`, `mlx5_cmd_query_srq()`, and `mlx5_cmd_arm_srq()` are the public command operations used by `srq.c`.
- `get_pas_size()`, `set_wq()`, `set_srqc()`, `get_wq()`, and `get_srqc()` compute PAS sizes and map common attributes into or out of mlx5 WQ/SRQC command structures.
- `create_srq_cmd()`, `destroy_srq_cmd()`, `arm_srq_cmd()`, and `query_srq_cmd()` implement pre-ISSI legacy SRQ commands.
- `create_xrc_srq_cmd()`, `destroy_xrc_srq_cmd()`, `arm_xrc_srq_cmd()`, and `query_xrc_srq_cmd()` implement XRC SRQ commands.
- `create_rmp_cmd()`, `destroy_rmp_cmd()`, `arm_rmp_cmd()`, and `query_rmp_cmd()` implement RMP-backed SRQs.
- `create_xrq_cmd()`, `destroy_xrq_cmd()`, `arm_xrq_cmd()`, and `query_xrq_cmd()` implement XRQ and tag-matching SRQs.
- `create_srq_split()`, `destroy_srq_split()`, and query/arm switch logic select command families based on ISSI and resource type.
- `mlx5_cmd_get_srq()` holds an SRQ by SRQN from the xarray for event users.
- `srq_event_notifier()` receives mlx5 SRQ events, holds the SRQ, calls its event callback, and releases it.

## Control flow
Creation first maps RDMA SRQ type to resource kind: XRC uses `MLX5_RES_XSRQ`, tag matching uses `MLX5_RES_XRQ`, and basic uses `MLX5_RES_SRQ`. The selected create function computes or validates page size for user memory, allocates a command buffer sized for PAS entries, fills SRQ/WQ context fields, populates PAS from `ib_umem` or kernel PAS arrays, executes the firmware command, and stores SRQN/UID. The created resource is refcount-initialized and inserted into `dev->srq_table.array`.

Destroy uses `xa_cmpxchg_irq()` to replace the SRQ entry with `XA_ZERO_ENTRY`, destroys the hardware object, restores the entry if firmware destroy fails, then removes the placeholder only if it still belongs to this destroy sequence. It drops the initial resource reference and waits for event references to complete.

Query and arm operations choose legacy or ISSI-specific command families. Query returns common WQ fields and marks `MLX5_SRQ_FLAG_ERR` when hardware state is not good/ready. XRQ query additionally extracts tag-matching append index and hardware/software phase counters.

Event table initialization clears and initializes the xarray with IRQ locking, registers the notifier, and cleanup unregisters it.

## State and persistence
Persistent hardware state includes SRQ/XRC SRQ/RMP/XRQ contexts and their PAS-backed WQs. In-memory state includes the SRQ xarray, notifier block, resource refcount/completion, resource kind, SRQN, UID, and event callback. `XA_ZERO_ENTRY` is used as temporary destroy state to handle hardware-number reuse races.

## Dependencies and integration points
This file depends on mlx5 firmware command layouts, mlx5 command execution helpers, `mlx5_umem_find_best_quantized_pgoff()`, `mlx5_ib_populate_pas()`, `ib_umem_num_dma_blocks()`, xarray IRQ locking, mlx5 notifier registration, and common resource refcounting from the QP resource code.

## Risks
- PAS sizing must match the selected page size and hardware context layout; mismatches trigger warnings or invalid command buffers.
- Legacy non-ISSI and ISSI command families have different context fields; changes must preserve both paths.
- Destroy races with SRQN reuse are subtle and rely on `XA_ZERO_ENTRY` compare/exchange sequencing.
- `get_wq()` and `get_srqc()` use flag assignment for signature state; changes should avoid accidentally clearing unrelated flags.
- Event callbacks run outside the xarray lock but rely on refcounts being held.
- Tag-matching XRQ fields are only valid for XRQ contexts and must not be assumed for basic SRQs.

## Test signals
- Creation tests should cover legacy SRQ, ISSI basic/RMP, XRC SRQ, and tag-matching XRQ with user and kernel memory.
- Page-size tests should validate quantized offsets, PAS counts, and failure on invalid page sizing.
- Query tests should cover good and error hardware states plus XRQ tag-matching counters.
- Destroy race tests should exercise SRQN reuse and firmware destroy failure retry behavior.
- Event tests should inject SRQ limit and catastrophic events, including events during destroy.
