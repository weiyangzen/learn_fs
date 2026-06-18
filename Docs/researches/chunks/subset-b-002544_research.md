# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 1-2547

## Purpose

This chunk is generated AMD GC 11.5.0 register offset metadata. It contains no executable driver logic; it publishes preprocessor constants that name memory-mapped hardware registers and the SOC15 base-index bank used to access them. Consumers combine these `reg*` offsets with `*_BASE_IDX` constants, the companion `gc_11_5_0_sh_mask.h` field masks, and AMDGPU MMIO helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and their offset variants.

The selected range covers the header guard and the first 2,387 `#define` entries. It starts with SDMA0 engine and queue registers, then moves through early graphics-command/status blocks, color/depth/cache arbitration blocks, RMI and UTC/VM blocks, and ends inside the VM L2 performance-counter configuration block. Although this source tree is under `sources/distributed-fs/ceph-client`, this file is AMD GPU driver hardware metadata, not Ceph or filesystem code.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, locks, allocations, callbacks, or control structures in this chunk. The exported API is a generated macro namespace:

- `reg<REGISTER>` gives the register offset within the relevant GC address block.
- `reg<REGISTER>_BASE_IDX` gives the SOC15 register-space base index, usually `0` for the main GC block and `1` for a secondary MMIO aperture used by some hypervisor, power, and perf blocks.
- Address-block comments group the offsets by hardware decode block and record the underlying base address for the generated database.

Major address blocks in this chunk:

- `gc_sdma0_sdma0dec` at base `0x4980`: the largest section in the chunk. It defines SDMA0 global control/status registers, timestamp, power, chicken bits, address configuration, UTCL1/XNACK status, queue reset, error logs, scratch RAM, and eight SDMA queue register groups. Each queue group follows a repeated layout for ring-buffer control/base/read/write pointers, indirect-buffer control/base/size/offset, skip/context/doorbell state, CSA addresses, scheduling, preemption, polling addresses, AQL control, minor pointer update, RB preempt, and mid-command save/restore registers.
- `gc_sdma0_sdma0hypdec`, `gc_sdma0_sdma0perfsdec`, `gc_sdma0_sdma0perfddec`, and `gc_sdma0_sdma0pwrdec`: SDMA0 hypervisor/virtualization, microcode load, VM context, active function, virtual reset, perf-counter selection/data, and SDMA clock/power-control offsets.
- Early graphics blocks: `gc_grbmdec`, `gc_cpdec`, `gc_padec`, `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and `gc_rbdec`. These expose GRBM status/reset/scratch/trap/error registers; CP/CPC/CPF/CPG debug and busy/stall status; primitive assembler and shader queue debug/status windows; shader front-end control/status; texture pipe debug/status; GDS control/status; and render-backend/color/depth-related control and status.
- GCEA and RMI blocks: `gc_gceadec`, `gc_gceadec2`, `gc_gceadec3`, and `gc_rmi_rmidec` define graphics client/external arbitration maps, read/write priority and urgency controls, SDP arbitration/credits/reserves, latency/EDC/debug controls, and RMI crossbar/UTCL1/scoreboard/clock/status registers.
- VM and translation blocks: `gc_pmmdec`, `gc_utcl1dec`, `gc_gcvmsharedpfdec`, `gc_gcvml2pfdec`, `gc_gcatcl2dec`, `gc_gcl2tlbpfdec`, `gc_gcvmsharedvcdec`, and `gc_gcvml2vcdec`. These include system aperture, AGP, FB, local FB, default-page, virtual reset, active function, L1 TLB, VM L2 control/status, protection-fault, dummy-fault, invalidate, context, page-table, identity aperture, bank-select, walker throttle, cache-dump, credit-safety, ATC L2, L2 TLB, translation-assist, and per-context fragment-size registers.
- VM perf blocks at the chunk tail: `gc_gcvml2perfddec`, `gc_gcvml2prdec`, `gc_gcatcl2perfddec`, `gc_gcatcl2pfcntrdec`, `gc_gcl2tlbprdec`, `gc_gcvml2perfsdec`, and the beginning of `gc_gcvml2pldec`. These define low/high VM L2, UTCL2, ATC L2, and L2 TLB performance-counter data registers plus select/mode/config registers. Line 2547 stops at `regGCUTCL2_PERFCOUNTER3_CFG`, so the full `gc_gcvml2pldec` group continues in the next chunk.

Important naming patterns:

- `*_LO` and `*_HI` registers are 32-bit halves of 64-bit addresses, counters, or status values.
- `QUEUE<N>_*` macros identify repeated SDMA queue register windows. Driver code can compute per-queue offsets using the distance between queue 0 and queue 1 register names.
- `CONTEXT<N>_*` macros identify repeated VM context register windows for VMID/context programming.
- `INVALIDATE_ENG<N>_*` macros identify repeated VM invalidation engines with semaphore, request, acknowledge, and address-range registers.
- `PERFCOUNTER*_SELECT`, `*_SELECT1`, `*_MODE`, `*_CFG`, and `*_LO`/`*_HI` distinguish perf event selection, mode/config, and readback registers.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU and AMDKFD consumers:

1. Driver code selects GC 11.5.0 support based on the discovered graphics IP version.
2. The relevant module includes `gc/gc_11_5_0_offset.h` and `gc/gc_11_5_0_sh_mask.h`.
3. Code computes an MMIO address from a `reg*` offset and base index using SOC15 helper macros.
4. Field values are composed or decoded with the matching shift/mask macros from `gc_11_5_0_sh_mask.h`.
5. MMIO reads and writes program hardware state or poll status while higher-level driver logic handles ordering, locking, reset, power state, firmware, and virtualization policy.

`gfxhub_v11_5_0.c` is the direct include user in this repository. It uses the VM-related offsets from this chunk to program GART and system apertures, page-table base/start/end registers, VM context controls, L1 TLB and L2 cache controls, protection-fault defaults and status, invalidation request/ack/semaphore registers, and per-context/per-engine register spacing. SDMA offsets in this generated namespace are used by related SDMA, KFD, MES, and GFX paths for GC 11-era hardware, often through shared `regSDMA0_*` names and per-instance offset helpers.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware state that lives in GPU registers.

The represented hardware state includes:

- SDMA0 queue state: ring-buffer base addresses, read/write pointers, indirect-buffer pointers, doorbell offsets/logs, context status, preemption state, AQL control, polling addresses, CSA addresses, and mid-command save/restore data.
- SDMA0 global state: microcode version and load address/data windows, power/control bits, timestamp, address swizzle/tiling configuration, UTCL1 status and invalidation/XNACK state, error/status logs, scratch RAM, interrupt status, and performance-counter registers.
- Graphics front-end and command state: GRBM status/reset/trap/error/scratch, CP/CPC/CPF/CPG debug and stall status, PA/SQ/SPI/texture/GDS/render-backend controls, and cache/color/depth hardware controls.
- Memory-system and VM state: FB/AGP/system aperture limits, default-page address, VM L1/L2 TLB/cache controls, protection-fault status and default addresses, context enable/control registers, per-context page-table base/start/end registers, invalidation sem/req/ack/range registers, identity apertures, ATC L2/L2TLB controls, RMI/UTC status, and credit-safety registers.
- Profiling state: VM L2, UTCL2, ATC L2, and L2TLB performance-counter select/config/mode registers and low/high result registers.

Persistence is hardware-defined. Some registers retain values until a GPU reset, suspend/resume, power-gating transition, function-level reset, or explicit reprogramming. Others are live status, write-one-to-clear, write-only command, self-clearing strobe, indirect data, or hardware-owned counter registers. This offset header does not encode access type, reset value, side effects, reserved-bit policy, or ordering requirements.

## Dependencies And Integration Points

Directly paired files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h` supplies the register field shifts and masks for these offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` directly includes this header and uses the VM and GCMC/GCVM register offsets from this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/navi10_enum.h` is included by the direct GFXHUB user for enum-style field values used with the masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_common.h` and AMDGPU register helpers provide the MMIO access layer.

Functional integration points:

- GFXHUB initialization and teardown: page-table base programming, GART aperture setup, system aperture setup, L1 TLB control, L2 cache control, system-domain enablement, identity aperture setup, and fault handling.
- VM invalidation: the repeated `regGCVM_INVALIDATE_ENG*` offsets allow the VM hub code to issue per-VMID invalidations, program optional address ranges, and poll acknowledgements.
- GPU fault reporting: `regGCVM_L2_PROTECTION_FAULT_STATUS`, address, default-address, and control registers provide the hardware state decoded for VM fault logs.
- SDMA queue setup and recovery: SDMA queue ring, pointer, doorbell, polling, preemption, and context-status offsets are used by SDMA/KFD/MES style paths to create queues, restore queue state, reset queues, and diagnose hangs.
- Power, reset, and clock-gating: GRBM status/reset and SDMA/GCVM/GCEA/ATC/RMI clock/power-related offsets are consumed by graphics initialization, reset recovery, runtime power management, and firmware setup.
- Profiling and diagnostics: perf-counter select/config/data offsets expose VM and SDMA performance-monitor registers, while debug/status registers support low-level diagnostics and validation.

## Risks And Edge Cases

- Offset/header mismatch is the central risk. Pairing `gc_11_5_0_offset.h` with the wrong shift/mask header or an incompatible GC IP version can compile successfully while reading or writing the wrong register.
- The macros are untyped constants. A caller can accidentally use a register from the wrong block, base index, queue, VM context, or invalidation engine without compiler help.
- Repeated register windows rely on exact spacing. Code such as GFXHUB context setup and SDMA queue setup computes distances between queue/context/engine registers; a generated offset change or wrong base register breaks every derived address.
- SDMA queue registers are stateful and ordering-sensitive. Ring base, read/write pointers, doorbells, polling addresses, AQL control, preemption, and mid-command state must be programmed in the sequence expected by the SDMA engine and firmware.
- VM registers are high impact. Wrong page-table base, aperture, context-control, or invalidation programming can cause GPU page faults, stale translations, memory corruption, hangs, or broken SR-IOV isolation.
- Many `LO`/`HI` pairs represent 64-bit values. Consumers need stable read/write ordering and correct shifts; mixing `>> 12`, `>> 24`, `>> 44`, or raw lower/upper 32-bit programming is context-specific.
- Some registers are PF-only, VF-visible, hypervisor, or PSP/firmware-owned. The header does not encode access privilege, so SR-IOV and secure/firmware mediated paths must decide whether a write is legal.
- Register side effects are not visible in the offset list. Invalidation requests, reset requests, queue reset, counter result controls, fault clears, and indirect data windows may be strobes or command registers, not durable configuration.
- Perf counters can return misleading results if the select/mode/config registers are programmed while clocks are gated, blocks are idle, wrong clients/contexts are selected, or low/high halves are sampled inconsistently.
- The chunk boundary is artificial. The `gc_gcvml2pldec` perf-counter configuration block is only partially present here, so downstream research must merge adjacent chunks before treating the per-file coverage as complete.

## Test Signals

Useful validation signals are mostly build, static generated-header checks, and hardware smoke tests:

- Build AMDGPU with GC 11.5.0 support enabled and ensure `gfxhub_v11_5_0.c` compiles against both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
- Static generated-header checks that every `reg*` macro has a matching `reg*_BASE_IDX`, that register names used by `gfxhub_v11_5_0.c` exist in this offset header, and that corresponding field macros exist in `gc_11_5_0_sh_mask.h`.
- VM initialization tests on GC 11.5.0-class hardware: GART aperture setup, system aperture setup, VM context enablement, page-table base programming, and successful command submission using VMID-backed mappings.
- VM invalidation tests that issue per-VMID invalidations, poll `GCVM_INVALIDATE_ENG*_ACK`, and verify stale translations are not observed after page-table updates.
- Fault-path tests that intentionally trigger invalid GPU virtual addresses and verify `GCVM_L2_PROTECTION_FAULT_STATUS` plus fault address/default-page handling are decoded and cleared correctly.
- SDMA queue smoke tests that initialize queues, update doorbells and write pointers, submit copy/fill work, exercise preemption or reset where supported, and verify status/idle registers after completion.
- Suspend/resume, GPU reset, runtime power-management, and SR-IOV VF/PF tests because many offsets in this chunk touch state that is lost, privileged, firmware-owned, or reinitialized across power and function transitions.
- Perf-counter smoke tests for SDMA, VM L2, UTCL2, ATC L2, and L2TLB counters: configure select/mode registers, run known memory or copy workloads, read low/high counter pairs, and verify values are plausible and not stuck at zero or saturated.
