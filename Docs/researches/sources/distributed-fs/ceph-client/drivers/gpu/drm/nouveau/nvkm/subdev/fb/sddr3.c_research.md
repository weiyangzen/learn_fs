<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr3.c

## Purpose
Calculates SDR DDR3 mode-register values from BIOS timing data and existing mode register state.

## Important APIs, Types, And Functions
Defines `struct ramxlat`, translation helper `ramxlat`, tables for DDR3 CL, WR, and CWL encodings, and exported `nvkm_sddr3_calc`.

## Control Flow
The function reads timing version 0x10 or 0x20. Version 0x10 requires a header large enough to include CWL; otherwise it returns `-ENOSYS`. Version 0x20 decodes CL/CWL/WR from packed timing words and derives ODT from existing MR1 bits. It translates all values, updates MR0, MR1, and MR2, and leaves actual programming to callers.

## State And Persistence
Only `ram->mr[]` is changed. BIOS timing fields and current MR values are inputs.

## Dependencies And Integration Points
Used by RAM reclocking code through the shared Nouveau RAM layer. It depends on BIOS timing decoding and the caller's earlier capture of current mode registers.

## Risks And Edge Cases
Unsupported timing values or missing CWL data cause explicit errors. The version 0x20 ODT path is marked as a placeholder that should eventually come from VBIOS.

## Test Signals
Expected signals are successful MR calculation, no `-EINVAL` or `-ENOSYS` during reclocking, and stable DDR3 mode after memory frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr3.c -->
