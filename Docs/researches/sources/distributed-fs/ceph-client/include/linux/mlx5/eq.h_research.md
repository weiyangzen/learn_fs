# `sources/distributed-fs/ceph-client/include/linux/mlx5/eq.h`

## Purpose

`eq.h` defines the compact public API for mlx5 event queues. Event queues carry firmware and completion events from the HCA to mlx5 core consumers. The header exposes sizing constants, generic EQ create/destroy and enable/disable functions, consumer-index maintenance helpers, and the `mlx5_nb` wrapper used to bind notifier callbacks to a specific firmware event type.

## Important APIs, Types, and Constants

- `MLX5_NUM_CMD_EQE`, `MLX5_NUM_ASYNC_EQE`, and `MLX5_NUM_SPARE_EQE` define command, async, and spare EQ entry sizing expectations.
- `struct mlx5_eq_param` passes the requested entry count, a 256-bit event mask (`mask[4]`), and an IRQ object into generic EQ creation.
- `mlx5_eq_create_generic()` allocates a generic EQ for a device using `mlx5_eq_param`; `mlx5_eq_destroy_generic()` tears it down.
- `mlx5_eq_enable()` registers a notifier and enables event delivery for an EQ; `mlx5_eq_disable()` removes it and disables delivery.
- `mlx5_eq_get_eqe()` returns an event queue entry for a consumer counter, and `mlx5_eq_update_ci()` writes the consumer index back to hardware, optionally arming the queue.
- `mlx5_eq_update_cc()` is an inline IRQ-handler helper that forces periodic CI updates when the local consumed count reaches `MLX5_NUM_SPARE_EQE`.
- `struct mlx5_nb`, `mlx5_nb_cof()`, and `MLX5_NB_INIT()` wrap a `notifier_block` with a concrete `MLX5_EVENT_TYPE_*` selector.

## Control Flow and Lifetimes

Typical flow is allocate an EQ with `mlx5_eq_create_generic()`, enable it with a notifier callback through `mlx5_eq_enable()`, process EQEs in an interrupt path by repeatedly reading entries and calling `mlx5_eq_update_cc()` on every event, and finally call `mlx5_eq_disable()` before destroying the EQ. The inline comment documents a key hardware flow-control rule: because EQs are created with spare entries, software must update hardware's consumer index at least once per spare-entry window or the HCA may treat the queue as overflowed.

## State and Persistence Behavior

The opaque `struct mlx5_eq` owns hardware queue state, DMA memory, producer/consumer indices, and IRQ binding in implementation files. `eq.h` exposes only the caller-owned `mlx5_eq_param` and notifier wrapper. The consumed counter passed through `mlx5_eq_update_cc()` is caller-maintained transient state and resets to zero after a forced CI update.

## Dependencies and Integration Points

The header forward-declares `mlx5_eq`, `mlx5_irq`, and `mlx5_core_dev`, and relies on `notifier_block` and mlx5 event type definitions visible through including context. `driver.h` includes this header and publishes `mlx5_eq_notifier_register()` for broader event dispatch. Usage in this tree includes core EQ implementation under `drivers/net/ethernet/mellanox/mlx5/core/eq.c` and RDMA ODP creating generic EQs for page-fault/event handling.

## Risks and Edge Cases

- Forgetting to call `mlx5_eq_update_cc()` for every EQE can lead to hardware-visible overflow even when software is processing events.
- Notifier callbacks must match the event type initialized by `MLX5_NB_INIT()` and must obey IRQ-context constraints.
- Disable/destroy ordering matters: destroying an enabled EQ risks callbacks racing with freed queue memory.
- The `mask[4]` contract is low-level; wrong bit placement can silently subscribe to the wrong firmware events.

## Test Signals

Validate with mlx5 core EQ creation/destruction paths, interrupt-driven event delivery, RDMA ODP generic EQ setup, command EQ behavior, synthetic event bursts above `MLX5_NUM_SPARE_EQE`, module unload while events are active, and lockdep/IRQ-context checks for notifier callbacks.
