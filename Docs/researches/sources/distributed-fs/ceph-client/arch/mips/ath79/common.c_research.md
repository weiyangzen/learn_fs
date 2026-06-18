## sources/distributed-fs/ceph-client/arch/mips/ath79/common.c

Purpose: provides shared ATH79 global SoC state, DDR controller helpers, PCI window setup, DDR write-buffer flushing, and serialized reset-module bit control.

Important APIs and functions: exported globals include `ath79_cpu_freq`, `ath79_ahb_freq`, `ath79_ddr_freq`, `ath79_reset_base`, `ath79_soc`, and `ath79_soc_rev`. `ath79_ddr_ctrl_init()` maps the DDR controller and selects write-buffer flush and PCI window offsets by SoC family. `ath79_ddr_wb_flush()` performs the documented two-pass flush. `ath79_ddr_set_pci_windows()` writes PCI window offsets. `ath79_device_reset_set()` and `ath79_device_reset_clear()` choose the reset-module register for the current SoC and update bits under `ath79_device_reset_lock`.

Control flow: setup code calls DDR init after SoC detection. Drivers can call exported DDR/reset helpers later. Reset set/clear choose register offsets using `soc_is_*()` predicates and BUG on unknown SoC, then do read-modify-write under IRQ-safe spinlock.

State and persistence: static mapped bases track DDR subregisters. Reset register writes persist in hardware until changed/reset. Global SoC and frequency variables are runtime state exported to modules.

Dependencies and integration: depends on ATH79 SoC predicates, reset read/write helpers from public machine headers, Linux spinlocks, raw MMIO, and PCI constants. PCI and device drivers use these helpers.

Risks: `ath79_ddr_wb_flush()` assumes `ath79_ddr_ctrl_init()` has run. `ath79_ddr_set_pci_windows()` BUGs if no PCI window base is available. Unknown SoC families BUG in reset helpers, so all supported SoCs must be represented.

Test signals: DDR flush should complete without hanging; PCI devices should DMA correctly after window setup; device reset calls should toggle hardware and not race under concurrent drivers.
