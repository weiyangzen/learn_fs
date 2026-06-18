# sources/distributed-fs/ceph-client/drivers/memory/ti-emif-sram-pm.S

Purpose: This ARMv7 assembly file is the SRAM-resident low-level PM routine set for TI EMIF. It saves/restores EMIF context, enters/exits/aborts SDRAM self-refresh, reruns DDR3 hardware leveling, and reserves the SRAM data block used by the C driver.

Important APIs/types/functions: Entry points are `ti_emif_sram`, `ti_emif_save_context`, `ti_emif_restore_context`, `ti_emif_run_hw_leveling`, `ti_emif_enter_sr`, `ti_emif_exit_sr`, `ti_emif_abort_sr`, `ti_emif_pm_sram_data`, and `ti_emif_sram_sz`. Offsets come from `ti-emif-asm-offsets.h`; register constants come from `emif.h`.

Control flow: Save-context uses virtual EMIF/data addresses, stores common EMIF registers, and conditionally saves AM43xx extra registers plus a block of PHY control registers. Restore-context uses physical addresses, writes timing/refresh/PM/COS/OCP/PHY registers, restores ZQ config, and writes SDRAM config last for DDR2. Hardware leveling starts DDR3 read/write leveling and busy-waits for completion. Enter/exit/abort self-refresh manipulate PM control bits and wait for EMIF ready where needed.

State and persistence: Saved EMIF context is stored in SRAM data (`ti_emif_pm_sram_data`) and survives while SRAM does. The routines directly mutate EMIF hardware registers during low-power transitions when DDR may be unavailable.

Dependencies and integration: The file depends on ARM linkage/assembler conventions, generated asm offsets, and C-side copying/address setup from `ti-emif-pm.c`. It is called by platform PM code through the exported function table.

Risks and test signals: Risks include incorrect generated offsets, using virtual addresses after MMU-off, unbounded wait loops if EMIF never becomes ready, and missing AM43xx PHY registers. Test signals include assembly build with offset generation, SRAM copy size correctness, suspend/resume from DDR2 and DDR3, hardware-leveling completion, and abort path returning DDR to ready state.
