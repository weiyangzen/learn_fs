
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_common.h

## Purpose

This header defines the shared data model, constants, enums, and cross-file scheduling declarations for the HIBMCGE driver.

## Important APIs, Types, and Functions

- Constants define status values, RX skip/header layout, vector count, packet header size, TX timeout log size, and `HBG_NO_PHY`.
- `enum hbg_dir`, `enum hbg_tx_state`, `enum hbg_nic_state`, `enum hbg_reset_type`, and `enum hbg_hw_event_type` describe ring direction, TX descriptor state, driver state bits, reset source, and firmware/hardware event types.
- `struct hbg_buffer` holds SKB/page DMA state, TX completion state DMA address, direction, and back-pointers.
- `struct hbg_ring` represents TX or RX software rings, including coherent buffer array, head/tail aliases, NAPI object, page pool, and timeout log buffer.
- `struct hbg_dev_specs` caches device-provided capabilities such as MAC ID, PHY address, FIFO sizes, MTU range, VLAN layers, MAC table size, frame size, and RX buffer size.
- `struct hbg_irq_info` and `struct hbg_vector` describe IRQ metadata and per-IRQ counters.
- `struct hbg_mac`, `struct hbg_mac_filter`, `struct hbg_user_def`, `struct hbg_stats`, and `struct hbg_priv` are the core per-device state containers.
- `hbg_err_reset_task_schedule()` and `hbg_np_link_fail_task_schedule()` are declared for async service-task triggers.

## Control Flow

The header itself has no control flow. It enables all HIBMCGE modules to share one `struct hbg_priv` and common enums for lifecycle, reset, IRQ, ring, stats, and PHY operations.

## State and Persistence

All persistent runtime driver state is represented here: PCI/netdev pointers, BAR base, device specs, state bits, PHY/MDIO handles, vector stats, TX/RX rings, MAC filter table, saved user pause settings, accumulated stats, last stats-update time, and delayed service work.

## Dependencies and Integration Points

The header depends on ethtool, netdevice, PCI, page pool helpers, and `hbg_reg.h`. It is included by nearly every HIBMCGE source file and forms the integration contract among hardware helpers, TX/RX, ethtool, debugfs, MDIO, IRQ, diagnostics, and reset recovery.

## Risks and Edge Cases

Because this is a shared state header, layout changes can affect stats offset macros, DMA state handling, debugfs output, diagnostics, and reset restoration. `struct hbg_stats` is consumed via offset arithmetic in ethtool and diagnose paths, so field additions need synchronized table updates. The comment "rest" in the user settings comment is a typo only.

## Test Signals

Compile all HIBMCGE objects after any structure changes, verify ethtool stats offsets, debugfs state display, diagnostics pushes, reset restore behavior, and TX/RX ring initialization using the shared fields.
