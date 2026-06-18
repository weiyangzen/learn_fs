
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/regs.h

Purpose: register map and bit definitions for legacy Nouveau PGRAPH engines, covering NV03/NV04 through NV50-era context-control, status, trap, tile, DMA, and rendering state registers.

Important APIs/types/functions: this header is macro-only. It defines addresses such as `NV03_PGRAPH_INTR`, `NV04_PGRAPH_CTX_*`, `NV10_PGRAPH_CTX_*`, `NV20_PGRAPH_TILE/TSIZE/TLIMIT`, `NV40_PGRAPH_CTXCTL_*`, `NV50_PGRAPH_CTXCTL_*`, and many status/source bit masks.

Control flow/state: no execution; it names hardware state used by init, interrupt, tiling, and context code. Persistence is in device MMIO registers and GPU context images built by other files.

Dependencies/integration: included by old GR files (`nv04.c`, `nv10.c`, `nv20.c`, `nv40.c`, variants). Risks are incorrect constants causing silent hardware misprogramming, wrong bit decoding, or bad context save/restore. Test signals are compile coverage plus runtime validation of interrupts, context switching, and tile programming on affected chipsets.
