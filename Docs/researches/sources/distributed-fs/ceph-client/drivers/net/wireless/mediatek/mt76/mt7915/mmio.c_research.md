# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mmio.c

## Purpose

`mmio.c` provides the MT7915-family MMIO backend, register translation, WED attachment, interrupt handling, mt76 device allocation, and module registration. It selects chip-specific register tables for MT7915, MT7916, MT7981, and MT7986, wraps mt76 bus operations to remap large physical register addresses into accessible PCI/AXI windows, and connects the device to mt76 DMA/NAPI callbacks and mac80211 operations.

## Important APIs, Types, and Functions

- Chip tables `mt7915_reg`, `mt7916_reg`, and `mt7986_reg` provide revision-specific base addresses for interrupts, WFDMA, firmware crash/debug addresses, SWDEF, and WED rings.
- Offset tables `mt7915_offs` and `mt7916_offs` provide revision-specific register offsets for TMAC, MDP, ARB, RMAC/MIB, AGG, LPON, WTBL, PLE, and ETBF areas.
- Register maps `mt7915_reg_map`, `mt7916_reg_map`, and `mt7986_reg_map` translate high physical register ranges into mapped MMIO windows.
- `mt7915_mmio_init()` initializes mt76 MMIO, selects register descriptors by device ID, clones and overrides bus ops, records ASIC revision, and initializes the remap spinlock.
- `mt7915_rr()`, `mt7915_wr()`, `mt7915_rmw()`, and `mt7915_memcpy_fromio()` are the register access wrappers used through mt76.
- `mt7915_mmio_wed_init()` optionally attaches MediaTek WED and fills bus-specific WED register addresses, token sizes, RX buffer sizes, callbacks, IRQ, and DMA device.
- `mt7915_dual_hif_set_irq_mask()` manages shared IRQ masks across primary and secondary HIF.
- `mt7915_irq_handler()` is the top-half IRQ entry. `mt7915_irq_tasklet()` processes interrupt status, schedules NAPI, handles MCU command errors, and re-masks interrupts.
- `mt7915_mmio_probe()` allocates the mt76/mt7915 device and installs `struct mt76_driver_ops`.
- `mt7915_init()` and `mt7915_exit()` register and unregister PCI primary, PCI HIF, and optional platform WMAC drivers.

## Control Flow

Probe code from PCI or platform calls `mt7915_mmio_probe()` with a mapped base and device ID. That allocates an mt76 device with `mt7915_ops` and MT7915-specific `mt76_driver_ops`, initializes MMIO/register mapping through `mt7915_mmio_init()`, and sets up the IRQ tasklet.

`mt7915_mmio_init()` calls `mt76_mmio_init()` first, then chooses register and offset maps by device ID. It saves the original bus ops in `dev->bus_ops`, duplicates the bus ops, replaces `rr`, `wr`, and `rmw` with MT7915 remapping wrappers, and installs the clone back into `dev->mt76.bus`. Direct register offsets below `0x100000` pass through. High addresses are searched in `dev->reg.map`; if absent, the code programs layer-1 or layer-2 HIF remap registers under `dev->reg_lock` and accesses the remapped aperture.

Interrupt flow starts in `mt7915_irq_handler()`, which masks primary and optional secondary interrupt sources, rejects interrupts before initialization, and schedules `mt76.irq_tasklet`. The tasklet reads WED or raw interrupt status, combines secondary HIF status, traces it, disables RX done and MCU TX done bits, schedules TX NAPI and RX NAPI queues for main, band1, MCU, WA, and variant-specific WA queues, then checks MCU command status. Firmware error or watchdog bits set `dev->recovery.state` and call `mt7915_reset()`.

WED initialization is optional and gated by the `wed_enable` module parameter and build support. When active, it maps PCI BAR or platform resources, fills WPDMA/WED addresses from the selected register table, sets token and RX buffer parameters, registers offload and reset callbacks, attaches WED, replaces the IRQ with WED's IRQ, and switches DMA ownership to the WED device.

Module init registers the auxiliary HIF PCI driver before the primary PCI driver, then optional MT798x WMAC platform driver. Exit unregisters in reverse order.

## State and Persistence Behavior

`mmio.c` sets persistent runtime state inside `struct mt7915_dev` and `struct mt76_dev`:

- `dev->reg` stores selected register bases, offsets, map pointer, and map size.
- `dev->bus_ops` preserves original low-level MMIO operations while `dev->mt76.bus` points to remapping wrappers.
- `dev->reg_lock` serializes remap window programming and access.
- `mdev->rev` records device ID and hardware revision.
- `mdev->mmio.irqmask` is updated under `mmio.irq_lock`, and dual-HIF writes mirror masks into both interrupt controllers.
- `dev->mt76.mmio.wed` stores WED attachment state, register addresses, callbacks, token sizes, IRQ, and DMA device.
- IRQ/NAPI scheduling state lives in mt76 NAPI objects.

No file-backed persistence is performed. State is re-established on driver load/probe and torn down on remove/module exit.

## Dependencies and Integration Points

This file integrates with the Linux PCI, platform, module, DMA, IRQ, NAPI, RTNL, and optional WED subsystems. It depends on mt76 MMIO, DMA, bus, tracing, and allocation helpers. It exports functions declared in `mt7915.h` and consumes functions from `main.c`, `mac.c`, `mcu.c`, DMA code, and reset logic through the `mt76_driver_ops` table and interrupt recovery callouts.

WED reset integration calls `mt7915_mcu_set_ser()` and waits for `mdev->mmio.wed_reset`, temporarily dropping RTNL. Register remapping relies on definitions in `regs.h` and chip predicates from mt76.

## Risks and Edge Cases

- Register remap access is global-window based. Missing `dev->reg_lock` coverage or nested remap use can read/write the wrong physical register.
- `__mt7915_reg_addr()` returns `0` when a high address is not in the static map, causing dynamic remap. A legitimate mapped offset of zero is indistinguishable from "needs remap" by design and must remain compatible with the tables.
- WED attach changes IRQ and DMA device ownership; cleanup paths must detach WED instead of freeing PCI vectors when active.
- Interrupt masking must be balanced with NAPI poll completion. Missing re-enable causes stalls; premature re-enable can cause interrupt storms.
- Dual-HIF interrupt masks must update both primary and secondary controllers. Primary-only changes can leave band1 queues dead or noisy.
- `mt7915_irq_handler()` returns `IRQ_NONE` before initialization after masking interrupts; probe ordering must ensure interrupts are not lost permanently.
- Chip-specific register maps are large and manually maintained; wrong entries can cause silent hardware misconfiguration or firmware crash dump failures.

## Test Signals

Validation should cover probe for each supported device ID, direct and remapped register reads, firmware download through remapped MCU registers, interrupt delivery for TX done and every RX queue, NAPI poll completion re-enabling interrupts, dual-HIF operation, WED attach/detach and reset, crash/status register reads, module unload/reload, and negative tests for invalid device IDs. Useful runtime signals include ASIC revision logs, no IRQ storms, stable traffic under both bands, working MCU command error recovery, and WED counters advancing when offload is enabled.
