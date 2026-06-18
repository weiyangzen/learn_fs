# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_lbc.h

Purpose: Defines register layouts, bitfields, controller state, and helper APIs for the Freescale Local Bus Controller and its UPM/FCM/GPCM operating modes.

Important APIs, types, and functions: `struct fsl_lbc_bank` models bank base/option registers, `struct fsl_lbc_regs` mirrors BR/OR, MAR/MAMR/MBMR/MCMR, event, bus, clock, and FCM registers, `struct fsl_upm` describes an assigned UPM machine, and `struct fsl_lbc_ctrl` stores the device, lock, IRQ, mapped registers, bank count, and suspend shadows. Helpers include `fsl_lbc_addr()`, `fsl_lbc_find()`, `fsl_upm_find()`, `fsl_upm_start_pattern()`, `fsl_upm_end_pattern()`, `fsl_upm_run_pattern()`, and global `fsl_lbc_ctrl_dev`.

Control flow: Drivers locate a bank/UPM by physical base, lock the controller, program machine mode registers or FCM sequences, start UPM patterns by writing `MxMR_OP_RP`, access attached devices, end patterns by returning to normal operation, and service/clear LTESR events.

State and persistence: Runtime state is MMIO register content plus controller lock/IRQ/bookkeeping. Suspend support snapshots bank and controller registers for restore. No disk persistence exists.

Dependencies and integration points: Depends on MMIO helpers, device model, spinlocks, and Freescale NAND/UPM/localbus consumers. It bridges board device-tree mappings to low-level local bus registers.

Risks: Bitfield definitions directly encode hardware ABI. Incorrect bank matching or endian MMIO access can corrupt memory windows. UPM pattern mode is global to the machine and must be serialized. Event masks distinguish NAND-specific and full-controller faults; clearing the wrong bits can lose diagnostics.

Test signals: Validate BR/OR decoding, UPM start/end under lock, FCM NAND command sequences, LTESR interrupt handling, suspend/resume register restore, and address lookup for all configured localbus banks.
