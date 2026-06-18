# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore.c

Purpose: SPU-side restore program loaded by host `switch.c`. It reconstructs the upper local store, special channels, FPCR, decrementer, SRR0, event/tag masks, and final stopped/running behavior from the LSCSA.

Important functions: `fetch_regs_from_mem`, `restore_upper_240kb`, `restore_decr`, `write_ppu_mb`, `write_ppuint_mb`, `restore_fpcr`, `restore_srr0`, `restore_event_mask`, `restore_tag_mask`, `restore_complete`, and `main`.

Control flow: `main()` receives the LSCSA effective address through signal notification channels, fetches the register spill area, masks events/tags, builds DMA lists, GETLs upper local store, clears lock-line reservation, waits for tag completion, restores special state, and calls `restore_complete()`. That function patches instructions at `exit_fini` based on `stopped_status` so the final crt0 exit recreates illegal instruction, halt, stop-and-signal, single-step, running, or infinite-branch state.

State and dependencies: shares `regs_spill` and DMA list utilities with crt0 and `spu_utils.h`; generated into `spu_restore_dump.h` for host use. Risks include self-modifying exit code correctness, exact LSCSA offsets, channel ordering, and DMA list address assumptions. Test signals include context restore after each stopped-status combination, decrementer wrap events, mailbox restore, and successful host `SPU_RESTORE_COMPLETE`.
