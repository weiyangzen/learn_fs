<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc57d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc57d.c

### Purpose
`crcc57d.c` provides the C57D CRC source-programming callback while reusing the C37D notifier format and reader/completion helpers.

### Key APIs And Functions
`crcc57d_set_src()` builds `NVC57D_HEAD_SET_CRC_CONTROL` arguments for SOR and SF sources, binds the notifier context DMA on enable, and clears both control and CTXDMA on disable. The exported `crcc57d` table points `set_ctx`, `get_entry`, and `ctx_finished` to C37D helpers and uses C37D entry count, threshold, and notifier size constants.

### Control Flow And State
The class-specific control path is minimal: reserve push space, optionally write context DMA, then write CRC control. Runtime state is owned by `crc.c`; this file only expresses how the class wants source and context methods encoded.

### Dependencies And Integration
It depends on `crcc37d.h`, `clc57d`, `pushc37b`, and the shared core/display/head interfaces. `corec57d.c` exposes this table when debugfs CRC support is built.

### Risks And Test Signals
PIOR, DAC, and RG source types are not explicitly mapped here, so caller source mapping and hardware support need coverage. Tests should include DP/SOR CRC capture, SF source capture, disable/re-enable, notifier overflow reuse from C37D, and C57D-specific push method validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc57d.c -->
