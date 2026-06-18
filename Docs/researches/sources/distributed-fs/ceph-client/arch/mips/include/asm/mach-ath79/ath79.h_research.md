# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ath79.h

**Purpose:** Provides common ATH79 SoC identity, revision, and reset/PLL access helpers for board and platform code.

**Important APIs/types/functions:** Defines `enum ath79_soc_type`, extern globals `ath79_soc` and `ath79_soc_rev`, SoC predicate helpers such as `soc_is_ar71xx()`, `soc_is_ar724x()`, `soc_is_ar933x()`, `soc_is_ar934x()`, `soc_is_qca955x()`, and `soc_is_qca956x()`, declarations for `ath79_ddr_wb_flush()`, `ath79_ddr_set_pci_windows()`, `ath79_device_reset_set()`, and `ath79_device_reset_clear()`, and extern MMIO bases `ath79_pll_base`/`ath79_reset_base`. Inline helpers `ath79_pll_wr/rr()` and `ath79_reset_wr/rr()` perform raw MMIO access.

**Control flow:** Boot CPU detection initializes the global SoC type and revision; all later SoC-specific paths branch through the inline predicates. Reset and PLL helpers are used during device bring-up and clock programming. DDR flush helpers are called around DMA or device write-buffer synchronization.

**State and persistence behavior:** Holds global software identity state through `ath79_soc` and `ath79_soc_rev`, and uses global mapped MMIO base pointers. Inline writes mutate PLL and reset registers, which can change clocks or hold/release device blocks.

**Dependencies and integration points:** Depends on `<linux/types.h>`, `<linux/io.h>`, CPU detection code, MMIO mapping setup, `ar71xx_regs.h` register definitions, clock/reset users, PCI setup, and board files.

**Risks:** Incorrect SoC identity causes broad misconfiguration because many drivers branch through these predicates. The QCA9561/QCA9563 helpers currently both map to the single `ATH79_SOC_QCA956X` value, so code cannot distinguish those packages unless additional revision/strap logic is used. Raw writes have no locking in the inline layer.

**Test signals:** Validate CPU ID/revision logs across every SoC, unit-review predicate coverage for new enum entries, boot-test reset/PLL users, and run Ethernet/PCI/USB/SPI smoke tests that exercise DDR flush and reset helpers.
