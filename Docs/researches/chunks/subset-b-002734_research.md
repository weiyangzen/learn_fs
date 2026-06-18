# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_sh_mask.h lines 1-5205

## Scope

This chunk is the first 5,205 lines of the generated AMD GMC 7.1 shift/mask register header. It contains preprocessor constants only: hardware register fields are exposed as `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` macros so C code can pack, update, and decode 32-bit MMIO values.

The requested range covers the license and include guard plus 5,180 `#define` lines across roughly 458 register groups. Within this chunk there are 2,590 mask constants and 2,589 shift constants; the mismatch is intentional at the artificial chunk boundary, because line 5205 ends on `MC_MCBVM_PERFCOUNTER3_CFG__PERF_SEL_END_MASK` and its matching shift is in a later line outside this work item.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata for the CIK/GMC 7.x memory-controller generation. It does not implement Ceph or filesystem behavior.

## Purpose

`gmc_7_1_sh_mask.h` describes the bit layout of GMC 7.1 memory-controller, graphics memory hub, virtual-memory, crossbar, peer-to-peer, and performance-counter registers. Driver code pairs these constants with register offsets from the companion GMC offset headers and then uses AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32`.

This chunk covers these major hardware surfaces:

- MC arbiter configuration, aging, refresh, DRAM timing, list management, write/read arbitration, return credits, error correction, replay, address swizzle/hash, power management, and busy/status reporting.
- CITF client-interface controls for graphics/local/hub clients, credits, DAGB delay, group routing, watermark decrements, local read/write client knobs, performance monitor state, and CITF clock-gating controls.
- MC hub read-request, write-data-path, write-return, credit, bypass, shared delay, idle/status, blackout, and clock-gating controls for GPU clients including GFX, RLC, SDMA, display/DMIF, UVD, VCE, ACP, CP, XDMA, ISP, HDP, SMU, VMC, IA, CPG/CPF/CPC, and memory-channel blocks.
- MC RPB, shared channel mapping/remapping, read/write group maps, memory aperture registers, L1 TLB debug/status registers, and MCD/MCD clock-gating configuration.
- MC XPB routing, destination mapping, cross-link gateway configuration, loopback/address matching, unclean thresholding, write-combine buffer status/configuration, P2P BAR and peer system BAR registers, XPB interface/status/sub-control, sticky bits, and XPB clock gating.
- MC XBAR address-decode, remote, credit, channel remap, two-channel, arbitration, burst, and performance-monitor registers.
- Low/high performance counter value registers and the beginning of per-block performance-counter configuration registers for CITF, HUB, RPB, ARB, MCBVM, and related blocks.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, locks, allocations, callbacks, or direct MMIO operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit.
- Consumer code normally writes `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` or `REG_GET_FIELD(value, REGISTER, FIELD)`, which depends on these exact macro names.
- Matching register address names are in GMC offset headers such as `gmc_7_1_d.h`/related generated register files included by the same CIK-era sources.

Important register groups in this chunk include:

- `MC_CONFIG`, `MC_CONFIG_MCD`, `MC_CG_CONFIG`, and `MC_CG_CONFIG_MCD`: enable reads/writes for memory-controller channels/MCDs and indexed access modes.
- `MC_ARB_*`: arbiter aging, ECC/GECC2 status and injection/debug, address swizzle/hash, DRAM timing, refresh, power-management override, group decode, list management, replay, return credits, max-latency capture, busy status, and clock gating.
- `MC_CITF_*`, `MC_RD_*`, and `MC_WR_*`: client-interface credit allocation, read/write grouping, local/hub/TC/CB/DB client throttling, watermark decrement, performance monitor, and CITF clock-gating fields.
- `MC_HUB_MISC_*`, `MC_HUB_RDREQ_*`, `MC_HUB_WDP_*`, and `MC_HUB_WRRET_*`: hub idle/status bits, read-request and write-data path queue controls, per-client enable/prescale/blackout/stall/burst/lazy-timer knobs, MCD channel credit counts, bypass controls, and per-client availability/status reporting.
- `MC_RPB_*`: request path buffer configuration, ordering, switch counts, write-combine behavior, CID queue programming, TCI controls, and RPB performance counter control/status.
- `MC_VM_*`: frame-buffer and AGP apertures, system aperture bounds/default address, display-controller write hit regions, L1 TLB controls/debug/status, VM steering, and memory-channel/MCD VM-related debug.
- `MC_XPB_*`: cross-partition/bus routing apertures, destination maps, CLG configuration, P2P BAR setup, peer system BARs, interface credits/status, subblock stall/reset controls, sticky bits, and clock gating.
- `MC_XBAR_*`: memory crossbar address decode, remote routing, per-output credits, channel remapping, arbitration, max burst, and XBAR performance monitoring.
- `*_PERFCOUNTER_LO`, `*_PERFCOUNTER_HI`, and `*_PERFCOUNTER*_CFG`: split counter values, compare values, select ranges, mode, enable, and clear bits for CITF, HUB, RPB, MCBVM, MCDVM, VM L2, ARB, and ATC performance fabrics.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is:

1. A CIK/GMC7 driver source includes `gmc/gmc_7_1_sh_mask.h` and the corresponding register address header.
2. The driver reads a hardware register through `RREG32`, `RREG32_PCIE`, or a CGS/powerplay wrapper, or starts from a zero/full-register value.
3. It uses `REG_SET_FIELD`, `REG_GET_FIELD`, raw mask tests, or mask arrays to update or decode a specific field.
4. It writes the resulting value with `WREG32`/wrapper helpers, or uses the decoded field for topology, memory size, VM, display, power, or debug decisions.

Concrete integration patterns in this tree include:

- `amdgpu/gmc_v7_0.c` reads `mmMC_VM_FB_LOCATION` to derive VRAM placement, programs system/AGP apertures, uses `MC_SHARED_CHMAP__NOOFCHAN` to infer memory channels, configures `MC_VM_MX_L1_TLB_CNTL`, and toggles clock/memory light-sleep bits in `MC_HUB_MISC_*`, `MC_XPB_CLK_GAT`, and `MC_CITF_MISC_*`.
- `amdgpu/gmc_v7_0.c` uses `MC_SHARED_BLACKOUT_CNTL__BLACKOUT_MODE` around blackout/FBI enable sequencing, showing that some fields in this header participate in ordered reset/display/memory-controller transitions.
- `display/dc/resource/dce80/dce80_resource.c` maps `mmMC_HUB_RDREQ_DMIF_LIMIT` plus `MC_HUB_RDREQ_DMIF_LIMIT__ENABLE_{MASK,SHIFT}` into display resource register tables.
- `pm/powerplay/hwmgr/smu7_hwmgr.c` reads and writes `mmMC_CG_CONFIG`, connecting this mask family to power-management clock-gating policy.

The header itself does not encode required waits, polling loops, write-one-to-clear behavior, ordering around reset, whether a field is read-only, or whether a write triggers hardware action. Those semantics are in consuming code and the hardware specification.

## State And Persistence Behavior

The macros hold no software state. They describe hardware state that lives in GMC 7.1 registers.

Hardware state represented by this chunk includes:

- Persistent configuration until reset or reprogramming: channel enables, memory-channel routing/remapping, DRAM timing, arbiter policy, credit depths, queue burst/lazy timers, blackout behavior, VM apertures, L1 TLB controls, P2P BARs, crossbar routing, and clock-gating/light-sleep enables.
- Live status: arbiter and hub busy bits, outstanding client read/write bits, MCD availability, RPB/XPB pipe and buffer status, write deadlock/read deadlock warnings, TLB busy bits, sticky XPB status, and performance counter values.
- Fault and reliability state: GECC/ECC corrected/uncorrected/FED status and clear fields, replay and poison controls, debug injection fields, VM-related protection/fault support registers, and write-one-to-clear-style sticky status surfaces such as `MC_XPB_STICKY_W1C`.
- Profiling state: selected performance events, counter mode, enable/clear bits, compare values, and low/high counter values across MC subblocks.

Persistence is hardware-defined. Some registers are initialized during ASIC bring-up, resume, BACO/power transitions, or display setup and then left programmed. Others are transient status/counters or write-trigger controls. The generated macros do not distinguish safe observation from side-effecting writes.

## Dependencies And Integration Points

This chunk depends on the AMDGPU generated register ecosystem:

- Companion GMC 7.1 address/offset headers provide `mm*` register addresses such as `mmMC_VM_FB_LOCATION`, `mmMC_SHARED_CHMAP`, `mmMC_HUB_RDREQ_DMIF_LIMIT`, `mmMC_CG_CONFIG`, and `mmMC_XPB_CLK_GAT`.
- AMDGPU field helpers require the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names emitted here.
- CIK-era consumers include `amdgpu/gmc_v7_0.c`, `amdgpu/cik.c`, `amdgpu/cik_sdma.c`, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/dce_v8_0.c`, `pm/powerplay/hwmgr/ci_baco.c`, `pm/powerplay/smumgr/ci_smumgr.c`, and `display/dc/resource/dce80/dce80_resource.c`.
- Closely related generated headers such as `gmc_7_0_sh_mask.h` and `gmc_8_2_sh_mask.h` share many names but not all bit layouts. Consumers must include the header matching the active ASIC generation.

Functionally, this header is integrated into memory-controller setup, VRAM aperture discovery, GPUVM/TLB programming, display read-request limiting, power/clock gating, memory-channel topology detection, reset/blackout sequencing, peer-to-peer routing, and diagnostics/performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but causes the driver to program or decode the wrong hardware bits.
- The chunk boundary is artificial and ends mid-register group. `MC_MCBVM_PERFCOUNTER3_CFG__PERF_SEL_END_MASK` is present, while its matching `__SHIFT` and the rest of `MC_MCBVM_PERFCOUNTER3_CFG` are outside this chunk. The final merged file research must reconcile that continuation.
- Many register families are highly repetitive across channels, groups, clients, MCDW/MCDX/MCDY/MCDZ/MCDS/MCDT/MCDU/MCDV, and counter indices. Copy or generation errors can affect only one client/channel and be difficult to diagnose.
- Cross-generation similarity is dangerous. GMC 7.0 and 7.1 definitions are close, but line searches show differences such as additional MCDS/MCDT/MCDU/MCDV fields and shifted `MC_HUB_RDREQ_CNTL` bit positions in GMC 7.1.
- VM aperture and TLB fields are isolation-critical. Bad masks for `MC_VM_FB_LOCATION`, system aperture, AGP aperture, L1 TLB controls, or VM steering can corrupt address translation, mis-size VRAM, or route accesses outside intended memory ranges.
- Clock-gating and light-sleep fields under `MC_HUB_MISC_*`, `MC_CITF_MISC_*`, `MC_XPB_CLK_GAT`, and `MC_CG_CONFIG*` can create hangs, wakeup failures, or power regressions if toggled with incorrect masks or without required sequencing.
- Blackout, reset, stall, and self-init controls can disturb live display, hub, XPB, RPB, and memory-controller traffic. These should be changed only in the ordered paths that own those transitions.
- ECC/GECC/replay/debug-injection fields may be sticky, W1C, diagnostic-only, or fault-injection surfaces. Treating them as ordinary configuration can clear evidence or inject hardware errors.
- Low/high performance counters can race hardware updates. This header gives masks, but not a coherent sampling method.
- Reserved/debug fields such as `DEBUG_RSV`, `RSVD*`, `TBD_FIELD`, and generic `FIELDNAME*` should generally be preserved during read-modify-write unless authoritative init tables specify full register values.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU CIK/GMC7 paths that include this header, especially `gmc_v7_0.c`, `cik.c`, `cik_sdma.c`, `amdgpu_amdkfd_gfx_v7.c`, `sdma_v2_4.c`, `dce_v8_0.c`, `ci_baco.c`, `ci_smumgr.c`, and `dce80_resource.c`.
- Mechanically compare this range against AMD's authoritative GMC 7.1 register database. Every complete field in the range should have aligned mask/shift pairs, and the known line-5205 boundary should be completed by the next chunk.
- Cross-check against companion offset/address headers so every register group used with `REG_SET_FIELD`/`REG_GET_FIELD` has matching `mm*` addresses for GMC 7.1.
- Run static mask sanity checks: masks should align with shifts, repeated client/channel groups should have expected structural symmetry, full-width fields should use full masks, and reserved fields should not overlap named fields.
- Boot and initialize CIK/GMC7 hardware, verifying VRAM size/aperture discovery, memory-channel count detection, MC blackout transitions, VM/TLB enablement, and display initialization complete without register access warnings.
- Exercise suspend/resume, BACO/power transitions, clock-gating toggles, and display on/off paths. Relevant regressions include hangs on wake, memory-controller busy bits stuck, display underflow, or incorrect `MC_HUB_MISC_IDLE_STATUS`.
- Run GPUVM and GART tests that program system/AGP/framebuffer apertures, enable L1/L2 translation, invalidate TLBs, and validate fault reporting.
- Run SDMA, graphics, display, UVD/VCE, and KFD workloads concurrently to stress hub/CITF credits, read/write groups, MCD availability, and arbitration fairness.
- Validate performance counters by programming covered `*_PERFCOUNTER*_CFG` registers, reading low/high counter pairs, and checking that controlled memory/display/SDMA/GFX traffic moves the expected counters.
- Run ECC/RAS/debug tests only where supported by hardware and platform policy, confirming GECC status/clear/replay/debug masks decode observed faults correctly.

## Cross-Chunk Notes

This chunk starts at the top of `gmc_7_1_sh_mask.h` and covers the first part of the generated GMC 7.1 mask namespace through the beginning of `MC_MCBVM_PERFCOUNTER3_CFG`. Later chunks are required for the remainder of that performance-counter group and the rest of the 14,416-line header. The final per-file research should merge this chunk with later chunks before making file-wide claims about the complete GMC 7.1 register field set.
