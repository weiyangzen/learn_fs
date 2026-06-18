
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.c

## Purpose

This file contains low-level HIBMCGE hardware programming helpers for firmware event handshakes, device spec discovery, IRQ masking/clearing, MAC address/filter programming, MTU/frame sizing, MAC enable, FIFO state, TX/RX descriptor doorbells, link mode changes, pause control, FIFO thresholds, and initial hardware setup.

## Important APIs, Types, and Functions

- `hbg_hw_event_notify()` sends `HBG_HW_EVENT_INIT`, `RESET`, or `CORE_RESET` requests and polls until specs become valid and the request clears.
- `hbg_hw_init()` reads device specs and initializes endian mode, mode-change, RX control, transmit control, and FIFO thresholds.
- `hbg_hw_get_irq_status()`, `hbg_hw_irq_clear()`, `hbg_hw_irq_is_enabled()`, and `hbg_hw_irq_enable()` abstract normal, TX-indirect, and RX-indirect interrupt registers.
- `hbg_hw_set_mtu()`, `hbg_hw_mac_enable()`, `hbg_hw_set_uc_addr()`, `hbg_hw_set_mac_filter_enable()`, `hbg_hw_set_pause_enable()`, `hbg_hw_get_pause_enable()`, and `hbg_hw_set_rx_pause_mac_addr()` implement netdev-facing configuration.
- `hbg_hw_set_tx_desc()` and `hbg_hw_fill_buffer()` write TX descriptors and RX buffer addresses into hardware CFF registers.
- `hbg_hw_adjust_link()` reprograms speed/duplex and waits for MAC-to-PHY link when an external PHY exists.

## Control Flow

Initialization starts with a hardware/firmware event handshake, then reads specification registers into `priv->dev_specs`, derives max frame and RX buffer sizes, and programs PCU/GMAC control registers. Link adjustment disables the MAC, writes port mode and duplex, sends a core-reset event, reenables the MAC, and polls NP link status; repeated NP link failures are scheduled for service-task recovery.

## State and Persistence

The file populates persistent `priv->dev_specs` and writes persistent device registers for IRQ masks, MAC tables, MTU, filters, pause state, RX buffer size, FIFO thresholds, and link mode. `HBG_NIC_STATE_EVENT_HANDLING` serializes firmware event requests.

## Dependencies and Integration Points

It depends on register definitions in `hbg_reg.h`, inline accessors from `hbg_hw.h`, Linux polling helpers, ethtool/if_vlan constants, and service-task scheduling declarations from `hbg_common.h`. It is used by main lifecycle, TX/RX, IRQ, MDIO, ethtool, debugfs, and reset recovery.

## Risks and Edge Cases

Event notification can return `-EBUSY` if another event is in progress and times out after two seconds. Link adjustment ignores the return value from the core-reset event and may reenable the MAC after a failed event. MTU programming toggles a burst-length bit based on `mtu > 2000`, a hardware-specific performance/drop tradeoff. IRQ helpers treat the driver-only TX/RX pseudo-mask bits specially; passing combined masks with those bits and normal bits would only service the first special path.

## Test Signals

Signals include successful device-spec discovery, valid MAC address and MTU range, IRQ enable/disable and clear behavior for normal/TX/RX interrupts, link mode changes for 10/100/1000 SGMII, pause enable get/set, FIFO threshold programming, reset/rebuild register restoration, and NP link-failure scheduling on poll timeout.
