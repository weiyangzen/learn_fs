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
