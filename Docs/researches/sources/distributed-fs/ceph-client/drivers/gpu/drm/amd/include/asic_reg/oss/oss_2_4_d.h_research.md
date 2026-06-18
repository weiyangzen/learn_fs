# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_d.h

## Purpose
`oss_2_4_d.h` is the OSS 2.4 register address header for the AMDGPU Linux driver. It contains only preprocessor constants mapping symbolic register names to MMIO register indices for the OSS block generation used by Iceland/CIK-era hardware. The companion headers in the same directory provide field masks and enum values; this file anchors those fields to actual register offsets consumed by low-level `RREG32()` and `WREG32()` accessors.

The covered hardware areas are interrupt handler (`IH_*`), semaphore/mailbox (`SEM_*`), system register bus manager (`SRBM_*`), SDMA0/SDMA1 engine control and rings, and HDP/XDP host data path registers.

## Important APIs, Types, and Functions
- The public interface is a flat list of `#define mm...` constants. There are no C functions, structs, or runtime declarations.
- IH address constants include `mmIH_VMID_0_LUT` through `mmIH_VMID_15_LUT`, `mmIH_RB_CNTL`, `mmIH_RB_BASE`, `mmIH_RB_RPTR`, `mmIH_RB_WPTR`, writeback pointer address registers, interrupt control/status, DSM match controls, and `mmIH_VERSION`.
- SEM constants cover MCIF and client request configuration (`mmSEM_MCIF_CONFIG`, `mmSDMA_CONFIG`, `mmUVD_CONFIG`, `mmVCE_CONFIG`, `mmACP_CONFIG`, `mmCPG_CONFIG`, `mmCPC1_CONFIG`, `mmCPC2_CONFIG`), status/EDC, mailbox payload/control, and "chicken bit" workaround controls.
- SRBM constants include core control/status, soft reset, clock enable controls, read/firewall error reporting, DSM triggers, perf counters, domain address windows, GRBM index/select indirection, virtualization controls, and CAM registers.
- SDMA constants are repeated for engines 0 and 1. Each engine has microcode, power/clock, ring buffer, indirect buffer, context, doorbell, virtual address, watermark, CSA, dummy, preempt, performance, and status registers. Register ranges are separated by engine and queue context, for example `mmSDMA0_GFX_*`, `mmSDMA0_RLC0_*`, `mmSDMA0_RLC1_*`, then the same pattern for `SDMA1`.
- HDP/XDP constants define host path, nonsurface addressing, tiling/address config, memio access, direct-to-HDP flush/bar update slots, peer-to-peer mailbox/BAR config, status/debug, and high BAR address bits.

## Control Flow
There is no executable control flow in this header. Runtime control flow appears in consumers such as `amdgpu/iceland_ih.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/cik.c`, and `amdgpu/vi.c`, where code selects one of these register offsets, reads or writes it through AMDGPU MMIO helpers, and composes fields using `oss_2_4_sh_mask.h`. For example, interrupt setup writes IH ring base/read/write pointer registers and toggles `mmIH_RB_CNTL`; SDMA setup iterates engine offsets from `mmSDMA0_*` to configure rings, IBs, writeback pointers, and enable bits.

## State and Persistence Behavior
This file stores no driver state. The values are compile-time ABI constants for hardware registers. State lives in the GPU registers reached through these offsets and in driver-owned objects that decide what to write. Because many registers control persistent hardware modes until reset or reprogramming, incorrect constants can persist as bad ring setup, disabled interrupts, stale writeback addresses, bad VMID selection, or broken host cache behavior until device reset.

## Dependencies and Integration Points
- Included directly by `drivers/gpu/drm/amd/amdgpu/iceland_ih.c` and `drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c` for OSS 2.4-specific register programming.
- Designed to be included with `oss_2_4_sh_mask.h` so address constants and field masks share the same register schema.
- Indirectly relies on AMDGPU register access helpers such as `RREG32`, `WREG32`, `REG_SET_FIELD`, and engine offset tables in SDMA code.
- Register names overlap with newer generation headers, so include ordering and ASIC-specific source selection are the boundary that keeps OSS 2.4 offsets from being used on incompatible hardware.

## Risks
- A wrong offset silently targets a different hardware register. The highest risk areas are reset, interrupt ring control, SDMA ring base/write pointer registers, and HDP cache flush controls because errors can hang command submission or lose interrupts.
- The `SDMA0` and `SDMA1` blocks are highly repetitive; manual edits can accidentally update one engine but not the other or use the wrong engine offset.
- The header contains both low address spaces such as IH/SRBM and high address ranges such as perf counters and CAM/domain registers; callers must use the correct MMIO access path for the target ASIC.
- Constants are generated hardware documentation artifacts. Refactoring names without preserving compatibility can break existing driver code that uses these exact macros.

## Test Signals
- Compile coverage: build the AMDGPU driver with `CONFIG_DRM_AMDGPU` and an affected ASIC path to catch missing or renamed macros.
- Runtime bring-up signals: IH ring initialization succeeds, interrupts are delivered, SDMA rings start and process jobs, and no SRBM read/firewall errors appear in kernel logs.
- Targeted checks: compare `mmIH_RB_CNTL`, `mmIH_RB_BASE`, `mmSDMA0_GFX_RB_CNTL`, `mmSDMA1_GFX_RB_CNTL`, and `mmHDP_XDP_CGTT_BLK_CTRL` values against the vendor register database for OSS 2.4.
- Regression symptoms: GPU reset loops, stuck SDMA fences, IRQ storms or missing IRQs, HDP cache coherency failures, or failed suspend/resume on affected hardware.
