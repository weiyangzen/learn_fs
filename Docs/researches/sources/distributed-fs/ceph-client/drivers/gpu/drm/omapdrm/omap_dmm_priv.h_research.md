# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_priv.h

Purpose: Defines private DMM/TILER register offsets, IRQ/status bits, PAT descriptor formats, refill engine structures, platform data, and the central `struct dmm` used by `omap_dmm_tiler.c`.

Important APIs/types: Register macros cover DMM revision/sysconfig, LISA map, TILER orientation, PAT geometry/view/IRQ/status/descriptor registers, and PEG priority registers. IRQ/status masks identify transaction completion and error conditions. `struct pat_area`, `struct pat_ctrl`, and `struct pat` describe PAT refill descriptors. `struct dmm_txn` tracks descriptor allocation within a refill buffer. `struct refill_engine` tracks one PAT engine, refill memory, completion, async state, and idle list node. `struct dmm` stores MMIO, IRQ, dummy page, refill memory, engine pool, TCM containers, allocation list, platform data, and DRA7 i878 DMA workaround state.

Control flow: The implementation allocates and initializes these objects at DMM probe, uses transactions to append PAT descriptors for TILER region fills, and releases engines via IRQ or synchronous completion.

State and persistence: All state is runtime-only. DMM LUT contents are hardware state and are reinitialized on probe/resume.

Dependencies/integration: Depends on `struct pat_area` from the public TILER header, TCM allocator objects, DMA engine concepts, and OMAP GEM/fbdev users through TILER APIs.

Risks and test signals: Bitfield layouts in `struct pat_ctrl` must match hardware descriptor encoding and endianness expectations. Refill buffer sizing assumes worst-case descriptor counts. Test compile/layout on supported architectures, DMM probe, resume LUT refill, DRA7 workaround path, and error IRQ reporting.
