# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mmio.c

## Purpose
`mmio.c` provides the memory-mapped bus layer for MT7996-family PCIe devices. It selects chip-specific register bases, offset tables, and physical-to-MMIO maps; wraps mt76 bus read/write/rmw callbacks with dynamic remap handling; initializes optional MediaTek WED hardware offload integration; drives interrupt masking and the irq tasklet; allocates the mt76 device; and registers/unregisters the PCI drivers at module load/unload.

## Important APIs, Types, And Functions
The register data tables are `mt7996_reg_base`, chip-specific offset arrays (`mt7996_offs`, `mt7992_offs`, `mt7990_offs`), and address maps (`mt7996_reg_map`, `mt7990_reg_map`). `mt7996_reg_map_l1()`, `mt7996_reg_map_l2()`, and `mt7996_reg_map_cbtop()` program HIF remap registers for addresses outside the directly mapped window. `__mt7996_reg_addr()` searches static maps, while `__mt7996_reg_remap_addr()` chooses L1/L2/CBTOP remapping for infra, WFSYS, CBTOP, and fallback ranges.

The exported `mt7996_memcpy_fromio()` supports bulk MMIO reads with the same remap lock discipline. `mt7996_rr()`, `mt7996_wr()`, and `mt7996_rmw()` replace the mt76 bus ops after `mt7996_mmio_init()`. `mt7996_mmio_wed_init()` configures `struct mtk_wed_device` fields for primary and secondary HIF, including WPDMA interrupt/mask/ring addresses, RRO rings, token sizing, TXFREE routing, RX buffer sizing, and callbacks. `mt7996_dual_hif_set_irq_mask()`, `mt7996_irq_handler()`, and `mt7996_irq_tasklet()` manage interrupt masking and NAPI scheduling.

`mt7996_mmio_probe()` allocates the device with mt76 driver ops and initializes bus mapping, tasklet, and initial IRQ state. Module init registers `mt7996_hif_driver` first and `mt7996_pci_driver` second; module exit unregisters them in reverse.

## Control Flow
During PCI probe, `pci.c` calls `mt7996_mmio_probe()` with BAR0. The function calls `mt76_alloc_device()`, then `mt7996_mmio_init()`, which initializes the base MMIO bus, sets the chip-specific register descriptor, clones the original bus ops, overrides rr/wr/rmw, and records the ASIC revision. Runtime register access first attempts direct static mapping; if no mapping is found it acquires `dev->reg_lock`, programs the appropriate remap window, performs the access, and releases the lock.

Interrupt flow starts in `mt7996_irq_handler()`, which masks primary and optional secondary HIF interrupts and schedules the mt76 irq tasklet after initialization. The tasklet reads interrupts either through active WED devices or raw interrupt source CSRs, merges HIF2 status when present, traces the interrupt, disables active RX/MCU TX bits, schedules TX NAPI or RX NAPI per queue, and handles MCU error/watchdog command bits by recording recovery state and invoking `mt7996_reset()`. RX poll completion re-enables either NPU WLAN IRQs or normal MT_INT_RX bits.

## State And Persistence
This file initializes and mutates `dev->reg`, `dev->bus_ops`, `dev->mt76.bus`, `dev->mt76.mmio.irqmask`, `dev->mt76.hwrro_mode`, WED device structs, DMA device selection, token sizes, irq tasklet state, and hardware interrupt mask/source registers. All state is runtime-only hardware/driver state; module parameters `wed_enable` and WED attach success decide whether WED state is active.

## Dependencies And Integration Points
`mmio.c` integrates mt76 MMIO, Linux PCI/module APIs, MediaTek WED (`CONFIG_NET_MEDIATEK_SOC_WED`), optional NPU queues, `trace_dev_irq`, DMA/RRO callbacks, and reset/SER routines in `mcu.c` and `mac.c`. Its driver ops connect mac80211-facing operations (`mt7996_ops`) to DMA/TX/RX/channel callbacks implemented in other files. The PCI drivers it registers are defined in `pci.c`.

## Risks
Register remap programming is serialized only for unmapped accesses; any caller bypassing bus ops could race remap windows. Chip-specific map/offset errors can send reads/writes to wrong hardware blocks. WED setup has many variant-dependent ring offsets and interrupt bits, especially with dual HIF and MT7992/MT7990 differences. Interrupt masking must stay balanced with NAPI completion; missed re-enable paths can stall RX, while premature unmasking can storm interrupts. WED reset temporarily drops RTNL, so reset completion and state bits must be robust.

## Test Signals
Probe should log the expected ASIC revision and succeed on MT7996, MT7992, and MT7990. Register reads through mapped and remapped ranges should return sane values. Traffic should schedule the expected RX/TX NAPI queues on single-HIF, dual-HIF, WED, and non-WED configurations. MCU watchdog/error interrupts should trigger recovery. WED attach/detach, RRO traffic, and NPU RX queue interrupt re-enable are key integration tests.
