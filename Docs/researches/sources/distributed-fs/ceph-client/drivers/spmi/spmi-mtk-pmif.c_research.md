# sources/distributed-fs/ceph-client/drivers/spmi/spmi-mtk-pmif.c

## Purpose

`spmi-mtk-pmif.c` implements MediaTek's PMIF-backed SPMI controller driver for MT6873, MT8195, and MT8196-style SoCs. It maps SoC-specific PMIF and SPMI master register layouts, issues SPMI read/write/reset/sleep/shutdown/wakeup commands through a software-interface channel, manages clocks, and for SPMI v2 hardware exposes an IRQ domain for remote-control/status interrupts by slave ID.

## Important APIs, Types, And Functions

Important types are `struct ch_reg` for selected software-interface channel register indexes, `struct pmif_data` for SoC register tables and capabilities, `struct pmif_bus` for each SPMI bus instance, and `struct pmif` for the parent device's shared state. SoC data tables include `mt6873_regs`, `mt8195_regs`, `mt6873_spmi_regs`, `mt8195_spmi_regs`, `mt6873_pmif_arb`, `mt8195_pmif_arb`, and `mt8196_pmif_arb`.

Register helpers are `pmif_readl()`, `pmif_writel()`, `mtk_spmi_readl()`, `mtk_spmi_writel()`, and `pmif_is_fsm_vldclr()`. SPMI callbacks are `pmif_arb_cmd()`, `pmif_spmi_read_cmd()`, and `pmif_spmi_write_cmd()`. IRQ support is implemented by `mtk_spmi_handle_chained_irq()`, `mtk_spmi_rcs_irq_eoi()`, `mtk_spmi_rcs_irq_enable()`, `mtk_spmi_rcs_irq_disable()`, `mtk_spmi_rcs_irq_set_wake()`, `mtk_spmi_rcs_irq_translate()`, `mtk_spmi_rcs_irq_alloc()`, `mtk_spmi_irq_init()`, and `mtk_spmi_irq_remove()`. Probe/remove paths are `mtk_spmi_bus_probe()`, `mtk_spmi_probe()`, and `mtk_spmi_remove()`.

## Control Flow And State

Parent probe allocates `struct pmif`, selects SoC match data, stores it as platform driver data, then either probes one bus from the parent node or iterates child nodes named `spmi` when the SoC supports multiple SPMI buses. After bus probing, it computes the selected software-interface channel from `soc_chan` and stores register indexes for status, write data, read data, command send, and valid-clear.

Each bus probe determines a bus ID from OF aliases for multi-bus SoCs, allocates an SPMI controller, maps `pmif` and `spmimst` register resources by name, obtains and enables the three clocks, initializes SPMI v2 IRQ support when applicable, installs SPMI command/read/write callbacks, assigns the controller OF node and name, initializes the raw spinlock, adds the controller, and finally attaches a chained IRQ handler if an IRQ domain exists. Remove walks all bus slots, removes IRQ domains and chained handlers, removes SPMI controllers, disables clocks, and releases clock references.

Reads validate SID and length, map framework opcodes into PMIF command classes, wait for the software-interface FSM to become idle, issue a packed command, wait for `SWINF_WFVLDCLR`, read a 32-bit data register, clear the valid flag, unlock, and copy the requested bytes to the caller. Writes validate SID/length/opcode class, copy bytes into a 32-bit word, wait for idle, write the data register, issue a packed write command, and return after command submission. Both paths serialize the shared software interface with `raw_spin_lock_irqsave()`.

SPMI command opcodes for reset/sleep/shutdown/wakeup use the SPMI master operation-state registers and poll `SPMI_OP_ST_STA`. SPMI v2 IRQ handling creates an IRQ domain, clears stale bootloader interrupts, translates firmware interrupt specs by SID, tracks min/max SIDs seen, handles the parent chained IRQ by scanning only relevant SPMI interrupt banks, dispatches one domain IRQ per enabled SID, and acknowledges by writing the eight-bit bank mask back to the hardware register.

## State And Persistence Behavior

Persistent runtime state includes SoC register mapping tables, MMIO bases, enabled clocks, per-bus IRQ domain, enabled-SID bitmap, min/max SIDs discovered by IRQ translation, and the selected software-interface channel register indexes. No disk state is involved. Hardware interrupt flags are cleared during IRQ init and on child IRQ EOI; clock state persists while the platform device is bound.

## Dependencies And Integration Points

The driver depends on OF match data and aliases, named MMIO resources, named clocks (`pmif_sys_ck`, `pmif_tmr_ck`, `spmimst_clk_mux`), the SPMI framework, IRQ domains, chained IRQ handling, raw spinlocks, and atomic MMIO polling. It integrates with PMIC child devices through the SPMI bus and, for v2, with device-tree interrupt consumers through the controller's IRQ domain.

## Risks And Test Signals

Risks include mismatched register tables for SoC variants, incorrect software-interface channel selection, raw-spinlocked polling under long hardware stalls, no explicit zero-length rejection before `(len - 1)` encoding, write command completion not being polled after submission, IRQ-bank decoding that depends on SID-to-bank math, and multi-bus overflow if firmware exposes more child buses than `PMIF_MAX_BUSES`. The `pmif_arb_cmd()` poll condition appears to wait for the busy bit to become set rather than clear, which deserves hardware confirmation.

Useful tests include probe/remove for each compatible, missing clock/resource/alias failures, 1-4 byte read/write transfers, invalid SID/opcode/length handling, PMIF FSM timeout with valid-clear recovery, reset/sleep/shutdown/wakeup commands, multi-bus MT8196 enumeration, SPMI v2 IRQ domain allocation from firmware specs, wake enable propagation, stale interrupt clearing, chained IRQ dispatch only for enabled SIDs, and repeated bind/unbind checking clocks and controller removal.
