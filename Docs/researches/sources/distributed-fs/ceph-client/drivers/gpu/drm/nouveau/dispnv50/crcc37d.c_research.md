<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.c

### Purpose
`crcc37d.c` implements the Volta-class C37D CRC callback table. It programs `NVC37D` CRC control, reuses a large notifier layout, selects either RG or output CRC data, and reports notifier completion and overflow status.

### Key APIs And Functions
`crcc37d_set_src()` maps generic source types to `PRIMARY_CRC` values for SOR, PIOR, and SF. `crcc37d_set_ctx()` binds or clears the CRC CTXDMA. `crcc37d_get_entry()` returns `rg_crc` for the RG source and `output_crc[0]` otherwise. `crcc37d_ctx_finished()` decodes done and overflow bits. The exported `crcc37d` table uses constants from `crcc37d.h`.

### Control Flow And State
Enable ordering mirrors older classes: set the context DMA, then CRC control. Disable clears CRC control and then the context. The function table itself carries notifier size and entry count; runtime state stays in `struct nv50_crc` from the generic layer.

### Dependencies And Integration
The file depends on `crcc37d.h`, `clc37d`, `pushc37b`, and Nouveau core/head/display helpers. It is selected by C37D-generation core tables and is reused indirectly by later C57D/CA7D files for notifier parsing.

### Risks And Test Signals
Only a subset of generic source types is explicitly mapped; unsupported types fall through to no primary CRC bits. Tests should cover RG vs output source entry selection, overflow bit decoding, DP/SOR source capture, context flips near the threshold, and disable behavior during output reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.c -->
