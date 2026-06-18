# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk104.c

## Purpose
Defines GK104/Kepler VMM descriptors by reusing GF100 PTE/PDE logic and adding an LPT invalidation encoding for large-page shadow PTEs.

## Important APIs, Types, And Functions
Exports `gk104_vmm_lpt_invalid`, descriptor arrays `gk104_vmm_desc_17_12`, `gk104_vmm_desc_17_17`, `gk104_vmm_desc_16_12`, `gk104_vmm_desc_16_16`, and constructor `gk104_vmm_new`. The local `gk104_vmm_lpt` descriptor supplies `.invalid`, `.unmap`, and `.mem`.

## Control Flow
The constructor delegates to `gf100_vmm_new_`, selecting 16-bit or 17-bit big-page tables according to framebuffer configuration. Mapping and flushing are entirely through GF100 helpers; only invalid LPT entries differ, using `VALID_FALSE + PRIV` to make the MMU ignore corresponding small-page entries.

## State And Persistence
State lives in GF100-style page tables and instance memory. The file defines no private runtime state; it selects page descriptors and supported page flags for GK104.

## Dependencies And Integration Points
Depends on `vmm.h` declarations and GF100 exported functions. GM20B and GK20A also reuse these descriptor arrays. It integrates into the MMU factory for Kepler-class GPUs.

## Risks And Test Signals
The main risk is descriptor mismatch between big-page size and LPT/SPT layout, causing invalid entries to be interpreted as real mappings. Test 16/17-bit big-page hardware, small-page fallback, sparse/invalid large-page holes, and compile-time consumers of exported descriptor arrays.
