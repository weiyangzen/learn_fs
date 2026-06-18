# sources/distributed-fs/ceph-client/drivers/edac/dmc520_edac.c

## Purpose
This file implements an interrupt-driven EDAC driver for the Arm DMC-520 memory controller. It currently handles DRAM ECC correctable and uncorrectable interrupts, initializes rank geometry from DMC registers, and reports errors through the EDAC MC core.

## Important APIs, Types, And Functions
`struct dmc520_edac` stores MMIO base, a spinlock protecting `mci->error_desc`, memory width, and arrays mapping discovered IRQs to interrupt masks. `struct ecc_error_info` carries decoded rank/bank/row/column details. `dmc520_irq_configs[]` maps ten named interrupt lines to status/control bits, although only DRAM ECC CE/UE paths produce EDAC reports.

Key functions are `dmc520_edac_probe()`, `dmc520_edac_remove()`, `dmc520_isr()`, `dmc520_edac_dram_all_isr()`, `dmc520_edac_dram_ecc_isr()`, `dmc520_handle_dram_ecc_errors()`, `dmc520_get_dram_ecc_error_count()`, `dmc520_get_dram_ecc_error_info()`, and `dmc520_init_csrow()`.

## Control Flow
Probe enumerates optional named IRQs, requires at least one valid line, maps registers, exits if DRAM ECC is disabled, allocates a chip-select EDAC topology sized by register-derived rank count, initializes private state and controller metadata, switches to interrupt mode, derives memory width/type/device width/rank size, initializes DIMM entries, masks and clears discovered interrupts, requests each IRQ, resets DRAM CE/UE counters, registers with EDAC, and enables the selected interrupt mask.

On interrupt, `dmc520_isr()` finds the matching mask for the Linux IRQ and calls `dmc520_edac_dram_all_isr()`. That function reads interrupt status and dispatches CE and/or UE handling only if both the IRQ's mask and hardware status bit are set. `dmc520_handle_dram_ecc_errors()` reads latched address info, reads and clears per-rank counters, formats rank/bank/row/column detail, takes `error_lock`, and calls `edac_mc_handle_error()`.

## State And Persistence
Hardware error counters are reset after reads. Interrupt enables live in DMC control registers and are modified to preserve unrelated bits. EDAC state persists in `mci` and per-DIMM counters. The global `dmc520_mc_idx` increments for each controller instance. The spinlock prevents concurrent ISR paths from corrupting the shared `mci->error_desc` buffer.

## Dependencies And Integration Points
The driver depends on OF matching (`arm,dmc-520`), platform named IRQs, MMIO, bitfield helpers, spinlocks, EDAC MC APIs, and module platform-driver registration. It exposes standard EDAC MC sysfs and uses `edac_op_state = EDAC_OPSTATE_INT`.

## Risks
`dmc520_edac_remove()` computes `irq_mask_all` only while freeing IRQs but clears interrupt control before accumulating it, so the intended disable mask is zero at the write point; that path is worth review. Non-DRAM interrupt lines can be requested and enabled but do not generate EDAC reports in current handlers. Invalid or zero memory width can lead to zero grain/rank-size-derived metadata. Shared IRQ handling returns `IRQ_NONE` unless relevant status bits are set.

## Test Signals
Tests should cover no-IRQ and ECC-disabled probe failures, named IRQ discovery, CE/UE counter reset, concurrent CE/UE interrupt serialization, rank count/size calculations, sysfs counter increments, and remove-time interrupt disable behavior.
