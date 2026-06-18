# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_elbc_nand.c

## Purpose
Provides the Freescale Enhanced Local Bus Controller NAND driver using the eLBC Flash Control Machine. It maps one NAND chip-select bank, translates legacy NAND commands into eLBC FCM register sequences, handles controller-buffer data movement, configures hardware ECC when selected, and registers the resulting MTD device with command-line, RedBoot, or device-tree partitions.

## Important APIs, Types, And Functions
`struct fsl_elbc_mtd` stores per-bank NAND chip state, the shared LBC controller, mapped chip buffer, page-size mode, and FMR value. `struct fsl_elbc_fcm_ctrl` embeds `nand_controller` plus shared command-buffer state such as current FCM buffer address, page, read byte count, column, buffer index, command status, MDR, OOB mode, and max bitflips. Key functions include `set_addr()`, `fsl_elbc_run_command()`, `fsl_elbc_cmdfunc()`, `fsl_elbc_read_buf()`, `fsl_elbc_write_buf()`, `fsl_elbc_wait()`, `fsl_elbc_read_page()`, `fsl_elbc_write_page()`, and `fsl_elbc_attach_chip()`.

## Control Flow
`fsl_elbc_nand_probe()` waits for the global LBC controller, resolves the device-tree resource to a bank configured for FCM, allocates shared controller state under `fsl_elbc_nand_mutex`, maps the chip buffer, initializes NAND legacy callbacks, and runs `nand_scan()`. `fsl_elbc_cmdfunc()` handles READ0/READOOB/READID/PARAM/ERASE/SEQIN/PAGEPROG/STATUS/RESET by programming FIR/FCR/FBAR/FPAR/FBCR/MDR registers, calling `fsl_elbc_run_command()`, and serving subsequent byte/buffer reads from the mapped FCM buffer.

## State And Persistence
Runtime state is split between per-bank `priv` and shared `ctrl->nand`; the shared state tracks one active command path and must reflect FCM buffer index and lengths accurately. Persistent flash effects are page programs, erases, hardware-generated ECC bytes, flash-resident BBT descriptors at OOB offset 11, and registered partitions. Remove unregisters the MTD, cleans NAND, unmaps the bank buffer, clears the bank slot, and frees the shared controller when its counter reaches zero.

## Dependencies And Integration Points
Depends on `asm/fsl_lbc.h`, global `fsl_lbc_ctrl_dev`, big-endian LBC register accessors, raw NAND legacy hooks, MTD OOB layout APIs, and MTD partition parsers. The driver uses `nand_controller_ops.attach_chip` to infer or apply ECC settings after NAND identification.

## Risks
The command engine relies on controller-global state, so concurrent bank access would be fragile unless serialized by the NAND core. Only 512-byte and 2048-byte pages are supported. Hardware ECC correction accounting is approximate: LTECCR indicates corrected subpages, but the FIXME notes it only increments corrected once for large-page multi-subpage corrections. Partial/subpage writes intentionally write a full data/OOB buffer path and may surprise callers.

## Test Signals
Probe should log the eLBC bank and address. Register-level tests should cover READID, full-page reads with ECC, OOB-only reads, program/erase status, 512-byte and 2 KiB page modes, partition parser output, and removal after multiple banks. ECC tests should watch `mtd->ecc_stats.corrected`, `failed`, and returned max bitflips.
