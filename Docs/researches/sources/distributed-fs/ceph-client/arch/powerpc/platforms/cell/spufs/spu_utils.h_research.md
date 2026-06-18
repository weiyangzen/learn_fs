# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_utils.h

Purpose: shared SPU-side utility header for save and restore helper programs. It defines portable address/register unions, DMA list storage, LSCSA offset macros, and common channel/DMA helper sequences.

Important types and symbols: `addr64`, `spu_reg128v`, `struct dma_list_elem`, global aligned `dma_list[15]`, external `regs_spill`, `LSCSA_BYTE_OFFSET`, and `LSCSA_QW_OFFSET`. Helpers include `set_event_mask`, `set_tag_mask`, `build_dma_list`, `enqueue_putllc`, `set_tag_update`, `read_tag_status`, and `read_llar_status`.

Control flow: save/restore helpers call these routines to mask SPU events, restrict tag completion to tag group 0, prepare 15 DMA-list entries covering the upper 240 KiB of local store, clear lock-line reservation with PUTLLC, and wait for tag/atomic status.

State and dependencies: relies on `struct spu_lscsa` layout, SPU intrinsic channel numbers, and 16 KiB chunks. Risks include global definitions in a header causing duplicate storage if included in multiple linked objects, null-pointer offset calculation assumptions, and hardcoded DMA command opcodes. Test signals include helper build, correct DMA list effective addresses, and save/restore of all local-store ranges.
