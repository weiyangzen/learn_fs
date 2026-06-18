
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.c

## Purpose

This file implements HIBMCGE reset/rebuild logic and PCI error-recovery callbacks.

## Important APIs, Types, and Functions

- `hbg_rebuild()` reruns hardware initialization and restores user-visible settings.
- `hbg_reset()` performs a function reset when the netdev is down.
- `hbg_err_reset()` closes the netdev if running, resets/rebuilds under RTNL, and reopens it.
- `hbg_set_pci_err_handler()` installs the driver's `struct pci_error_handlers`.
- PCI callbacks handle `error_detected`, `slot_reset`, `reset_prepare`, and `reset_done`.

## Control Flow

Reset preparation serializes with `HBG_NIC_STATE_RESETTING`, rejects resets while the port is up for direct `hbg_reset()` calls, detaches the netdev, records reset type, clears failure state, and asks hardware/firmware for `HBG_HW_EVENT_RESET`. Reset completion checks the reset type, rebuilds hardware state, reattaches the netdev, and clears the resetting bit. Error-triggered reset closes the interface first, so reset preparation sees a down port.

PCI AER handling reports permanent failure as disconnect, otherwise requests reset. Slot reset reenables PCI, restores state, and invokes `hbg_err_reset()`. FLR prepare/done callbacks use the same reset-prepare/done helpers with `HBG_RESET_TYPE_FLR`.

## State and Persistence

Reset preserves and restores MAC table entries, MTU, pause settings, RX pause MAC address, filter enablement, and accumulated stats. It mutates `priv->state`, `priv->reset_type`, and `reset_fail_cnt`.

## Dependencies and Integration Points

The file depends on RTNL, PCI error recovery, PHY/netdev close/open behavior, hardware event notifications, hardware init, MAC filter state, and ethtool pause settings. It is called from IRQ error handling, service task, ethtool reset, and PCI AER.

## Risks and Edge Cases

Direct `hbg_reset()` refuses to run while the netdev is up, so callers must close first or use `hbg_err_reset()`. Failed hardware reset leaves reset-fail state and may keep the device detached. Restore assumes the saved MAC filter table and pause settings are valid. PCI slot reset calls `pci_disable_device()` before reenable; state restoration must match what pcim/device-managed setup expects.

## Test Signals

Signals include ethtool dedicated reset while down, IRQ-triggered reset while up, PCI AER reset callbacks, restoration of MAC address/filter/pause/MTU, reset failure counter increments on hardware timeout, and clean netdev detach/attach transitions.
