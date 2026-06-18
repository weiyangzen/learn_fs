# sources/distributed-fs/ceph-client/drivers/memory/fsl_ifc.c

## Purpose
`fsl_ifc.c` is the Freescale Integrated Flash Controller core driver. It maps global and runtime IFC registers, initializes common event reporting, exposes helper symbols for child flash/NAND drivers, dispatches IFC and NAND interrupts, and populates child devices.

## Important APIs, Types, And Functions
The file exports global `fsl_ifc_ctrl_dev`, `convert_ifc_address()`, and `fsl_ifc_find()`. `fsl_ifc_find()` walks CSPR chip-select registers to locate a bank by physical base address. `fsl_ifc_ctrl_init()` clears common chip-select errors and enables common event/error interrupts. `check_nand_stat()` serializes access to NAND event status with `nand_irq_lock`, clears events, stores `ctrl->nand_stat`, and wakes `ctrl->nand_wait`.

`fsl_ifc_ctrl_irq()` handles common IFC chip-select transaction errors, logs read/write, AXI ID, SRC ID, and error address, then also checks NAND status. `fsl_ifc_nand_irq()` handles the dedicated NAND IRQ. Probe maps registers with `of_iomap()`, determines endian mode, reads IFC version, selects bank count and runtime-register offset, maps IRQs, initializes wait queues, requests interrupts, and populates children.

## Control Flow
The driver registers at `subsys_initcall()` so it is available before child flash drivers. Probe maps global registers, configures endian access via fields in `struct fsl_ifc_ctrl`, computes `rregs` from version-specific offsets, initializes common events, requests controller and optional NAND IRQs, then calls `of_platform_default_populate()`. Remove depopulates children, frees IRQs, disposes IRQ mappings, unmaps registers, and clears drvdata.

## State And Persistence
The global controller pointer is shared with child drivers. Hardware state includes common event enable/status registers and NAND runtime event status. Runtime wait state is stored in `nand_wait` and `nand_stat`. State is not persisted or restored across power management in this file.

## Dependencies And Integration Points
It depends on `linux/fsl_ifc.h`, OF address/IRQ helpers, irqdomain mappings, child platform device population, and IFC endian accessor macros. Child NAND/NOR drivers use the exported controller pointer and bank lookup helpers.

## Risks
The single global `fsl_ifc_ctrl_dev` assumes one IFC controller. Error paths manually free IRQs and unmap resources, so ordering is sensitive. `remove()` calls `free_irq()` even for `nand_irq` values that may be zero if absent, so platform behavior should be verified. No PM restore path means event enables may be lost across deep suspend.

## Test Signals
Probe logs IFC version and bank count. Tests should verify endian property handling, bank lookup with valid/invalid CSPR entries, common transaction error logging, NAND IRQ wakeups, child population, and clean unwind when IRQ mapping or request fails.
