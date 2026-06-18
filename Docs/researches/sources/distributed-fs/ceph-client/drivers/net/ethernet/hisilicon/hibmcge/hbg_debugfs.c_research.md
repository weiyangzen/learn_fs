
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.c

## Purpose

This file exposes debugfs diagnostics for HIBMCGE ring occupancy, IRQ metadata, MAC filter entries, and reset/link state.

## Important APIs, Types, and Functions

- `hbg_debugfs_register()` creates the global `hibmcge` debugfs root.
- `hbg_debugfs_init()` creates one per-PCI-device directory and devm seqfiles for `tx_ring`, `rx_ring`, `irq_info`, `mac_table`, and `nic_state`.
- `hbg_debugfs_unregister()` removes the global root at module exit.
- `hbg_dbg_ring()`, `hbg_dbg_irq_info()`, `hbg_dbg_mac_table()`, and `hbg_dbg_nic_state()` are the seqfile renderers.

## Control Flow

Module init creates the global root before PCI driver registration. Device init creates a child directory named by `pci_name()` and registers devm seqfiles. Each file reads live driver state and hardware registers when opened. Device cleanup removes the per-device subtree through a devm action; module exit removes the global root.

## State and Persistence

The only file-local state is `hbg_dbgfs_root`. Per-device debugfs files reflect live state from `struct hbg_priv`, including ring indices, FIFO occupancy, IRQ enabled bits/counters, MAC table contents, reset flags, and NP link status.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, PCI device names, string-choice helpers, hardware IRQ/FIFO helpers, and TX/RX queue helpers. It integrates with `hbg_main.c` module/device lifecycle and shared state from `hbg_common.h`.

## Risks and Edge Cases

Debugfs failures are intentionally ignored because debugfs is not a functional requirement. Renderers read live state without heavy locking, so values are snapshots and may race with TX/RX or reset. `reset_type_str[priv->reset_type]` assumes reset type stays within enum range.

## Test Signals

Signals include `/sys/kernel/debug/hibmcge/<pci>/` creation, readable `tx_ring`, `rx_ring`, `irq_info`, `mac_table`, and `nic_state` files, removal after device unbind/module unload, and no crashes while reading during traffic or reset.
