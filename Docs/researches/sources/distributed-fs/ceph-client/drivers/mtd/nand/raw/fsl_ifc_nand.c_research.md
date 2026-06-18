# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_ifc_nand.c

## Purpose
Implements the Freescale Integrated Flash Controller NAND driver. It binds a NAND chip select configured in the IFC global registers, maps the controller SRAM buffer, programs IFC NAND-machine FIR/FCR sequences for NAND operations, supports 8-bit and 16-bit buses, and configures on-host hardware ECC from CSOR settings.

## Important APIs, Types, And Functions
`struct fsl_ifc_mtd` holds one NAND chip, the shared IFC controller, mapped SRAM base, bank number, and buffer-number mask. `struct fsl_ifc_nand_ctrl` embeds `nand_controller` and stores shared active-command state: buffer address, page, column, index, read length, OOB/ECC-read flags, and max bitflips. Important functions are `set_addr()`, `fsl_ifc_run_command()`, `fsl_ifc_cmdfunc()`, `fsl_ifc_wait()`, `check_erased_page()`, `fsl_ifc_read_page()`, `fsl_ifc_attach_chip()`, `fsl_ifc_sram_init()`, and `fsl_ifc_chip_init()`.

## Control Flow
`fsl_ifc_nand_probe()` resolves the DT resource, matches it to an IFC NAND bank, allocates or reuses shared controller state, maps the bank SRAM, enables NAND-machine events/interrupts, initializes chip callbacks, scans the NAND, and registers MTD partitions. `fsl_ifc_cmdfunc()` translates legacy NAND commands into IFC register programs and starts sequences with `fsl_ifc_run_command()`. Full READ0 operations set `eccread`, read the full page plus OOB, and let `fsl_ifc_run_command()` consume ECCSTAT registers after the interrupt-complete event.

## State And Persistence
Persistent flash state includes page data, OOB, hardware ECC layout, BBT descriptors, and partition data. Runtime state is controller-global through `ifc_nand_ctrl`, including current DMA/SRAM index and ECC status. `fsl_ifc_sram_init()` may temporarily rewrite CSOR/CSOR_EXT for IFC 1.1.0 SRAM initialization, then restores them. Cleanup unregisters MTD, cleans NAND, unmaps SRAM, clears the bank slot, and frees the shared controller when unused.

## Dependencies And Integration Points
Depends on `linux/fsl_ifc.h`, global `fsl_ifc_ctrl_dev`, IFC runtime/global register blocks, raw NAND legacy callbacks, MTD OOB layout APIs, and partition parsers. It uses IFC interrupt state (`ctrl->nand_stat`) and wait queues managed by the IFC core.

## Risks
The source uses a file-global `ifc_nand_ctrl`, so multi-controller assumptions must remain valid. The remove path decrements `counter`, but the probe path shown initializes the shared object without visibly incrementing it, which is a lifecycle risk if multiple chips or removal are exercised. IFC erratum handling disables direct ECCER reporting and reconstructs erased-page behavior in software; regressions can misclassify erased pages as failed. Small-page 8-bit BBT offsets are modified globally.

## Test Signals
Exercise bank matching, SRAM initialization across IFC versions, 8-bit and 16-bit `read_byte` paths, READID/PARAM, full-page ECC reads, erased-page correction, program/erase status, OOB layout/free regions, partition parsing, and module removal. Watch `nand_stat`, ECCSTAT-derived corrected counts, timeout/write-protect logs, and returned max bitflips.
