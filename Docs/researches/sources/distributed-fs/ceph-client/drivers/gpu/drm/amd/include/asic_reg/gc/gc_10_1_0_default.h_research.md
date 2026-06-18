# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002441`: lines 1-2943, `Docs/researches/chunks/subset-b-002441_research.md`
- `subset-b-002442`: lines 2944-5869, `Docs/researches/chunks/subset-b-002442_research.md`
- `subset-b-002443`: lines 5870-6028, `Docs/researches/chunks/subset-b-002443_research.md`

## Chunk Research

### subset-b-002441: lines 1-2943

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

### subset-b-002442: lines 2944-5869

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h lines 2944-5869

## Scope

This chunk covers lines 2944-5869 of `gc_10_1_0_default.h`, an AMDGPU ASIC register default header for the GC 10.1.0 graphics block. The file is a generated-style C header guarded by `_gc_10_1_0_DEFAULT_HEADER`; this chunk contains only `#define` constants and address-block comments, not executable code, types, or inline helpers.

Within the requested range there are 2,839 default-value macros. Most reset/default values are `0x00000000` (2,331 entries), with non-zero defaults concentrated in rasterization setup, command processor/MES setup, cache/interconnect arbitration, performance counter selectors, RLC power-management state, clock-gating controls, virtualization defaults, SDMA hypervisor context defaults, and indexed CAC/SPM/SQ debug registers.

## Purpose

The header provides compile-time symbolic reset/default constants for GC 10.1.0 registers. It complements the neighboring `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h` headers: offsets identify register addresses, masks/shifts identify fields, and this default header supplies default register values that driver code can use as a base before setting fields.

This chunk primarily covers:

- Graphics pipeline viewport/scissor, color-buffer, depth-buffer, shader input, VGT/GE draw-state, streamout, and rasterizer defaults.
- Command processor status, fence, counter, indirect-buffer, metadata, coherency, and MES microcontroller defaults.
- GUS, GL1/CH, and GL2 cache/interconnect defaults.
- Performance counter data and selection defaults across CP, SPI, SQ, TCP, GL1/GL2, CB, DB, RLC, RMI, UTCL1, GCR, PA_PH, GUS, GC ATC L2, and VM L2 blocks.
- RLC, RLCS, power, CGTS/CGTT clock-gating, hypervisor, SDMA hypervisor, GCVM shared hypervisor, CAC indexed, SPM indexed, and SQ wave debug defaults.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The public interface is the macro namespace itself:

- `mm..._DEFAULT` macros name memory-mapped register defaults, for example `mmPA_SC_MODE_CNTL_1_DEFAULT`, `mmGRBM_GFX_INDEX_DEFAULT`, `mmRLC_CNTL_DEFAULT`, and `mmSDMA0_VM_CTX_CNTL_DEFAULT`.
- `ix..._DEFAULT` macros name indexed register defaults, especially CAC and SPM indexed register defaults such as `ixGC_CAC_CNTL_DEFAULT`, `ixGC_CAC_WEIGHT_*_DEFAULT`, `ixSE_CAC_CNTL_DEFAULT`, `ixGLB_*_SAMPLEDELAY_DEFAULT`, `ixSE_*_SAMPLEDELAY_DEFAULT`, and `ixSQ_WAVE_*_DEFAULT`.
- Address-block comments partition the table into hardware decode regions. In this chunk the boundaries include `gc_gfxudec`, `gc_cprs64dec`, `gc_gusdec`, `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, `gc_perfddec`, several performance-counter control/data decode blocks, `gc_rlcdec`, `gc_rlcrdec`, `gc_rlcsdec`, `gc_pwrdec`, `gc_hypdec`, `gc_sdma0_sdma0hypdec`, `gc_sdma1_sdma1hypdec`, `gc_gcvmsharedhvdec`, `gccacind`, `secacind`, `spmglbind`, `spmind`, and `sqind`.

## Content And Control Flow

This chunk has no runtime control flow. C preprocessing exposes a flat table of constants. The driver control flow happens in C files that include this header and decide which defaults to write or use as bitfield bases.

The visible sequence is source-tree and register-database aligned:

1. The chunk begins in the user/config graphics-register area, continuing PA/SC viewport scissor and viewport Z defaults.
2. It defines PA/CL viewport transform defaults for 16 viewports, user clip plane defaults, SPI pixel shader input controls, SX blend defaults, CB blend controls, VGT/GE draw-state defaults, streamout defaults, and CB color target defaults for slots 0-7.
3. `gc_gfxudec` provides CP event/fence/streamout/counter/scratch/append/atomic/indirect-buffer/coherency defaults and UMD-visible VGT/GE draw-state defaults.
4. `gc_cprs64dec` defines MES register defaults, including non-zero program-counter start, control, pipe priorities, process quantum, and general-purpose register defaults.
5. `gc_gusdec`, `gc_gl1dec`, `gc_chdec`, and `gc_gl2dec` set interconnect/cache arbitration, burst, pipe steering, GL2 control, address-match, writeback/invalidate, and cache-management defaults.
6. Performance blocks define zeroed counter data registers and mostly disabled/unselected selectors, with non-zero sentinel select values such as `0x000fffff`, `0x000003ff`, and SQ select defaults `0x0000f000`.
7. `gc_rlcdec`, `gc_rlcrdec`, and `gc_rlcsdec` define RLC/RLCS control, GPM, load-balancing, power-gating, clock-gating, SPM, PACE, shader profiling, interrupt-disable, exception, idle, and bootload-related defaults.
8. `gc_pwrdec` defines CGTS/CGTT clock and power defaults across shader arrays, WGP/CU subblocks, and graphics frontend/backend blocks.
9. `gc_hypdec`, SDMA hypervisor blocks, and `gc_gcvmsharedhvdec` define hypervisor-visible CP, MES, GRBM, RLC, GCVM, SDMA, and IOMMU defaults.
10. The indexed blocks define CAC controls and weights, fixed/stall/power-brake lookup defaults, SE CAC controls, global and per-SE SPM sample delays, and SQ wave debug register defaults.

## State And Persistence Behavior

The header itself stores no state and performs no persistence. Its constants describe hardware reset/default state or driver base values for register programming. Persistence effects occur only when includers write these constants or modified copies of them to MMIO/indexed registers.

Important state surfaces in this chunk include:

- Render state defaults: PA/SC, PA/CL, SX, CB, DB, SPI, VGT, and GE defaults affect viewport, clipping, shader interpolation, blending, depth/stencil, streamout, and draw dispatch state after driver programming.
- Memory/cache state defaults: GUS, GL1, CH, GL2, GCMC, GCVM, GCVML2, GC_ATC_L2, UTCL1, and SDMA defaults affect arbitration, burst behavior, address matching, invalidation, VM fault state, and translation/cache behavior.
- Firmware/control state defaults: CP, MES, RLC, RLCS, and SDMA hypervisor defaults affect command processor firmware-visible registers, queues, fences, interrupts, power-gating/load-balancing, and virtualization state.
- Observability state defaults: performance counters, SPM sample delays, SQ wave registers, scratch registers, and thread-trace userdata defaults initialize diagnostic and profiling surfaces.

Non-zero defaults are especially state-sensitive because they encode enabled bits, sentinel selectors, masks, or hardware-tuned thresholds. Examples include `mmGRBM_GFX_INDEX_DEFAULT` and `mmGRBM_GFX_INDEX_SR_DATA_DEFAULT` at `0xe0000000`, `mmRLC_CNTL_DEFAULT` at `0x00000001`, many CGTT clock controls at `0x00000100`, SDMA context register type masks, and CAC controls at `0x000001fe`.

## Dependencies

This chunk depends only on the C preprocessor. It has no include directives inside the requested range.

Repository integration dependencies are implied by neighboring generated headers and includers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies the `mm...`/`ix...` register address symbols paired with these defaults.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h` supplies field masks and shifts for code that starts from a `*_DEFAULT` value and applies `REG_SET_FIELD`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c` includes `gc_10_1_0_default.h` alongside offset and mask headers and uses several `*_DEFAULT` symbols as base values for GCVM/GFXHUB setup.
- SOC15 register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD` are the runtime mechanism that makes these compile-time constants meaningful.

## Integration Points

The direct include found in this tree is `amdgpu/gfxhub_v2_0.c`, where default constants are used for GCVM L2 control and protection-fault programming. Although most macros in this chunk are not directly referenced by that file, this header is part of the generated ASIC register contract used by AMDGPU blocks for Navi10/GC 10.1 hardware.

The chunk aligns with multiple AMDGPU integration areas:

- GFX ring and command submission: CP, CPC/CPF/CPG, VGT, GE, IA, WD, and streamout defaults.
- Render backend and frontend programming: PA, SPI, SX, CB, DB, and shader input/viewport defaults.
- Memory management and VM fault handling: GCMC, GCVM, GCVML2, UTCL1, GC_ATC_L2, and SDMA VM context defaults.
- Power and clock management: RLC/RLCS, CGTS, CGTT, GC/SE CAC, and power-brake/stall pattern defaults.
- Profiling and diagnostics: SPM, per-block performance counters, scratch registers, SQ wave indexed registers, and thread trace userdata.
- SR-IOV/hypervisor paths: `gc_hypdec`, `gc_sdma0_sdma0hypdec`, `gc_sdma1_sdma1hypdec`, and `gc_gcvmsharedhvdec` define defaults for virtualization-visible register state.

## Risks And Edge Cases

- Generated-header drift: these constants must stay synchronized with the matching offset and mask headers for GC 10.1.0. A renamed register, wrong default, or mismatched bit definition can silently compile but program incorrect hardware values.
- Cross-generation similarity can hide errors. Several defaults match GC 9.0 and GC 10.3.0 names, but values can differ by generation, as seen in related headers for CAC control. Reusing another generation's default table can break power, VM, or cache behavior.
- Non-zero defaults are high-risk. Values like GL2 control words, GUS arbitration quanta, RLC interrupt masks, CGTS per-WGP controls, SDMA context masks, and CAC weights encode hardware policy rather than simple zero reset state.
- Address-block comments are non-semantic to the compiler but important to generated provenance and human review. Moving macros across decode-block regions can make generated diffs and register audits harder.
- Some macros represent write-sensitive, status, counter, debug, or firmware-owned registers. Treating every `*_DEFAULT` as a value to blindly write at runtime could clear status, disturb counters, or fight firmware ownership.
- The chunk includes indexed `ix...` registers as well as MMIO `mm...` registers. Mixing access paths would be a hardware programming bug: indexed defaults must be used with indexed access mechanisms, not normal MMIO register addresses.
- Large repeated tables, especially CB color target slots, CGTS per-WGP/CU controls, SPM sample delay grids, and CAC weight arrays, are prone to copy/paste or generator off-by-one errors.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/runtime smoke signals:

- C preprocessing/build success for AMDGPU files including `gc_10_1_0_default.h`, especially `amdgpu/gfxhub_v2_0.c`.
- Static checks that every `mm..._DEFAULT` and `ix..._DEFAULT` used by driver code has a matching register symbol in `gc_10_1_0_offset.h` and field definitions in `gc_10_1_0_sh_mask.h` where field updates are performed.
- Diff checks against AMD's generated register database for GC 10.1.0, with special attention to non-zero defaults in this chunk.
- Boot and driver initialization on GC 10.1 hardware without GFXHUB/GCVM fault storms, RLC boot failures, SDMA context failures, hangs during ring tests, or bad power-gating/clock-gating transitions.
- GPU VM tests that exercise protection-fault handling and invalidation paths, because the includer uses this default header in GFXHUB setup.
- Graphics and compute smoke tests covering draw, dispatch, streamout, color/depth targets, shader input interpolation, and performance counter collection.
- Runtime diagnostics for RLC/RLCS, CGTT/CGTS, and CAC changes: unexpected idle/busy state, clock-gating instability, performance counter selection anomalies, or SR-IOV/hypervisor regressions are strong signals that default values in this area may be wrong.

### subset-b-002443: lines 5870-6028

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h lines 5870-6028

## Scope

This chunk is the final segment of the generated AMD GC 10.1.0 default-register header. It contains only C preprocessor `#define` constants for reset/default values. There are no functions, structs, runtime branches, storage objects, or executable initialization logic in this range.

The range starts at the tail of the `sqind` address block with shader wave register defaults from `ixSQ_WAVE_TTMP10_DEFAULT` through the SQ interrupt-word defaults. It then covers the complete `didtind` address block for dynamic inductive droop/throttling defaults across the SQ, DB, TD, and TCP graphics sub-blocks, ending with stall event counter defaults and the file's `#endif`.

## Purpose

`gc_10_1_0_default.h` is generated hardware metadata for AMDGPU's GC 10.1 ASIC generation. Its `_DEFAULT` macros document the hardware reset/default value associated with each register name from the matching GC register address header. Driver code includes this file alongside `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h` so ASIC-specific code can use the correct register names, bit fields, and known default values for Navi10-era graphics hardware.

In this chunk, the SQ wave defaults describe debug-visible per-wave state and interrupt payload registers. The DIDT defaults describe the baseline power/throttle configuration for several graphics pipeline clients:

- `SQ`: shader sequencer / shader queue logic.
- `DB`: depth buffer/render backend logic.
- `TD`: texture data path logic.
- `TCP`: texture cache processor logic.

The DIDT block is concerned with droop-aware throttling, stall insertion, auto-release timing, energy/current-delta control, per-level weights, stall delay tables, status, overflow, rolling power delta, PCC performance counters, and stall event counters.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro convention:

- `ix<REGISTER>_DEFAULT` gives the reset/default value for an indexed GC register.
- The corresponding register address is defined in `gc_10_1_0_offset.h`.
- The corresponding bit layout is defined in `gc_10_1_0_sh_mask.h`.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and DIDT indirect helpers in older power-management code are the normal consumers of these register descriptions.

The `sqind` macros at the beginning of this chunk are all zero defaults:

- `ixSQ_WAVE_TTMP10_DEFAULT` through `ixSQ_WAVE_TTMP15_DEFAULT`: temporary trap scratch register defaults for a selected wave, with full-width `DATA` fields in the companion shift/mask header.
- `ixSQ_WAVE_M0_DEFAULT`, `ixSQ_WAVE_EXEC_LO_DEFAULT`, and `ixSQ_WAVE_EXEC_HI_DEFAULT`: wave scalar `M0` and execution-mask defaults.
- `ixSQ_WAVE_FLAT_SCRATCH_LO_DEFAULT`, `ixSQ_WAVE_FLAT_SCRATCH_HI_DEFAULT`, and `ixSQ_WAVE_FLAT_XNACK_MASK_DEFAULT`: flat scratch and XNACK mask defaults.
- `ixSQ_INTERRUPT_WORD_AUTO_DEFAULT`, `ixSQ_INTERRUPT_WORD_ERROR_DEFAULT`, and `ixSQ_INTERRUPT_WORD_WAVE_DEFAULT`: default encodings for SQ interrupt payload words. The companion masks expose fields such as thread trace, WLT, buffer-full/error bits, error type/detail, wave/SIMD/WGP/SE identifiers, privilege, and encoding.

The DIDT control defaults repeat across SQ, DB, TD, and TCP with block-specific macro prefixes:

- `*_CTRL0_DEFAULT` is `0x0000ff00`, which maps primarily to the high-power threshold field in the matching `*_CTRL0` masks while enable/reset/stall control bits default clear.
- `*_CTRL1_DEFAULT` is `0x00ff00ff`, setting default min/max power fields.
- `*_CTRL2_DEFAULT` is `0x18800004`, covering max power delta plus short-term and long-term interval fields.
- `*_CTRL_OCP_DEFAULT` is `0x000000ff` for SQ/DB/TD and `0x0000ffff` for TCP, setting the over-current-protection maximum power default.
- `*_STALL_CTRL_DEFAULT` is `0x00fff000`, describing default high/low stall delay and maximum-stall fields.
- `*_TUNING_CTRL_DEFAULT` is `0x00010004`, setting high/low max-power-delta tuning fields.
- `*_STALL_AUTO_RELEASE_CTRL_DEFAULT` is `0x00ffffff`, the default auto-release timer value.
- `*_CTRL3_DEFAULT` is `0x00038000`, covering DIDT throttle trigger/power-level/stall-pattern bit selection fields while enable/force/qualify bits default clear.

Each DIDT client also has common pattern and scale defaults:

- `*_STALL_PATTERN_1_2_DEFAULT` = `0x01010001`.
- `*_STALL_PATTERN_3_4_DEFAULT` = `0x11110421`.
- `*_STALL_PATTERN_5_6_DEFAULT` = `0x25291249`.
- `*_STALL_PATTERN_7_DEFAULT` = `0x00002aaa`.
- `*_MPD_SCALE_FACTOR_DEFAULT`, `*_STALL_RELEASE_CNTL0_DEFAULT`, `*_STALL_RELEASE_CNTL1_DEFAULT`, `*_STALL_RELEASE_CNTL_STATUS_DEFAULT`, and `*_WEIGHT0_3/4_7/8_11_DEFAULT` all default to zero.

The EDC and throttle-related defaults likewise repeat across the clients:

- `*_EDC_CTRL_DEFAULT` = `0x00001c00`, setting EDC trigger/stall-pattern bit fields while enable, reset, force-stall, GC/SE combination, and policy bits default clear.
- `*_EDC_THRESHOLD_DEFAULT` = `0x00000000`.
- `*_EDC_STALL_PATTERN_1_2/3_4/5_6/7_DEFAULT` mirror the DIDT stall-pattern defaults.
- `*_EDC_TIMER_PERIOD_DEFAULT` = `0x00003fff`.
- `*_THROTTLE_CTRL_DEFAULT` = `0x00000000`, so GC EDC, PCC, power-brake, and EDC-only stall modes default disabled.
- `*_EDC_STALL_DELAY_*_DEFAULT`, `*_EDC_STATUS_DEFAULT`, `*_EDC_OVERFLOW_DEFAULT`, `*_EDC_ROLLING_POWER_DELTA_DEFAULT`, and `*_EDC_PCC_PERF_COUNTER_DEFAULT` default to zero.

The range is not perfectly symmetrical: `DIDT_DB_EDC_STALL_DELAY_2` and `DIDT_DB_EDC_STALL_DELAY_3` are absent from this GC 10.1.0 default chunk, while SQ, TD, and TCP include delays 1-3. This should be treated as generated hardware description, not as a documentation omission.

## Control Flow

This header has no runtime control flow. The only behavior is compile-time substitution of numeric constants.

The implied driver control flow happens in consumers:

1. Include the GC 10.1.0 offset, shift/mask, and default headers for the target ASIC.
2. Address a register through its `ix...` or `mm...` address macro.
3. Use the shift/mask macros to modify a field with read-modify-write helpers.
4. Optionally compare, initialize, restore, or document expected values using the `_DEFAULT` macro from this file.

For the DIDT registers, real control flow is normally power-management or hardware-initialization sequencing outside this file: enable or reset a DIDT block, program thresholds/timers/patterns, allow/force throttling or stall insertion, poll status/counters, and clear event counters. The defaults in this chunk establish the hardware baseline before that sequencing begins.

## State And Persistence

The macros themselves are stateless constants and do not persist anything. The state they describe lives in GPU registers:

- SQ wave registers are volatile debug/state windows for currently selected shader waves. Values can change as waves are scheduled, trapped, interrupted, killed, or inspected by debug/thread-trace machinery.
- SQ interrupt-word registers describe interrupt payload formatting and event state that is hardware-generated rather than durable driver state.
- DIDT registers hold graphics power/throttling policy, timers, stall patterns, and counters. These can be reset by GPU reset, graphics IP reset, power-gating transitions, suspend/resume, firmware or SMU policy changes, and explicit driver writes.

The default values are important because they are the only persistent source-level record of expected reset state in this header. Code that writes DIDT registers must preserve hardware-owned or reserved fields according to the companion masks, because a full-register write can unintentionally change throttle policy, stall thresholds, or counter clear bits.

## Dependencies

This chunk depends on AMD's generated register metadata for the same ASIC revision staying in sync:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies register addresses such as `ixSQ_WAVE_TTMP10`, `ixSQ_INTERRUPT_WORD_ERROR`, `ixDIDT_SQ_CTRL0`, `ixDIDT_DB_CTRL0`, `ixDIDT_TD_CTRL0`, and `ixDIDT_TCP_CTRL0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h` supplies field names and masks for interpreting the defaults, including `SQ_WAVE_TTMP10__DATA_MASK`, `SQ_INTERRUPT_WORD_ERROR__ERR_TYPE_MASK`, and the `DIDT_*` enable, threshold, pattern, timer, status, and throttle masks.
- AMDGPU GC/GFX hub and power-management code includes GC 10.1.0 generated headers when programming Navi10-class graphics registers.
- SOC15 register access helpers provide the actual MMIO or indexed-register access paths.
- Firmware/SMU policy may also influence DIDT/throttling behavior, so these defaults are not the complete runtime policy.

The file path is under a Ceph-client source mirror, but the content is AMDGPU DRM hardware metadata and has no dependency on Ceph filesystem logic.

## Integration Points

The SQ wave defaults integrate with shader debugging, trap handling, wave inspection, thread trace, and interrupt reporting. The associated field layouts expose wave identifiers, SIMD/WGP/SE location, privilege state, error detail/type, and thread trace conditions used by diagnostics and fault reporting.

The DIDT defaults integrate with graphics power and reliability management. The common SQ/DB/TD/TCP pattern means the same conceptual throttling machinery is replicated per hardware client: thresholds and interval sizing estimate power or droop risk, stall patterns shape the duty cycle of inserted stalls, auto-release and release-control registers govern stall recovery, and EDC/PCC status/counter registers expose whether power-delta or current-related controls are triggering.

The header is directly included by `amdgpu/gfxhub_v2_0.c`, which includes the GC 10.1.0 offset, shift/mask, and default headers as the ASIC description set for GFXHUB v2.0. DIDT register families are also conceptually tied to power-management code paths that read and write `ixDIDT_*_CTRL0` registers using `DIDT_*_CTRL0__DIDT_CTRL_EN_MASK`-style masks, even when the visible example in this source tree is for older ASIC support.

## Risks

- This is generated hardware data. Hand-editing a default value can silently desynchronize the driver from AMD's register specification.
- The chunk starts mid-`sqind` register family. Earlier `SQ_WAVE_*` defaults are in the previous chunk, so file-level research should merge both ranges before drawing conclusions about the full SQ wave window.
- The DIDT register families are repetitive. Copying a value or mask between SQ, DB, TD, and TCP can compile cleanly but affect the wrong hardware client.
- `DIDT_TCP_CTRL_OCP_DEFAULT` differs from the SQ/DB/TD OCP default. Treating the four clients as byte-for-byte identical would lose a real hardware distinction.
- DB lacks the EDC stall delay 2 and 3 defaults present for SQ, TD, and TCP in this chunk. Consumers or validators should not assume every DIDT client has the exact same register list.
- Many DIDT controls are sequencing-sensitive: enable, reset, force-stall, throttle-mode, auto-release, and counter-clear bits must be written deliberately. Incorrect full-register writes can cause performance loss, throttling instability, or misleading counters.
- Some SQ interrupt masks in the companion header extend above 32 bits. Consumers must use appropriately wide integer types when decoding those payload words.
- Runtime firmware or SMU policy may override or reprogram throttling behavior, so these defaults should not be interpreted as the steady-state operating configuration after driver and firmware initialization.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU code that includes `gc_10_1_0_default.h`, especially GFXHUB v2.0 and GC 10.1 paths.
- Static comparison against regenerated AMD register headers to ensure `_DEFAULT` values and register presence match the authoritative hardware source.
- Cross-checks that every default macro in this range has a matching address macro in `gc_10_1_0_offset.h` and field definitions in `gc_10_1_0_sh_mask.h` where applicable.
- GPU reset, suspend/resume, and power-gating tests on GC 10.1/Navi10 hardware to confirm default restore assumptions do not regress.
- Shader trap/debug/thread-trace tests that exercise SQ wave state and SQ interrupt-word decoding.
- Power-management stress tests that exercise graphics load transitions, throttling, over-current or power-brake paths, and DIDT/EDC counter readback.
- Performance regression tests for shader, depth-buffer, texture, and texture-cache workloads, since DIDT misprogramming is likely to show up as unexpected throttling rather than a build failure.
