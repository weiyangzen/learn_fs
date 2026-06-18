# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mmio.c

Purpose: Provides PCI/platform MMIO registration glue, register base maps for MT7615E and MT7663E, interrupt dispatch, and mt76 bus operation wrappers that translate logical register addresses through `mt7615_reg_map()`.

Important APIs and functions: `mt7615e_reg_map[]` and `mt7663e_reg_map[]` map `enum mt7615_reg_base` indexes to chip-specific physical bases. `mt7615_irq_handler()` masks interrupts and schedules `irq_tasklet` after initialization. `mt7615_irq_tasklet()` reads `MT_INT_SOURCE_CSR`, acknowledges interrupts, schedules TX/RX NAPI, and queues SER reset work when MCU error bits appear. `mt7615_rr()`, `mt7615_wr()`, and `mt7615_rmw()` wrap original bus ops after applying register remapping. `mt7615_mmio_probe()` allocates the mt76 device, installs driver ops, requests IRQ, enables MT7663 PCI IRQ if needed, and calls `mt7615_register_device()`.

Control flow: PCI or platform probe passes a BAR/resource base and IRQ into `mt7615_mmio_probe()`. The function clones `mt7615_ops`, allocates `mt7615_dev`, initializes MMIO, records ASIC revision, replaces mt76 bus callbacks with remapping wrappers, disables interrupts, requests IRQ, then registers the device. Interrupt flow masks IRQs in hardirq context, drains sources in the tasklet, selectively disables sources while NAPI owns them, and re-enables RX through `mt7615_rx_poll_complete()`.

State and persistence: Runtime state includes `dev->reg_map`, `dev->bus_ops`, `dev->mt76.mmio.irqmask`, NAPI/tasklet scheduling state, and `dev->reset_state`. No persistent storage is written.

Dependencies and integration: Integrates Linux module init/exit, PCI driver registration, optional MT7622 platform driver registration, mt76 core allocation/MMIO/NAPI APIs, register macros from `regs.h`, MAC callbacks from `mac.h`, and tracepoint `trace_dev_irq()`.

Risks: Interrupt masking mistakes can lose RX/TX completions or spin tasklets. Register-map errors redirect MMIO operations to wrong hardware blocks. Reset work depends on accurate MCU error masks, which differ for MT7663. Error unwind must free IRQ/device without double-freeing devm resources.

Test signals: Probe success with correct ASIC revision log, IRQ/NAPI packet flow, firmware reset recovery after MCU error, suspend/resume coverage through PCI, and module load/unload without leaked IRQs.
