# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h lines 2473-4919

## Scope

This chunk is a generated AMD GC 9.4.2 register-offset header segment. It contains C preprocessor constants only: register offset macros named `reg*` and their paired `*_BASE_IDX` macros. There are no functions, structs, enums, variables, includes, branches, loops, locks, allocations, callbacks, or executable statements in this range.

The selected range starts in the middle of the `gc_gfxdec0` address block. Line 2473 is only `regCB_COLOR0_ATTRIB2_BASE_IDX`, whose matching `regCB_COLOR0_ATTRIB2` offset appears in the previous chunk. It then completes the color-buffer render-target register windows through `regCB_COLOR7_DCC_BASE_EXT`. The range continues through these address blocks:

- `gc_gfxudec`, base address `0x30000`, covering command processor counters, scratch registers, CP DMA/coherency/IB state, RLC GPM perf counts, graphics frontend state, GDS, SQ, SPI, CB/DB, and assorted graphics-user registers.
- `gc_grbmdec`, base address `0x8000`, covering GRBM status/control/scratch/trap registers.
- `gc_hypdec`, base address `0x3e000`, covering CP and RLC microcode access aliases plus GPU IOV virtualization registers.
- `gc_padec`, base address `0x8800`, covering global PA/VGT/WD/IA/GE/GC control, trap/binning, FIFO, UTCL1, and early raster/frontend controls.
- `gc_perfddec`, base address `0x34000`, covering performance-counter low/high readout registers for CP, GRBM, RLC, GDS, PA, SPI, SQ, SX, TA, TD, TCP, TCC/TCA, CB, and DB blocks.
- `gc_perfsdec`, base address `0x36000`, covering performance-counter select, select1, filter, mask, and control registers for the same GC sub-blocks.
- `gc_pwrdec`, base address `0x3c000`, covering CGTS/CGTT clock, CU power gating, TCC disable, SQ throttling, and per-block clock-control registers.
- `gc_rbdec`, base address `0x9800`, covering DB memory, scan, stencil/depth, HiZ/HiS, DFSM, RB redundancy/backend-disable, GB address/tile/macro-tile modes, CB hardware arbitration/DCC, and user RB disable/redundancy registers.
- The beginning of `gc_rlcpdec`, base address `0x3b000`, through `regRLC_SERDES_WR_NONCU_MASTER_MASK_1_BASE_IDX`.

Within lines 2473-4919 there are 2,411 `#define` lines: 1,205 register-offset macros and 1,206 base-index macros. The count is intentionally uneven because the chunk begins on a carried-over `_BASE_IDX` line.

Although the source tree is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for AMD GC 9.4.2 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_9_4_2_offset.h` supplies symbolic dword offsets for AMD Graphics Core 9.4.2 hardware registers. Driver code combines these constants with SOC15 register helpers such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and RLC-safe access helpers, then uses the companion shift/mask header to pack or decode fields.

This chunk covers a broad slice of GC register addressability:

- Color-buffer state for render targets 0 through 7, including base and extension addresses, views, attributes, info, DCC control/base, CMASK/FMASK base and extension, and clear words.
- Command processor and graphics-user state for event-of-pipe completion, streamout, primitive/statistics counters, scratch windows, atomics, semaphore waits, CP DMA, coherency windows, indirect-buffer and preamble state, CE/PFP metadata, indirect draw/dispatch addresses, index-buffer state, and ME coherency status.
- Graphics frontend state for GRBM instance selection, VGT primitive/index/streamout/tessellation state, WD/IA buffer and multi-VGT controls, PA line stipple, screen extents, trap screens, and DB occlusion counters.
- GDS access, VMID/GWS/OA windows, protection/fault reporting, compute dispatch routing, and EDC counters.
- SQ and SPI debug/configuration registers, including thread trace, shader debug wave status, trap controls, wave launch controls, per-VMID debug, performance snapshots, SQC cache invalidation, and SPI launch/attribute/throttle controls.
- CB/DB runtime controls and per-block performance counters/selectors used by diagnostics and performance tooling.
- GRBM status, soft reset, clock enable, trap, scratch, fence, and error-reporting registers.
- Hypervisor and SR-IOV style CP/RLC aliases, GPU IOV scheduling/status, VF enable/mask/status, doorbell status, SDMA busy/status, virtual reset request, and virtualization interrupt registers.
- Power and clock-control surfaces for clock gating, CU-level clock control, TCC disable masks, SQ throttling, RMI, CB/DB/TCC/TCA/TCP/GDS/CP/RLC clock controls, and GRBM CGTT.
- RB/GB configuration for backend mapping, tile and macrotile modes, depth/stencil/HiZ/HiS memory layout, DB FIFO/scan/ring/DFSM controls, CB hardware arbitration, DCC configuration, and user-visible RB disable/redundancy masks.
- The start of the RLC processor control/status block, including RLC enable/status/safe-mode, RLCV command/safe-mode, reference-clock timestamp, GPM timer interrupts/control/status, load-balance counter, and SERDES non-CU write mask.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The exported interface is the generated macro naming contract:

- `reg<REGISTER_NAME>` gives a register dword offset in the GC 9.4.2 SOC15 register space for the address block selected by the helper layer.
- `reg<REGISTER_NAME>_BASE_IDX` gives the base-index selector associated with that register. In this chunk, most user/perf/RLC-style windows use base index `1`, while many PA/RB block-local offsets use base index `0`.
- Matching bit layouts are expected in `gc_9_4_2_sh_mask.h`; matching reset values, where generated, are expected in the default header for this ASIC family.
- Consumer code should use these macros through AMDGPU register helper abstractions rather than manually adding raw byte addresses.

Major macro families in this chunk include:

- `regCB_COLOR0_*` through `regCB_COLOR7_*`: render-target base, metadata, compression, mask, clear, and DCC address state.
- `regCP_*` and `regSCRATCH_*`: EOP writeback, streamout/stat counters, scratch, append/fence state, atomic pre-ops, semaphore wait/signal, CP DMA, coherency, IB, preamble, CE/PFP metadata, indirect draw/dispatch, index, and sample status registers.
- `regGRBM_*`: graphics register bus manager selection, status, reset, clock, interrupt, trap, scratch, fence, and violation reporting.
- `regRLC_*`: GPM performance counts, microcode access, GPU IOV/virtualization control and status, clock controls, and the start of RLC core control/status/timer registers.
- `regVGT_*`, `regWD_*`, `regIA_*`, `regPA_*`, `regGE_*`, `regGC_*`, and `regCC_*`: graphics frontend, primitive assembly, workload distributor, scan converter, binning, shader-array/user controls, and rasterization-related offsets.
- `regGDS_*`: global data store read/write address/data, VMID/GWS/OA windows, protection/fault, dispatch routing, EDC, and GDS performance counters/selectors.
- `regSQ_*`, `regSPI_*`, `regSQC_*`, `regSX_*`, `regTA_*`, `regTD_*`, `regTCP_*`, `regTCC_*`, `regTCA_*`, and `regTCX_*`: shader/debug/thread-trace/cache/performance/clock-control surfaces.
- `regCPG_*`, `regCPC_*`, and `regCPF_*`: command processor graphics/compute/frontend performance counters and latency-statistics selectors.
- `regCGTS_*` and `regCGTT_*`: clock-gating, per-CU control, TCC disable, and block clock-control registers.
- `regDB_*`, `regGB_*`, `regCB_HW_*`, `regCB_DCC_CONFIG`, `regGC_USER_RB_*`, and `regCC_RB_*`: RB/DB/GB tiling, depth/stencil, HiZ/HiS, DFSM, backend disable/redundancy, CB arbitration, DCC, and memory layout controls.

## Control Flow

This header has no runtime control flow. All behavior is compile-time macro substitution.

The implied driver flow is:

1. Select the GC 9.4.2 generated register headers for Aldebaran/GC 9.4.2-class hardware.
2. Select a `reg*` offset from this header and a field mask/shift from `gc_9_4_2_sh_mask.h` when field manipulation is needed.
3. Use SOC15/MMIO/PM4/RLC helper code to read, write, poll, dump, or emit the register address for graphics, compute, debug, reset, virtualization, power, or performance-monitor paths.
4. Let the surrounding driver sequence own ordering, idleness checks, lock context, firmware coordination, register broadcast/instance selection, and timeout behavior.

For example, graphics initialization can program golden registers such as `regGB_ADDR_CONFIG`, debug paths can compose values for SPI/TCP debug registers, RAS paths can read GDS EDC counters, idle/reset paths can poll `regGRBM_STATUS`, and RLC bring-up paths can read or write `regRLC_CNTL`. This header only supplies the numeric offsets used by those flows.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware registers whose values may be persistent configuration, context state, volatile status, writeback addresses, side-effect triggers, counters, or firmware-owned state.

CB color registers describe render-target surface and compression state. Base/base-extension, DCC base, CMASK/FMASK, view, info, attrib, and clear-word registers are context-sensitive graphics state; incorrect offsets can bind the wrong memory, corrupt render targets, or break DCC/fast-clear behavior.

CP registers in this chunk include writeback addresses, streamout/statistics counters, append/fence state, atomic/semaphore operands, DMA source/destination/command registers, coherency ranges, IB/preamble state, and indirect draw/dispatch/index state. These values may be programmed by command submission paths, saved in context-related hardware, or read as volatile progress/status.

GRBM status and reset registers are global graphics lifecycle state. Status registers are volatile observations of busy/idle conditions; soft-reset and clock-enable/control registers affect live hardware state and must be sequenced with idleness and firmware expectations.

GDS, VMID, GWS, and OA registers expose per-VMID allocation/protection state and fault counters. These settings interact with compute queue isolation and KFD-visible behavior; some EDC counters are diagnostic state that may be sticky until cleared by a documented sequence.

SQ/SPI/SQC registers combine debug, trap, thread-trace, cache, launch, throttle, and performance surfaces. Some are persistent debug controls, some are volatile wave/status snapshots, and cache invalidation registers can have side effects when written.

Performance-counter readout and select registers are instrumentation state. Selector/filter registers persist until reprogrammed; low/high counter readouts are volatile and require coherent sampling rules outside this header.

CGTS/CGTT and SQ throttling registers are power-management and clock-gating state. Bad writes can disable units, mask TCCs, alter CU-level clocks, skew performance, or interfere with RLC/SMU ownership of power state.

RB/DB/GB registers cover backend topology, tiling mode tables, depth/stencil/hierarchical-Z layout, DFSM controls, FIFO/ring/watermark policy, CB arbitration, DCC config, and user backend masks. These values persist as graphics global or context state until reset or reprogramming and are central to address swizzling and render backend availability.

The RLC registers at the end of the chunk are RLC processor control/status and timer state. `regRLC_CNTL`, safe-mode, RLCV command, timer interrupts, and load-balance counters participate in firmware-controlled graphics power, context save/restore, and virtualization flows.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. The semantic dependency is AMD's generated GC 9.4.2 register database and its companion headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h` supplies matching field shifts and masks.
- Any generated GC 9.4.2 default header supplies reset/default values where available.
- AMDGPU SOC15 helper macros and MMIO/RLC/PM4 accessors interpret the `reg*` and `_BASE_IDX` constants.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c`, which includes this offset header for Aldebaran graphics initialization, golden settings, RAS/EDC register tables, compute diagnostics, and graphics control paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c`, which includes this header for KFD/debug integration, including debug trap control and TCP watch register addressing.

Important integration surfaces for this chunk are render-target programming, CP writeback and DMA/coherency paths, primitive/stat counter readback, scratch windows, GDS VMID/GWS/OA setup, SQ/SPI debug and trap handling, SQC cache invalidation, shader thread trace, performance-monitor setup/readout, GRBM idle/reset/status polling, hypervisor/GPU IOV scheduling and VF status, power/clock gating, RB backend mapping, GB tiling tables, DB depth/stencil layout, and RLC enable/safe-mode/timer handling.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong offset still compiles but can make a correct-looking register access touch unrelated hardware.
- This chunk starts mid-family. `regCB_COLOR0_ATTRIB2_BASE_IDX` has no matching offset inside the selected lines, so merge-time analysis must join the previous chunk for the complete `CB_COLOR0` group.
- The chunk also ends inside `gc_rlcpdec`; later chunks are required for the rest of the RLC register block.
- Repeated register families are index-sensitive: `CB_COLOR0..7`, `SCRATCH_REG0..7`, streamout and primitive counters, `GDS_VMID0..15`, `GDS_GWS_VMID0..15`, `GDS_OA_VMID0..15`, `GRBM_STATUS_SE0..3`, many per-block performance counters, `CGTS_CU0..15`, `GB_TILE_MODE0..31`, and `GB_MACROTILE_MODE0..15`. A single shifted value can produce lane-specific failures.
- Several symbols intentionally alias the same offset, such as CP ME atomic aliases and hypervisor/non-hypervisor microcode aliases. Consumers must understand ownership rather than assuming unique addresses.
- Status, counter, control, write-one/clear, side-effect, and reserved fields are indistinguishable at the offset-macro level. The shift/mask header and hardware programming guide are required for safe writes.
- Split low/high address registers appear throughout CP, CB, TA, and writeback paths. Incorrect pairing or ordering can point hardware at the wrong GPU virtual or physical address.
- `regGRBM_SOFT_RESET`, clock controls, CGTS/CGTT controls, SQ throttling, TCC disable masks, RLC controls, and GPU IOV registers can affect global device progress, reset behavior, virtualization isolation, and power management.
- GB tiling/macrotile, DB layout, CB DCC, and backend-disable/redundancy offsets are high blast-radius registers: incorrect programming can produce rendering corruption, memory addressing bugs, or bad harvesting/topology exposure.
- Performance counters require block selection, filtering, low/high sampling, and overflow handling outside this header. The presence of `*_LO`/`*_HI` offsets alone does not describe a coherent read protocol.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware integration:

- Kernel build or preprocessing coverage for `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`.
- Mechanical comparison against AMD's authoritative GC 9.4.2 register database for every offset and `_BASE_IDX` in lines 2473-4919.
- Static checks that each register offset has a matching `_BASE_IDX`, while allowing the known leading carried-over `_BASE_IDX` in this chunk.
- Cross-checks against `gc_9_4_2_sh_mask.h` so register names used with `REG_SET_FIELD` and `REG_GET_FIELD` have matching field definitions.
- Runtime graphics tests that exercise render-target setup, DCC/fast clear, CMASK/FMASK, depth/stencil, HiZ/HiS, tiling/macrotile modes, backend harvesting, primitive statistics, occlusion queries, streamout, tessellation, binning, and raster trap-screen paths.
- CP and command-submission tests covering EOP writebacks, fences, append/streamout counters, indirect buffers, preambles, indirect draw/dispatch, index buffers, CP DMA copies, semaphore wait/signal, coherency waits, and scratch access.
- KFD/compute tests covering GDS VMID/GWS/OA allocation, debug trap setup, TCP watchpoints, shader wave launch/debug controls, thread trace, and queue isolation on Aldebaran-class hardware.
- RAS diagnostics that validate GDS EDC counters and related GRBM-count paths used by `gfx_v9_4_2.c`.
- Idle, hang, and reset tests that poll `regGRBM_STATUS*`, exercise `regGRBM_SOFT_RESET`, and verify RLC control/safe-mode interactions.
- Virtualization/SR-IOV tests that exercise GPU IOV VF enable/mask/status, doorbell status, SDMA busy/status, virtual reset request/response, and IOV interrupt force/disable paths.
- Power-management tests for CGTS/CGTT clock controls, TCC disable masks, CU-level clock controls, SQ throttling, and RLC/GRBM clock controls under suspend/resume, reset, and workload transitions.
- Performance-monitor tests that program select/filter registers, sample low/high counter pairs for CP/GRBM/RLC/GDS/PA/SPI/SQ/SX/TA/TD/TCP/TCC/TCA/CB/DB, and verify block attribution, monotonicity, overflow, and zero/stuck-counter behavior.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002664`. It covers lines 2473-4919 of `gc_9_4_2_offset.h`. The final per-file research should merge it with the previous chunk for the start of the `CB_COLOR0` family and with later chunks for the remainder of `gc_rlcpdec` and the complete GC 9.4.2 generated register-offset namespace.
