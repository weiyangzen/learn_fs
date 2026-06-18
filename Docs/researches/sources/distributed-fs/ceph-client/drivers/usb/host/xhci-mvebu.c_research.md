# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.c

## Purpose
Provides the Marvell MVEBU xHCI MBus initialization quirk used by the platform xHCI glue. It programs USB3 address-decode windows so the host controller can access DRAM chip-select regions.

## Important APIs, Types, And Functions
The exported function is `xhci_mvebu_mbus_init_quirk(struct usb_hcd *hcd)`. The internal `xhci_mvebu_mbus_config()` clears and programs up to `USB3_MAX_WINDOWS` windows using `struct mbus_dram_target_info` and `struct mbus_dram_window`. Register helpers are `USB3_WIN_CTRL(w)` and `USB3_WIN_BASE(w)`.

## Control Flow
The platform wrapper invokes the quirk during xHCI setup for Armada compatibles. The quirk obtains IORESOURCE_MEM index 1 from the platform device, temporarily maps it with `ioremap()`, fetches DRAM target metadata from `mv_mbus_dram_info()`, clears all USB3 decode windows, writes one enabled window for each DRAM CS, then unmaps the temporary region.

## State And Persistence
No Linux object state is retained. The only lasting effect is hardware register programming in the USB3 MBus window block until reset or later reprogramming. The temporary mapping exists only during the quirk call.

## Dependencies And Integration Points
Depends on platform resources, MMIO accessors, and the MVEBU MBus library. It is connected through `xhci-plat.c` via `struct xhci_plat_priv.init_quirk` for Armada 375/380-style xHCI instances.

## Risks And Test Signals
Risks include missing resource index 1, stale or incorrect DRAM CS metadata, programming more chip selects than the hardware window count, and failures on systems with unusual memory maps. Test signals include successful Armada xHCI probe, DMA transfers to memory in each DRAM chip select, no decode errors under high I/O load, and suspend/resume behavior if the MBus registers are reset by firmware.
