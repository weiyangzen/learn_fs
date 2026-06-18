# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save_crt0.S

Purpose: SPU assembly entry runtime for the save helper. It spills all 128 SPU GPRs into `regs_spill`, sets up a stack, and calls C `main`.

Important symbols: global `regs_spill`, `_start`, `exit`, and `_exit`. The file allocates `SIZEOF_SPU_SPILL_REGS` aligned storage and uses `stqa` for registers 0-15 plus a loop around `save_reg_insts` for registers 16-127.

Control flow: `_start` immediately saves the first 16 registers, then iterates through the remaining registers in blocks of four. After register capture, it initializes the stack at 16 KiB minus 16, creates a minimal frame for `main`, and branches. If `main` unexpectedly returns, `exit` executes `stop 0`, which should be treated as a failed save path by the host because normal completion uses `SPU_SAVE_COMPLETE`.

State and dependencies: tightly coupled to `spu_save.c`, `spu_utils.h`, and SPU ABI register naming. Risks include alignment-sensitive instruction rewriting, stack overlap with save helper code/data, and object size changes affecting host DMA loading. Test signals include disassembly of generated helper, full register preservation, and no accidental return from `main`.
