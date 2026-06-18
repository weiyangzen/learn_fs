# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/base.c

## Purpose
Provides generic falcon ownership, memory transfer, start/reset, and discovery helpers. Falcon is NVIDIA's small embedded controller core used by SEC2, PMU, GSP, and other units.

## Important APIs, types, and functions
Key APIs include `nvkm_falcon_get()`, `nvkm_falcon_put()`, `nvkm_falcon_ctor()`, `nvkm_falcon_dma_wr()`, `nvkm_falcon_pio_rd()`, `nvkm_falcon_pio_wr()`, `nvkm_falcon_load_imem()`, `nvkm_falcon_load_dmem()`, `nvkm_falcon_start()`, `nvkm_falcon_reset()`, `nvkm_falcon_intr_retrigger()`, and `nvkm_falcon_riscv_active()`.

## Control flow, state, and persistence
`get()` serializes ownership, performs one-time discovery from TOP/MMIO, records version, secret capability, port counts, IMEM/DMEM limits, and optional debug state. DMA and PIO helpers select memory backends, validate alignment, transfer chunks, poll completion, and optionally trace data. DMEM loads are protected by `dmem_mutex`.

## Dependencies and integration points
Depends on generation `nvkm_falcon_func`, TOP, MC/timer helpers, and register access. Used by firmware boot, SEC2 queues, ACR WPR building, and all falcon-backed engines.

## Risks and test signals
Ownership misuse returns `-EBUSY`; alignment/length mistakes trigger warnings. Signals include falcon acquisition logs, transfer timeouts, and successful firmware start/boot.
