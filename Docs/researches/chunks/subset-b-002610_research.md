# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h lines 1-2940

## Scope

This chunk is the first 2,940 lines of the generated AMD GC 9.0 register default header. It starts with the AMD MIT-style license, header guard `_gc_9_0_DEFAULT_HEADER`, and then defines reset/default values for GC 9.0 graphics IP registers as C preprocessor constants named `mm<REGISTER>_DEFAULT`.

The requested range contains 2,812 `#define` macros grouped by generated `// addressBlock:` comments. It covers these address blocks through the start of `gc_perfsdec`: `gc_grbmdec`, `gc_cpdec`, `gc_padec`, `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, `gc_rbdec`, `gc_rmi_rmidec`, `gc_utcl2_atcl2dec`, `gc_utcl2_vml2pfdec`, `gc_utcl2_vml2vcdec`, `gc_utcl2_vmsharedpfdec`, `gc_utcl2_vmsharedvcdec`, `gc_tcdec`, `gc_shdec`, `gc_cppdec`, `gc_cppdec2`, `gc_spipdec`, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, `gc_rasdec`, `gc_gfxdec0`, `gc_gfxudec`, `gc_perfddec`, `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_vml2prdec`, and lines 2788-2940 of `gc_perfsdec`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for Vega/Raven-era GC 9 graphics IP. It is not Ceph filesystem code and contains no filesystem behavior.

## Purpose

`gc_9_0_default.h` gives driver code the documented hardware reset/default values for GC 9.0 registers. These defaults are paired with the matching GC 9.0 offset header, which provides register addresses, and the matching shift/mask header, which provides field encodings. Consumers use the constants as known-good seeds for read-modify-write programming, reset/init sequences, power-management policy, diagnostics, and command-stream state restoration.

Major register areas in this chunk include:

- Graphics register bus manager and command processor status/control defaults, including GRBM status/reset/error/trap/scratch registers, CP front-end/CPC/CPF/MEC status, ring-buffer, doorbell, interrupt, priority, preemption, VMID, and MQD/HQD queue defaults.
- Primitive assembly, rasterization, shader, texture, color-buffer, depth-buffer, render-backend, and global data-share defaults for draw and compute state.
- Shader core and SPI defaults, including SQ/SQC configuration, instruction-category counters, shader program/user-data registers, compute dispatch registers, wave limits, trap/debug registers, and thread-trace defaults.
- Graphics VM and cache defaults, including VM context controls for contexts 0-15, page-table base/start/end registers, invalidation engines 0-17, VM L2 protection fault policy, ATC L2, MC aperture/location registers, TCP/TCC/TCA cache controls, and RMI routing.
- Context-state style defaults for viewport/scissor arrays, clip planes, shader input controls, blend controls, color/depth target descriptors, stream-out state, tessellation/geometry state, MSAA/centroid/sample state, and draw-index state.
- Performance counter data and selector defaults for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA/TD, TCP/TCC/TCA, CB, DB, RLC, RMI, ATC L2, and VM L2.

## Important APIs, Types, And Macros

There are no functions, structs, enums, inline helpers, global variables, or callable APIs in this chunk. The public interface is the generated macro naming contract:

- `mm<REGISTER>_DEFAULT` is a 32-bit default/reset value for the named GC 9.0 register.
- Matching register-address macros live in `gc_9_0_offset.h`, normally as `mm<REGISTER>` plus a base-index macro.
- Matching field macros live in `gc_9_0_sh_mask.h`, normally as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- AMDGPU consumers combine these defaults with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, indexed-register helpers, and PM4/ring write helpers.

Important macro families in this range:

- `mmGRBM_*_DEFAULT`: GRBM control, status, clock gating, trap, scratch, read/write error, IOV error, RSMU, and UTCL2 invalidation range defaults.
- `mmCP_*_DEFAULT`, `mmCPC_*_DEFAULT`, `mmCPF_*_DEFAULT`, `mmCPG_*_DEFAULT`, and `mmCP_HQD_*_DEFAULT`: command processor front-end, graphics rings, compute queues, MQD/HQD queue descriptors, doorbells, interrupts, EOP, DMA, indirect-buffer, coherency, atomic, scratch, and performance defaults.
- `mmVM_*_DEFAULT`, `mmATC_L2_*_DEFAULT`, and `mmMC_VM_*_DEFAULT`: GPU virtual-memory context, L2 TLB/cache, invalidation, protection-fault, identity aperture, framebuffer aperture, AGP/system aperture, local HBM range, and page-table defaults.
- `mmSQ_*_DEFAULT`, `mmSQC_*_DEFAULT`, `mmSPI_*_DEFAULT`, and `mmCOMPUTE_*_DEFAULT`: shader queue/configuration, SQC cache, shader program/user data, pixel/vertex/geometry shader state, compute dispatch, wave lifetime, thread trace, and resource-reservation defaults.
- `mmPA_*_DEFAULT`, `mmVGT_*_DEFAULT`, `mmIA_*_DEFAULT`, `mmWD_*_DEFAULT`, `mmDB_*_DEFAULT`, `mmCB_*_DEFAULT`, `mmSX_*_DEFAULT`, and `mmTA/TD/TCP/TCC/TCA_*_DEFAULT`: draw setup, primitive assembly, scan conversion, depth/stencil, color buffer, texture/cache, raster, line/point/clip/viewport, stream-out, and render-target defaults.
- `mmGDS_*_DEFAULT` and `mmRAS_*_DEFAULT`: global data-share VMID partitions, GWS/OA/atomic state, context-switch state, and RAS signature defaults.
- `mm*_PERFCOUNTER*_DEFAULT`, `mm*_PERFCOUNTER*_SELECT_DEFAULT`, `mmRLC_SPM_*_DEFAULT`, and latency/select defaults: performance counter data, selectors, filters, windows, sample delays, masks, and bins.

Concrete local consumers include `amdgpu/gfx_v9_0.c`, `amdgpu/gfxhub_v1_0.c`, and `pm/powerplay/hwmgr/vega10_inc.h`. For example, `gfxhub_v1_0.c` seeds VM L2 programming from `mmVM_L2_CNTL3_DEFAULT` and `mmVM_L2_CNTL4_DEFAULT` before setting hardware-specific fields, while `gfx_v9_0.c` restores SPI wave-limit programming with `mmSPI_WCL_PIPE_PERCENT_CS0_DEFAULT` and `mmSPI_WCL_PIPE_PERCENT_GFX_DEFAULT`.

## Control Flow

This header has no runtime control flow. Inclusion only makes constants available to C translation units, and each macro is expanded by the preprocessor wherever referenced.

The implied driver flow is:

1. Select the GC 9.0 register headers for the active SOC15 graphics IP.
2. Use `gc_9_0_offset.h` to identify a register address.
3. Use a `mm..._DEFAULT` value as the initial full-register value or as a reference value for restore/reset logic.
4. Optionally adjust fields with `REG_SET_FIELD` using `gc_9_0_sh_mask.h`.
5. Write the result through AMDGPU MMIO, RLC-safe MMIO, indexed-register, or ring/PM4 mechanisms.

The ordering, locking, waits, cache flushes, interrupt handling, queue stop/start, and power-transition behavior are not in this file. They live in GC 9 driver code such as graphics initialization, VM hub setup, command processor ring setup, RLC/PM management, reset/resume paths, diagnostics, and command submission.

## State And Persistence Behavior

The macros are stateless compile-time constants and persist nothing by themselves. The hardware registers they describe are stateful. Once programmed, many GC registers persist until overwritten, context-switched, power-gated, reset, or restored during suspend/resume and GPU reset recovery.

Several groups in this chunk are especially state-sensitive:

- VM state: `mmVM_CONTEXTn_CNTL_DEFAULT`, page-table base/start/end defaults, invalidation-engine defaults, fault-control defaults, aperture registers, and L2/ATC defaults affect GPU address translation, protection-fault behavior, TLB/cache invalidation, and dummy/default-page handling.
- Queue state: CP ring, MQD, HQD, doorbell, RPTR/WPTR, IB, EOP, priority, VMID, interrupt, and preemption defaults define how graphics and compute queues start from reset and how inactive queue descriptors should look.
- Draw context state: shader program/user-data defaults, compute dispatch defaults, viewport/scissor arrays, clip planes, blend/color/depth target descriptors, stream-out, tessellation, rasterization, sample/centroid controls, and render-backend defaults determine what state is safe before userspace or kernel command streams program real values.
- Cache and memory state: TCP/TCC/TCA, RMI, ATC/VM L2, coherency, DMA, and cache invalidate/writeback defaults influence memory visibility, faulting, and ordering assumptions.
- Perf/debug/RAS state: performance counter data/select registers, thread trace, trap/debug, RAS signature, and error-count defaults must be reset or preserved according to the diagnostic path using them.

Many defaults are zero, but non-zero values are meaningful hardware policy rather than decoration. Examples in the requested range include `mmGRBM_CNTL_DEFAULT` at `0x00000018`, `mmCP_MEC_CNTL_DEFAULT` at `0x50000000`, `mmSQ_CONFIG_DEFAULT` at `0x01180000`, `mmVM_CONTEXT0_CNTL_DEFAULT` through `mmVM_CONTEXT15_CNTL_DEFAULT` at `0x007ffe80`, `mmCP_RB0_CNTL_DEFAULT` at `0x00400000`, `mmCP_HQD_PERSISTENT_STATE_DEFAULT` at `0x0be05301`, `mmIA_MULTI_VGT_PARAM_DEFAULT` at `0x006000ff`, and selector masks such as `mmSQ_PERFCOUNTER_MASK_DEFAULT` at `0xffffffff`.

This header does not say whether a register is read-only, write-only, sticky, pulse-style, protected, shadowed, context-saved, safe for read-modify-write, or reset-only. Callers must rely on the hardware specification and established AMDGPU programming sequences.

## Dependencies And Integration Points

Direct dependencies are generated-register consistency and include order:

- `gc_9_0_offset.h` must define the corresponding `mm...` register addresses.
- `gc_9_0_sh_mask.h` must define compatible fields for any default that consumers modify with `REG_SET_FIELD` or inspect with `REG_GET_FIELD`.
- `soc15.h`, `soc15_common.h`, AMDGPU MMIO helpers, RLC-safe accessors, PM4/ring helpers, and IP-version dispatch code provide the actual access paths.
- Related generated headers for other IP blocks, such as MMHUB defaults, may define macros with identical names. Include context matters because `mmVM_CONTEXT0_CNTL_DEFAULT` also appears in MMHUB default headers.

Local integration points visible in this tree:

- `amdgpu/gfx_v9_0.c` includes this file with the GC 9 offset and sh/mask headers and uses defaults in graphics resource and wave-limit programming.
- `amdgpu/gfxhub_v1_0.c` includes this file and uses VM defaults during graphics hub aperture, L2, context, and fault-control initialization.
- `pm/powerplay/hwmgr/vega10_inc.h` aggregates this default header with GC offset and sh/mask headers for Vega10 power-management code.

Functional integration points include graphics IP initialization, GFX/compute ring bring-up, HQD/MQD management, VM hub setup, TLB/cache invalidation, page-fault reporting, queue preemption, doorbells, interrupt routing, RLC and power-gating flows, render/compute context state setup, stream-out/counter reporting, RAS/error telemetry, and performance counter programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong default compiles cleanly but can seed incorrect hardware state, causing VM faults, hangs, corrupted rendering, missing interrupts, broken queues, bad performance data, or power-management regressions.
- Defaults are ASIC/IP-specific. Reusing GC 9.0 values for later GC IPs, or mixing GC defaults with MMHUB defaults that use the same macro names, can produce valid C with invalid hardware programming.
- Non-zero defaults often encode reserved, workaround, or policy bits. Replacing a default seed with zero, or using full-register writes without preserving required bits, can regress only some ASICs or only reset/resume paths.
- Repeated families are error-prone: VM contexts 0-15, invalidation engines 0-17, viewports 0-15, color targets 0-7, stream-out buffers 0-3, GDS VMIDs 0-15, and many performance counters must remain slot-consistent.
- Address-like defaults often use hardware-specific units and split low/high fields. Consumers must not treat page-table, framebuffer, stream-out, color/depth, DMA, EOP, scratch, and coherency addresses as raw byte-address fields without checking the associated offset and mask header.
- Queue and doorbell defaults are safety-critical. Ring control, active bits, MQD/HQD state, RPTR/WPTR reporting, EOP pointers, IB control, priority, VMID, and interrupt defaults interact with scheduler and KFD expectations.
- VM L2 and protection-fault defaults affect security and isolation. Incorrect fault-enable, dummy-page, context-disable, or invalidation settings can hide illegal accesses, over-report faults, or allow stale translations.
- Performance/debug defaults can perturb normal workloads if left enabled or misconfigured. Thread trace, trap screens, SPM, perf selectors, and latency stats must be restored after diagnostics.
- This chunk ends inside `gc_perfsdec`; the following chunk is needed for the rest of the performance selector/sample-delay defaults and the header guard close.

## Test Signals

Useful validation is mostly compile coverage, generated-data consistency, and hardware runtime coverage:

- Kernel build coverage for GC 9 AMDGPU code that includes this header, especially `gfx_v9_0.c`, `gfxhub_v1_0.c`, Vega10 power-management includes, and any files using GC 9 defaults through aggregate headers.
- Mechanical comparison of every `mm..._DEFAULT` in lines 1-2940 against AMD's authoritative GC 9.0 register database.
- Cross-check that each default macro in this chunk has a corresponding register address in `gc_9_0_offset.h`, and that defaults adjusted with `REG_SET_FIELD` have compatible fields in `gc_9_0_sh_mask.h`.
- Static duplicate-name checks against other IP headers, especially MMHUB VM defaults, to ensure consumers include and reference the intended IP block.
- Boot, suspend/resume, runtime power-management, GPU reset, and mode-switch coverage on GC 9 ASICs such as Vega/Raven family devices.
- GFX and compute queue tests covering ring initialization, doorbells, EOP fences, indirect buffers, VMID assignment, queue preemption, HQD/MQD activation/deactivation, and priority changes.
- VM tests covering GART setup, VRAM/system apertures, per-VMID page-table programming, invalidation engines, protection-fault reporting, dummy pages, XGMI/CPU translation paths, and cache/TLB flushes.
- Rendering and compute tests covering draw setup, shader program/user data, compute dispatch, stream-out, color/depth/stencil targets, blend/CB state, rasterization, tessellation/geometry paths, MSAA/centroid state, and reset-state assumptions before userspace commands.
- Diagnostics and observability tests for RAS signatures, EDC counters, thread trace, trap/debug state, CP stream-out and pipeline statistics, and performance counters/selectors.
- Runtime warning signals include GPU hangs during ring start or VM invalidation, unexpected page faults, bad fence completion, corrupted render targets, broken compute dispatch, stale translations after reset/resume, missing interrupts, incorrect perf counter readings, and regressions that appear only after diagnostics or power transitions.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002610`. It covers lines 1-2940 of `gc_9_0_default.h`; the final per-file document should merge it with later chunks that continue `gc_perfsdec` from line 2941, then cover RLC/power/hypervisor/indirect blocks and the header guard close.
