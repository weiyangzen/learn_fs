# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_d.h

## Purpose
`gmc_6_0_d.h` is the Southern Islands / GMC 6.0 register-address header for the AMD GPU memory-controller block. It gives driver code symbolic names for direct MMIO register offsets (`mm...`) and indexed memory-controller debug/register-table entries (`ix...`) used to initialize, train, power-manage, and diagnose the GPU memory controller, GPUVM, ATC, crossbar, hub, and memory PHY/PLL paths.

The file is a generated-style hardware contract, not an implementation module. Its value is address stability: code in `amdgpu`, display, and legacy power-management paths can refer to named registers instead of embedding most raw offsets.

## Important APIs, Types, And Functions
This header declares no C functions, structs, enums, or storage. Its API surface is 1,248 preprocessor constants protected by `GMC_6_0_D_H`.

The largest groups are:
- `ixMC_IO_DEBUG_*` and `ixMC_TSM_DEBUG_*`: indirect debug-table indices for memory IO lanes, command/address lanes, DQ/DBI/EDC/WCK/WCDR training, per-D0/D1 channel state, and training-state-machine debug access.
- `mmATC_*`: address-translation-cache and ATS control, status, aperture, fault, and VMID-to-PASID mapping registers.
- `mmGMCON_*`: memory-controller register-engine, save/restore, power-gating FSM, and performance-monitor registers.
- `mmMC_ARB_*`, `mmMC_CITF_*`, `mmMC_HUB_*`, `mmMC_XBAR_*`, and `mmMC_XPB_*`: memory arbitration, client-interface, hub read/write datapath, crossbar, peer-to-peer, routing, credit, and performance registers.
- `mmMC_BIST_*`, `mmMC_SEQ_*`, `mmMC_TRAIN_*`, `mmMC_IO_*`, and `mmMPLL_*`: memory BIST, sequencer, microcode/training, IO PHY, and memory PLL registers.
- `mmMC_VM_*` and `mmVM_*`: framebuffer/system/AGP aperture, L1/L2 TLB/cache, page-table context, invalidation, fault, and partially resident texture aperture registers.

The paired `gmc_6_0_sh_mask.h` supplies bit masks and shifts for many of these address constants. Typical call sites combine an address from this file with masks from the paired header via `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

## Control Flow
The header has no runtime control flow. It affects control flow by selecting the hardware register that later code reads or writes.

In `amdgpu/gmc_v6_0.c`, these constants drive the GMC bring-up sequence: stop or blackout the memory controller, optionally upload MC firmware through `mmMC_SEQ_IO_DEBUG_INDEX`, `mmMC_SEQ_IO_DEBUG_DATA`, and `mmMC_SEQ_SUP_PGM`, wait for training bits in `mmMC_SEQ_TRAIN_WAKEUP_CNTL`, discover VRAM placement from `mmMC_VM_FB_LOCATION`, program system and AGP apertures, configure VM L1/L2 controls and contexts, invalidate TLBs through `mmVM_INVALIDATE_REQUEST`, and enable or decode VM fault interrupts through `mmVM_CONTEXT*_CNTL` and fault-status registers.

Other users are table-driven. `amdgpu/si.c` includes GMC 6.0 addresses in ASIC golden-register arrays, while clock-gating and power paths iterate over arrays such as `mmMC_HUB_MISC_HUB_CG`, `mmMC_XPB_CLK_GAT`, `mmATC_MISC_CG`, and `mmVM_L2_CG`.

## State, Persistence, And Dependencies
The header itself is stateless and persistent only as compile-time constants. The state it names is hardware state: memory-controller registers, VM page-table bases, fault latches, firmware/training sequencer registers, arbitration credits, performance counters, clock-gating controls, and PHY/PLL tuning state.

Changes made through these addresses persist in the GPU until reset, suspend/resume reprogramming, power-gating save/restore, or driver teardown. Several registers are part of boot and resume paths, so stale or incorrect values can survive long enough to affect framebuffer aperture visibility, GART translations, MC training, or memory-client access.

Dependencies are mostly implicit:
- The source must be compiled in an AMDGPU register environment that defines the `RREG32`/`WREG32` accessors and register-field helpers.
- Bit-level interpretation depends on `gmc_6_0_sh_mask.h`.
- Device selection matters. These offsets are valid for GMC 6.0 / SI-era ASIC paths; later headers such as `gmc_7_0_d.h`, `gmc_7_1_d.h`, `gmc_8_1_d.h`, and SOC15 `*_offset.h` files may reuse names with different packaging or base-index rules.

## Integration Points
Direct includes in this tree are `amdgpu/gmc_v6_0.c`, `amdgpu/gfx_v6_0.c`, `amdgpu/si.c`, `amdgpu/dce_v6_0.c`, `pm/legacy-dpm/si_dpm.c`, and `display/dc/resource/dce60/dce60_resource.c`. The display resource file includes it conditionally as a compatibility source for GMC registers such as `mmMC_HUB_RDREQ_DMIF_LIMIT`.

The most important integration is the GMC v6 IP block. It uses this address map for MC firmware upload, VRAM/GART layout, VM context programming for VMIDs 0-15, VM fault control, TLB invalidation emission on rings, PRT aperture programming, VRAM width discovery from MC channel registers, and memory-controller clock/light-sleep gating.

Power-management and golden-register integration is also significant. Golden arrays in SI setup use these symbolic offsets to apply chip-specific masks and values, while DPM/hwmgr code writes memory sequencer debug indices and data to tune or inspect MC/PHY state.

## Risks
The primary risk is silent hardware misprogramming. A wrong constant can target a valid but unrelated register, causing memory corruption, VM faults, bad aperture setup, failed memory training, unstable power management, or hangs without compiler errors.

Name reuse across ASIC generations is another risk. Many `mmVM_*`, `mmMC_VM_*`, and `mmATC_*` names appear in later GMC, GC, MMHUB, and ATHUB headers with different offset schemes. Including the wrong generation header, or mixing old direct-MMIO macros with newer SOC15 accessors, can produce plausible builds that access the wrong block.

Indirect `ixMC_IO_DEBUG_*` constants are especially sensitive because firmware tables and driver loops write an index register followed by data. An off-by-one index or D0/D1 lane mixup can corrupt memory PHY training state rather than simply fail a read.

The file intentionally lacks type checking. All constants are integer macros, so callers can pass an indirect `ix...` value to a direct `mm...` accessor, or use a direct register offset as an indirect table index, unless review or runtime testing catches it.

## Test Signals
Useful build-time signals are successful compilation of SI-era AMDGPU, display, and legacy PM files with both `gmc_6_0_d.h` and `gmc_6_0_sh_mask.h` included, plus absence of macro redefinition conflicts when display compatibility includes are active.

Runtime signals include successful MC firmware load and memory training, correct VRAM size and aperture placement, enabled PCIE GART with valid table address logging, clean TLB invalidation behavior, absence of unexpected VM fault interrupts, stable suspend/resume or power-gating transitions, and working display scanout under DCE 6.0.

Diagnostic signals are meaningful reads from fault registers such as `mmVM_CONTEXT*_PROTECTION_FAULT_STATUS`, expected clock-gating register transitions, stable MC performance counter reads, and no hangs when golden-register arrays touch GMC addresses during ASIC initialization.
