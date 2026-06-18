# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.h

## Purpose
`efx.h` is the central internal header for the Falcon driver. It publishes constants, lifecycle functions, queue APIs, filter wrappers, reset APIs, interrupt moderation helpers, MTD hooks, scheduling helpers, and link/MAC helpers used across Falcon source files.

## Important APIs, Types, and Functions
The header declares netdev entry points (`ef4_net_open()`, `ef4_net_stop()`), TX/RX queue management, datapath transmit functions, RX refill and packet completion functions, channel reallocation, MAC/port reconfiguration, reset functions, IRQ moderation accessors, event queue start/stop, dummy PHY ops, software stat updates, MTD wrappers, link-state helpers, and `ef4_ethtool_ops`. Inline filter wrappers dispatch to `efx->type->filter_*` callbacks and document insertion/replacement semantics. Inline helpers include `ef4_rss_enabled()`, `ef4_schedule_channel()`, `ef4_schedule_channel_irq()`, `ef4_device_detach_sync()`, and a write-lock assertion helper.

## Control Flow
The header contributes inline control flow for filter operation dispatch, RFS expiration gating, NAPI scheduling, device detach synchronization, and optional MTD no-op behavior when `CONFIG_SFC_FALCON_MTD` is disabled. Most declared control flow is implemented in other C files.

## State and Persistence
No storage is allocated here, but the APIs operate on `struct ef4_nic`, `struct ef4_channel`, `struct ef4_tx_queue`, `struct ef4_rx_queue`, and `struct ef4_filter_spec`. Constants define queue/event queue sizing limits and minimums that shape persistent queue allocation decisions.

## Dependencies and Integration Points
The file includes `net_driver.h` and `filter.h`, so it sits above the core driver data structures and filter definitions. It ties together TX, RX, ethtool, MTD, RFS acceleration, reset, link, and NAPI code in the Falcon subtree.

## Risks
Because many helpers dispatch through `efx->type`, missing or incorrectly initialized NIC-type callbacks become runtime crashes. Queue-size constants must remain compatible with hardware ring limits and TSO descriptor requirements. Optional MTD and RFS branches must compile both enabled and disabled. The `ef4_rwsem_assert_write_locked()` helper temporarily attempts a read lock and should only be used in debug-style contexts where that behavior is acceptable.

## Test Signals
Full subtree build coverage with `CONFIG_SFC_FALCON_MTD` and `CONFIG_RFS_ACCEL` toggled is important. Runtime tests should exercise filter insertion/removal/get wrappers, NAPI scheduling, event queue start/stop, ring resize constraints, MTD probe/remove stubs, and reset/link helper callers.
