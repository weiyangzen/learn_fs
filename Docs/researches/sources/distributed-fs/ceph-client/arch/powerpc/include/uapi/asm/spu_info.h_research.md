<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/spu_info.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/spu_info.h

Purpose: Defines Cell SPU DMA and proxy-DMA information structures exposed to userspace tooling.

Important APIs/types/functions: Userspace `struct mfc_cq_sr`, `struct spu_dma_info`, and `struct spu_proxydma_info`.

Control flow: SPU filesystem/debug interfaces fill these structures with DMA queue status and command data for userspace inspection.

State and persistence: Structures serialize SPU DMA engine state and command queue contents.

Dependencies and integration points: Depends on Linux types and Cell SPU support.

Risks: Struct layouts are ABI for Cell debugging tools. The `mfc_cq_sr` userspace guard avoids duplicate kernel declarations.

Test signals: Cell/SPU tooling compile tests, SPU DMA info reads, and structure layout checks.

Source read size: 40 lines, 832 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/spu_info.h -->
