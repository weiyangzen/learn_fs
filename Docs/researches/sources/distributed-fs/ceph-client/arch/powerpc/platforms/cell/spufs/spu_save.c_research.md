# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save.c

Purpose: SPU-side save program loaded by host `switch.c`. It saves local store beyond the first 16 KiB, FPCR, decrementer, SRR0, event/tag masks, and the register spill area into the LSCSA.

Important functions: `save_event_mask`, `save_tag_mask`, `save_upper_240kb`, `save_fpcr`, `save_decr`, `save_srr0`, `spill_regs_to_mem`, `enqueue_sync`, `save_complete`, and `main`.

Control flow: `main()` reads the LSCSA effective address from signal notification channels, relies on crt0 to save registers, saves masks, masks events/tags, builds a DMA list for upper local store, PUTLs that region to CSA, saves special state, issues a PUTLLC to clear lock-line reservation, PUTs the register spill area, syncs tag group 0, reads tag and atomic status, and stops with `SPU_SAVE_COMPLETE`.

State and dependencies: uses `spu_utils.h`, `regs_spill` from `spu_save_crt0.S`, and LSCSA field offsets from `asm/spu_csa.h`. Host `switch.c` waits for the completion stop code. Risks include exact ordering of DMA and channel operations, size/alignment assumptions for the 240 KiB DMA list, and loss of state if crt0 register spill layout changes. Test signals include save/restore round trips, FPCR/decrementer preservation, local-store checksums, and completion status validation.
