<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cla0b5.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cla0b5.h

Purpose: `cla0b5.h` defines the `NVA0B5` copy engine/memory-to-memory class used by newer Nouveau buffer moves and device-memory migration. It is a macro-only ABI header for DMA copy launch, physical/virtual aperture selection, line geometry, and component remapping.

Important APIs and types: source/destination physical mode methods select local framebuffer, coherent system memory, or noncoherent system memory. `NVA0B5_LAUNCH_DMA` contains transfer type, flush, semaphore, interrupt, source/destination layout, multiline, remap, L2 bypass, virtual/physical source/destination, and semaphore reduction fields. Offset, pitch, line length, and line count methods describe the copy. Remap constants and `SET_REMAP_COMPONENTS` allow constant fills or component swizzles using source components, constants, or no-write lanes.

Control flow: `nouveau_boa0b5.c` uses the header for BO moves: program offsets/pitches/line geometry and launch a non-pipelined flushed pitch-to-pitch copy. `nouveau_dmem.c` uses it for HMM/device-memory migration, selecting physical source/destination targets, emitting launch flags for physical addressing, and using remap mode for memory clear/fill-style operations.

State and persistence: copy state persists in the copy engine object until overwritten. The durable effect is modified destination memory or migrated page contents. Physical-mode methods affect how subsequent physical addresses are interpreted.

Dependencies and integration: included by `nouveau_boa0b5.c` and `nouveau_dmem.c`; it depends on Nouveau memory management, HMM migration paths, channel push helpers, and kernel address helpers such as `upper_32_bits`/`lower_32_bits`.

Risks: mixing virtual and physical address flags with the wrong address source can corrupt memory or fault the engine. Coherent versus noncoherent sysmem target selection affects CPU/GPU visibility. Remap component fields are compact and can turn a copy into a fill/no-write unexpectedly. Launch flag semantics differ substantially from older `NV9039`, so shared copy helpers must not assume compatible bit positions.

Test signals: BO migration tests, VRAM-to-sysmem and sysmem-to-VRAM dmem migrations, high-address copies, large multi-line transfers, and dmem clear/remap paths. Correctness signals include byte-accurate migrated pages, no copy engine faults, no cache-coherency stale reads, and successful memory-pressure migration loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cla0b5.h -->
