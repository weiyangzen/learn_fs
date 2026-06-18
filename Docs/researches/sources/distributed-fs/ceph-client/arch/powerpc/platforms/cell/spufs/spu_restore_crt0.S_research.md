# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore_crt0.S

Purpose: SPU assembly entry/exit runtime for the restore helper. It sets up a minimal stack, calls C `main`, restores all 128 SPU GPRs from `regs_spill`, and exits with a restore-complete stop sequence.

Important symbols: global `regs_spill`, `_start`, `exit`, `_exit`, `exit_fini`, and `_exit_fini`. The `restore_reg_insts` loop is self-modifying-style code that iterates through registers 16-127 four at a time.

Control flow: `_start` initializes stack pointer at 16 KiB minus 16, creates a minimal frame, and branches to `main`. On return, `exit` restores higher registers from the spill area, then restores registers 0-15. `exit_fini` contains `stop SPU_RESTORE_COMPLETE` followed by padding `stop 0` instructions that `spu_restore.c` may patch to recreate the original stopped status.

State and dependencies: depends on `SIZEOF_SPU_SPILL_REGS`, `SPU_RESTORE_COMPLETE`, and the C helper filling `regs_spill`. Risks include register clobbering before all registers are restored, alignment requirements, and patchable instruction layout changing. Test signals are SPU helper object disassembly, generated dump header size/alignment, and successful restore of full register files.
