# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h lines 1-2943

## Purpose

This chunk is a generated AMD Graphics Core 10.1.0 default-value header slice. It contains compile-time preprocessor constants for reset/default values of GC, SDMA, GFXHUB/GCVM, command processor, shader, render backend, cache, and graphics pipeline registers. It has no executable C logic; its public surface is `#define mm<REGISTER>_DEFAULT 0x...` macros that companion AMDGPU driver code can use as hardware baseline values while programming registers.

The requested range covers the file prologue and the first 2,943 lines of a larger 6,028-line header. Within this range there are 2,826 `#define` entries across 32 address blocks. The chunk starts at `gc_sdma0_sdma0dec`, covers the full `gc_sdma0_sdma0dec` and `gc_sdma1_sdma1dec` default tables, then moves through GRBM, CP, PA, SQ, SPI/SH, texture, GDS, RB, GCEA, RMI, PMM, UTCL1, GCVM L2/context/shared VM, TC/TCP, shader programming, CP/HQD, DIDT/CAC, GDS partitioning, and ends partway through `gc_gfxdec0` after early DB/PA/CB graphics-context defaults. Later portions of `gc_10_1_0_default.h` are intentionally outside this chunk.

Although this repository path is under a local `ceph-client` source mirror, the file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this chunk. The exported interface is a generated macro convention:

- `mm<REGISTER>_DEFAULT`: the reset/default 32-bit value for a GC 10.1.0 register.
- Address-block comments such as `// addressBlock: gc_gcvml2vcdec`: generator metadata that groups defaults by hardware decode block.

The major macro families in this chunk are:

- `SDMA0` and `SDMA1`: public SDMA engine defaults, including power/clock control, global address config, status registers, UTCL1 controls, EDC, atomic preop, performance counters, interrupt/IOV logging, and per-context ring/IB/doorbell defaults for `GFX`, `PAGE`, and `RLC0` through `RLC7`. Most base pointers, read/write pointers, CSA addresses, mid-command data, and status values default to zero, while ring controls default to values such as `0x80840000`, IB controls to `0x00000100`, write-pointer polling control to `0x00401000`, and dummy registers to `0x0000000f`.
- `GRBM`, `CP`, `CPP`, `CPPHQD`, and `SPIP`: graphics register bus manager, command processor, command queue, HQD/MQD, doorbell, context, priority, interrupt, preemption, DDID, DMA watch, UTCL1, and queue state defaults. These include reset baselines for ring base/control/pointers, VMID assignment, queue priority, MQD/HQD state, and command processor counters.
- `PA`, `RB`, `GFXDEC0`, `SQ`, `SHS`, and `SH`: graphics pipeline, shader, and render state defaults. They cover vertex/geometry pipeline FIFOs, primitive and shader-array config, pixel/geometry/hull/local shader program/user-data defaults, compute dispatch registers, depth/color buffer defaults, scissor/window/clip rectangles, and many performance/status/watch registers.
- `GDS` and `GDSP`: global data share defaults, VMID partition base/size values, GWS/OA allocation defaults, reset masks, max wave IDs, and context-switch counters.
- `GCEA`, `RMI`, `TC`, `TCP`, `UTCL1`, and `GCATCL2/GCVML2`: memory fabric, request arbitration, cache/TLB, address decode, and virtual memory defaults. These include DRAM/IO client-to-group mappings, priority/quantum tables, cache controls, page table walker/protection-fault defaults, invalidate engine defaults, and per-VMID page-table base/start/end defaults.
- `GCMC_VM_*` and `GCVM_*`: GFXHUB/GCVM shared and L2 virtual memory defaults used by the VM hub setup path. Notable defaults in this range include `mmGCVM_L2_CNTL3_DEFAULT`, `mmGCVM_L2_CNTL4_DEFAULT`, `mmGCVM_L2_CNTL5_DEFAULT`, `mmGCVM_CONTEXT0_CNTL_DEFAULT` through `mmGCVM_CONTEXT15_CNTL_DEFAULT`, invalidate engine request defaults, protection fault defaults, and GCMC aperture/TLB defaults.
- `DIDT`, `GC_CAC`, `PCC`, `EDC`, and `PWRBRK`: throttling, activity/power estimation, dynamic IDT, error detection, and related performance counters.

The address-block distribution in the mapped range is: `gc_sdma0_sdma0dec` 495 defines, `gc_sdma1_sdma1dec` 491, `gc_grbmdec` 43, `gc_cpdec` 72, `gc_padec` 74, `gc_sqdec` 74, `gc_shsdec` 74, `gc_tpdec` 12, `gc_gdsdec` 13, `gc_rbdec` 98, `gc_gceadec2` 23, `gc_spipdec2` 3, `gc_gceadec3` 11, `gc_rmi_rmidec` 30, `gc_pmmdec` 7, `gc_utcl1dec` 4, `gc_gcatcl2dec` 12, `gc_gcvml2pfdec` 35, `gc_gcvml2vcdec` 203, `gc_gcvmsharedpfdec` 20, `gc_gcvmsharedvcdec` 8, `gc_gceadec` 129, `gc_tcdec` 9, `gc_shdec` 326, `gc_cppdec` 239, `gc_spipdec` 50, `gc_cpphqddec` 72, `gc_didtdec` 3, `gc_gccacdec` 24, `gc_tcpdec` 19, `gc_gdspdec` 91, and the opening 61 defines of `gc_gfxdec0`.

## Control Flow

This header has no runtime control flow. It participates in compile-time selection of constants for runtime register programming:

1. AMDGPU code includes `gc/gc_10_1_0_offset.h`, `gc/gc_10_1_0_sh_mask.h`, and this `gc/gc_10_1_0_default.h` together so register addresses, bit fields, and reset/default values stay aligned for the same ASIC generation.
2. Driver code reads current register values with SOC15 register helpers, token-pastes field names through mask/shift helpers, starts selected programming sequences from default constants when appropriate, and writes back updated values.
3. The direct source-tree consumer found for this generated default header is `drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`. Its GFXHUB setup path uses defaults from this chunk for VM L2 control registers: `mmGCVM_L2_CNTL3_DEFAULT`, `mmGCVM_L2_CNTL4_DEFAULT`, and `mmGCVM_L2_CNTL5_DEFAULT`.
4. Actual sequencing for SDMA engine setup, ring and MQD/HQD initialization, graphics pipeline programming, GDS partitioning, shader program/user-data setup, cache/TLB enablement, VM invalidation, fault handling, power/throttle controls, and register restoration is implemented by AMDGPU runtime code and hardware microcontrollers outside this generated header.

For the most visible integration path, `gfxhub_v2_0_gart_enable()` initializes the GART aperture, system aperture, TLB, and VM L2 cache, enables context 0, configures VMID contexts, and programs invalidate engines. `gfxhub_v2_0_init_cache_regs()` reads live GCVM L2 registers, applies fields, and uses the generated `mmGCVM_L2_CNTL3_DEFAULT`, `mmGCVM_L2_CNTL4_DEFAULT`, and `mmGCVM_L2_CNTL5_DEFAULT` as the baseline before setting bank select, fragment size, and physical-request fields.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes hardware-visible default state:

- SDMA defaults describe idle/reset ring state: ring/IB bases and pointers are zero, doorbells are disabled/zeroed, CSA addresses are zero, status registers report reset-specific constants, and context slots use common reset control values until the driver initializes queues.
- GCVM/GCMC defaults describe VM contexts, page-table base/start/end registers, invalidate engines, protection-fault addresses/status/counters, L2 control registers, system aperture registers, AGP/FB aperture locations, identity aperture defaults, and TLB/cacheability state. Runtime code overwrites these during GART and VM hub setup.
- CP/HQD defaults describe command processor queues, ring buffers, doorbell ranges, VMID binding, interrupts, priority counters, preemption/suspend state, MQD/HQD base/control, AQL/EOP state, and watchpoint registers. These values are baselines, not the live queue state after KFD/graphics scheduling.
- Shader and graphics context defaults describe pipeline registers such as shader program addresses/resources, shader user data, compute dispatch dimensions, scratch, resource limits, scissor/clip/window rectangles, depth/color targets, and cache controls. They generally represent reset or context-initial defaults before command streams program draw/dispatch state.
- GCEA/RMI/TC/TCP/GDS/CAC defaults describe memory arbitration, cache, GDS partition, throttling, and status/counter baselines. Many counters and status registers default to zero, while fabric priority, credit, and mapping registers have nonzero hardware reset values.

Persistence is hardware-defined. These macro values are compile-time constants; the actual register contents persist until driver programming, context switch restore, firmware activity, power gating, suspend/resume, GPU reset, or ASIC reset changes them. Status, fault, invalidate, EDC, performance counter, and clear registers may be latched, sticky, clear-on-write, self-clearing, read-only, or only valid while a related clock or power domain is active. This header does not encode access type or side-effect semantics.

## Dependencies And Integration Points

This generated default header must stay synchronized with the GC 10.1.0 register database and companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies matching `mm<REGISTER>` addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h` supplies matching field shift/mask constants for the same registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c` directly includes this header and uses the GCVM/GCMC subset from this chunk while initializing GFXHUB VM, L2 cache, protection-fault behavior, and invalidation engines.
- Runtime register helper infrastructure in AMDGPU, such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`, consumes the offsets and masks that must match these defaults.
- SDMA, graphics, KFD queue-management, command processor, and power-management code may depend on equivalent register defaults indirectly through reset assumptions, saved/restored register tables, hardware init sequences, or generated-table consistency checks even when this exact header is not directly referenced in a local C file.

Behaviorally, this chunk sits below high-level DRM, GEM, VM, command submission, KFD, and graphics scheduling code. It provides hardware baselines used when bringing up Navi10/GC 10.1-era graphics and VM blocks, debugging register dumps, validating reset state, and avoiding magic constants in low-level register programming.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong value can compile cleanly while programming an invalid reset baseline or preserving the wrong reserved bits.
- The file is generated metadata. Manual edits risk divergence from AMD's register source, the matching offset/mask headers, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. This chunk begins at the file prologue but ends in the middle of `gc_gfxdec0`; the rest of `gc_gfxdec0` and later blocks are owned by later chunks.
- The SDMA0 and SDMA1 sections are highly repetitive. A generator or copy error in only one engine or one RLC context can break a single DMA queue path while other engines appear correct.
- Many defaults are safe only as reset baselines. Reapplying them blindly at runtime could clear live ring pointers, page-table pointers, doorbell state, shader program addresses, fault status, GDS allocations, queue context, performance counters, or graphics context state.
- GCVM/GCMC defaults are security and stability sensitive. Incorrect L2, TLB, context, aperture, protection-fault, or invalidate-engine defaults can cause VM faults, stale translations, data corruption, fault storms, invalid dummy-page behavior, or SR-IOV PF/VF programming mismatches.
- CP/HQD/MQD and doorbell defaults are scheduling sensitive. Bad defaults can leave queues unmapped, mapped to the wrong VMID, polling the wrong address, failing preemption/suspend, or corrupting read/write pointer handling.
- Graphics pipeline and shader defaults affect context state. Incorrect defaults can cause bad draw/dispatch behavior, wrong shader resource setup, invalid scissor/clip/depth/color state, hangs, or rendering corruption when used in context images or reset paths.
- Status, clear, fault, and counter registers may have side effects or volatile meanings. The default header does not distinguish writeable configuration registers from read-only status, write-one-to-clear, sticky fault, or self-clearing command registers.
- Some register defaults include reserved or undocumented bits. Driver code should prefer field helpers and hardware documentation rather than decomposing these values casually.

## Test Signals

Useful validation combines generated-header checks with AMDGPU runtime behavior:

- Build AMDGPU with GC 10.1/GFXHUB 2.0 support enabled. Missing or renamed macros from this chunk should fail in direct users such as `gfxhub_v2_0.c`.
- Mechanically compare every `mm*_DEFAULT` in this chunk against AMD's authoritative GC 10.1.0 register database and the companion `gc_10_1_0_offset.h`/`gc_10_1_0_sh_mask.h` headers.
- Diff replicated SDMA0/SDMA1 and RLC context groups where hardware expects parallel engines or queues to share the same reset shape, while allowing intentional differences such as engine-specific status/default registers.
- Boot on GC 10.1-era hardware and confirm GFXHUB GART enable succeeds, VM contexts are programmed, VM invalidations complete, and protection-fault reporting decodes correctly.
- Exercise graphics and compute command submission, SDMA copy/fill, KFD queues, preemption, suspend/resume, GPU reset, and SR-IOV paths. Watch for hangs, VM faults, stale translations, doorbell failures, or queue restore errors.
- Capture register dumps immediately after reset and after driver initialization. Defaults from this header should match reset baselines where hardware exposes them, while driver-owned registers should show expected programmed deviations.
- Run rendering, compute, and memory-stress tests that use VMID contexts, GDS, shader user data, cache/TLB invalidations, and SDMA engines. Failures in only one queue/engine or only after reset/resume are strong signals of bad generated defaults or mismatched companion headers.

## Cross-Chunk Notes

This is the first chunk for `gc_10_1_0_default.h`. It owns the file prologue and complete early default blocks through `gc_gdspdec`, then stops after the first 61 defaults in `gc_gfxdec0` at line 2943. The merge lane should combine this with later chunks before making whole-file claims about all GC 10.1.0 default blocks, especially the remainder of `gc_gfxdec0` and all later performance, RLC, power, hypervisor, and indirect-register sections.
