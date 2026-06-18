<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sid.h

## Purpose
`sid.h` is the Southern Islands ASIC hardware definition header for the Radeon DRM driver. It supplies SI-family register addresses, bitfield helpers, golden configuration constants, PM4 packet encoders, DMA packet encoders, and media/display/VM/power-management register definitions used by the SI display, command processor, DMA, SMC, UVD, VCE, interrupt, memory-controller, and DPM code.

## Important APIs, types, and definitions
- ASIC topology and golden constants: `TAHITI_RB_BITMAP_WIDTH_PER_SH`, `*_GB_ADDR_CONFIG_GOLDEN`, and maximum masks for shader engines, SIMDs, backends, pipes, LDS, and TCCs.
- SMC and clock/power registers: `SMC_IND_*`, `SMC_MESSAGE_0`, `CG_SPLL_*`, `CG_UPLL_*`, `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, thermal/fan registers, CAC/ULV controls, and power-gating flags.
- VM and memory-controller definitions: `VM_L2_CNTL*`, `VM_CONTEXT*_CNTL`, fault status fields, invalidation registers, FB/AGP/system aperture registers, MC timing/training registers, and memory-clock PLL fields.
- Display and interrupt definitions: DMIF/LB priority and watermarks, vblank/vline/pflip interrupt bits, HPD status/control registers, DCE6 audio endpoint registers, audio DTO registers, and AFMT source selection.
- Graphics and CP/RLC definitions: `GRBM_*`, soft reset masks, `GRBM_GFX_INDEX`, CP ring registers, interrupt bits, scratch registers, shader/tiling/backend registers, and RLC power-gating/register save-restore fields.
- Packet helpers: `PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`, many `PACKET3_*` opcodes and field helpers, async DMA ring registers, `DMA_PACKET`, `DMA_IB_PACKET`, `DMA_PTE_PDE_PACKET`, and DMA opcodes.
- Media definitions: UVD ring/status/clock-gating registers and VCE firmware, ring, cache, command, and PLL definitions.

## Control flow and integration points
The file has no executable control flow. It is included by SI implementation files such as `si.c`, `si_dma.c`, `si_dpm.c`, `si_smc.c`, DCE6 audio/display code, and Radeon VCE support. Those consumers use the macros to compose MMIO writes, indirect SMC accesses, CP command streams, DMA command streams, VM invalidation sequences, media firmware setup, display interrupt handling, and power-management transitions.

## State and persistence behavior
All persistent state represented by this header lives in hardware registers or command streams emitted to hardware. Writes using these definitions configure clocks, voltage/power gates, PLLs, memory mappings, VM contexts, interrupts, CP rings, RLC state, display/audio state, DMA rings, UVD, and VCE. Packet macros create transient CPU-side dwords that become persistent GPU state after ring execution.

## Dependencies and constraints
Consumers must provide Radeon packet constants such as `RADEON_PACKET_TYPE0`, `RADEON_PACKET_TYPE3`, and `REG_SET`, plus MMIO/indirect access helpers. Register addresses and bitfields are SI-specific; they must not be reused for CIK or Sumo without verifying the register map. Many helpers shift values without full range validation, so call sites must mask, clamp, and respect ordering requirements for PLL changes, VM invalidation, CP packets, and DMA packets.

## Risks and test signals
The risk is high because a wrong address, mask, shift, or packet count can hang the GPU, misprogram clocks, corrupt VM translations, lose interrupts, break modesets, or corrupt copy/render/media command streams. Useful validation signals include SI probe and modeset, vblank/pflip/HPD interrupts, ring and IB tests, DMA copy tests, VM fault/invalidation tests, DPM transitions, suspend/resume, UVD decode, VCE encode, and register readback against known-good traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sid.h -->
