# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002663`: lines 1-2472, `Docs/researches/chunks/subset-b-002663_research.md`
- `subset-b-002664`: lines 2473-4919, `Docs/researches/chunks/subset-b-002664_research.md`
- `subset-b-002665`: lines 4920-7410, `Docs/researches/chunks/subset-b-002665_research.md`
- `subset-b-002666`: lines 7411-7687, `Docs/researches/chunks/subset-b-002666_research.md`

## Chunk Research

### subset-b-002663: lines 1-2472

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h lines 1-2472

## Scope

This chunk covers the opening 2,472 lines of the generated AMD GC 9.4.2 register offset header. The range starts with the AMD permissive license and include guard `_gc_9_4_2_OFFSET_HEADER`, then defines register offset constants for these address blocks:

- `didtind`, base address `0x0`, indirect DIDT/PCC/EDC throttling registers for SQ, DB, TD, TCP, and DBR-related counters.
- `gc_cpdec`, base address `0x8200`, command processor decoder status, busy, stalled, scratch, queue, ring-read-pointer, queue-threshold, and privileged violation registers.
- `gc_cppdec`, base address `0xc080`, CP public/control registers for ring buffers, write pointers, interrupts, doorbells, VMID, UTCL1 errors, power, ECC, context control, instruction-cache base, and VMID/preemption status.
- `gc_cppdec2`, base address `0xc600`, scheduler doorbell controls, CP EDC counters, DSM controls, graphics MQD base/status, UTCL1 status, soft reset, and CPC graphics control registers.
- `gc_cpphqddec`, base address `0xc800`, HQD/HPD queue registers for active state, VMID, persistent state, queue priority, PQ/IB/EOP bases and pointers, doorbells, dequeue/offload, semaphores, atomic preops, scheduler/status, context-save state, and AQL/PQ write pointers.
- `gc_didtdec`, base address `0xca00`, GC-level DIDT control/status registers.
- `gc_ea_gceadec`, base address `0xa800`, GCEA clock, status, configuration, protection, debug, error, address-normalization, address-decode, IO/DRAM priority, latency, and performance counter configuration registers.
- `gc_ea_gceadec2`, base address `0x9c00`, GCEA result control, EDC, DSM, TCC/XBR credits, probe, error, DRAM bank arbitration, and address-decoder selection registers.
- `gc_ea_pwrdec`, base address `0x3c000`, GCEA clock-gating/timing control.
- `gc_gccacdec`, base address `0xca10`, graphics clock/power accounting, CAC, DIDT, EDC, throttle, and power-break registers.
- `gc_gdsdec`, base address `0x9700`, GDS performance counter selection and readout registers.
- `gc_gdspdec`, base address `0xcc00`, GDS/GWS/OA VMID partitioning, resets, compute limits, enhancement, context-switch status, and many shader-stage context-switch counters.
- The beginning of `gc_gfxdec0`, base address `0x28000`, covering depth buffer, scissor, viewport, clip, shader input, SPI/SX/CB blend, VGT, PA, DB, AA sample, binner, NGG, and the first `CB_COLOR0` registers before the chunk stops at `regCB_COLOR0_ATTRIB2`.

The chunk contains 2,397 preprocessor `#define`s. Of these, 1,130 are `_BASE_IDX` companion constants. It is a generated hardware register-address map only: it has no C functions, types, variables, executable logic, or software storage.

## Purpose

The purpose of this header section is to give AMDGPU and KFD code symbolic names for GC 9.4.2 hardware register offsets. The generated convention separates register address metadata from register field metadata:

- `reg*` constants name MMIO registers within a named address block.
- `reg*_BASE_IDX` constants select the SOC15 base aperture used by AMDGPU register helpers. In this chunk CP, HQD, GCEA, GC CAC, GDS, and GDSP blocks mostly use base index `0`; the initial graphics context block `gc_gfxdec0` and the GCEA power register use base index `1`.
- `ix*` constants name indirect-index registers, such as DIDT/CAC/SQ windows, that are generally accessed through an index/data path rather than as ordinary direct MMIO offsets.

Driver code combines these names with helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, indexed-register helpers, and field macros from the sibling `gc_9_4_2_sh_mask.h`. This file supplies the register number and base index; the mask header supplies bit placement; default headers supply reset/default values where generated.

## Important Macro Families

### DIDT, EDC, PCC, and CAC

The first `didtind` block exposes a regular sequence of dynamic inductive droop throttling and error-detection controls for the shader queue (`SQ`), depth block (`DB`), texture/data blocks (`TD`, `TCP`), and DBR-related counters. Each unit has control, stall, tuning, auto-release, stall-pattern, MPD scale factor, throttle counter/status, weight, EDC control, threshold/status, overflow, and rolling power delta registers. The block also exposes aggregate stall event and PCC performance counters.

Later `gc_didtdec` and `gc_gccacdec` registers provide direct GC-level controls for DIDT, CAC aggregation, EDC performance counters, PCC/power-break performance counters, throttle controls, thresholds, overflow, and rolling power data. These are power-management and protection integration points rather than ordinary rendering state.

### Command Processor Decoder and Public CP Registers

`gc_cpdec` starts with CP front-end diagnostics: CPC/CPF status, busy, stalled status, free counts, scratch index/data, MEC control, header dumps, CE/DE counters, instruction pointers, and global command processor status. It then maps queue/ring state, including ROQ/STQ/MEQ thresholds, availability, command index/data, ring-buffer read pointers, write-pointer delay/poll control, queue statistics, CE queue availability, and privilege violation address.

`gc_cppdec` maps the public/control side of the command processor. It includes ring-buffer base/control/read-pointer/write-pointer registers for rings 0 through 2 and aliases such as `regCP_RB_BASE`/`regCP_RB0_BASE`. It also defines CP interrupt controls/status, doorbell range/control, MEC doorbell range, UTCL1 error registers, fatal error state, ring VMID state, ring priority counters, power and memory sleep controls, ECC first-occurrence registers, per-pipe interrupt control/status for MEC ME1/ME2, microprogram counter start addresses, interrupt routine starts, context control, instruction-cache base/control, VMID reset/preempt/status, and PQ status.

`gc_cppdec2` extends this with scheduler doorbell controls for scheduler slots 0 through 7, CP EDC counters and DSM controls, graphics MQD base address/control, RB status, UTCL1 status, CP soft reset, and CPC graphics control.

### HQD and Queue State

`gc_cpphqddec` describes the hardware queue descriptor path. It defines HQD graphics control/status, HPD ROQ/status/UTCL1 state, MQD base addresses, active/VMID/persistent state, pipe and queue priority, quantum, packet queue base/high, read-pointer/report/write-pointer-poll addresses, doorbell control, PQ control, IB base/read/control, timers, dequeue request, DMA offload/offload aliases, semaphore command, message type, atomic pre-operation registers, HQ scheduler/control/status registers, EOP base/control/read/write/events, context-save base/control/size/offset state, GDS resource state, HQD error, AQL control, and PQ write pointers.

These offsets are central to compute queue bring-up and teardown. KFD and MES/MEC paths rely on matching HQD register numbers when programming queue descriptors, doorbells, AQL state, and context-save state.

### GCEA Addressing, Priority, and Performance

`gc_ea_gceadec` and `gc_ea_gceadec2` map graphics client external access/state. The first block includes clock control, status, protection fault, host/DRAM/GMI/IO access control, ROM, debug, MSI debug, error status, credit and urgent flow control, pipe-to-granularity maps, address normalization base/limit/offset registers, DRAM/GMI hole controls, non-power-of-two channel configuration, bank/address decode configuration, harvested channel enables, and repeated address decode tables for several decoders and chip-select groups.

The same block also maps DRAM and IO priority controls: client-to-group maps, combine flushes, burst controls, priority aging, queuing, fixed priority, urgency, urgency masking, and priority quantum registers. It ends with latency sampling and performance counter low/high/config registers. The second block supplies performance counter result control, EDC counters, DSM controls, TCC/XBR credit/max-burst registers, probe control/map, error status, DRAM bank arbitration, address decoder selection, and another EDC counter.

These registers influence memory routing, arbitration, diagnostics, and performance measurement. They must match ASIC topology and memory fabric setup.

### GDS, GWS, OA, and Context-Switch Counters

`gc_gdsdec` contains GDS performance counter select and readout offsets. `gc_gdspdec` contains the partitioned GDS register surface: generic GDS/GWS/OA control/status, per-VMID GDS base and size registers for VMIDs 0-15, per-VMID GWS and OA allocations, reset masks and reset commands, compute maximum wave ID, enhancement/restoration controls, compute and graphics context-switch status, and per-stage context-switch counters for VS, PS0-PS7, and GS.

The repeated VMID and shader-stage families are configuration-sensitive. They encode per-process or per-VM resource partitioning and diagnostic counters that are consumed by queue management and debugging code.

### Graphics Context Registers

The `gc_gfxdec0` portion begins a large graphics context register block. Within this chunk it covers:

- DB render/depth/stencil control, HTILE base, depth size, bounds, clear values, Z/stencil read/write bases, and DFSM/Z/stencil info.
- PA/SC screen, window, generic, and viewport scissor registers, clip rectangles, edge rules, and hardware screen offset.
- Coherency destination bases, CB target/shader masks, viewport transforms for 16 viewports, user clip planes, near-clip and point-size state.
- SPI pixel shader input controls 0-31, VS output config, PS input enable/address, interpolation and barycentric controls, temporary ring size, and shader output format registers.
- SX downconvert/blend optimization and MRT blend optimization registers.
- CB blend control and MRT epitch registers.
- VGT draw/index/streamout/tessellation/geometry shader/primitive ID/reuse/deallocation/event-initiation registers.
- PA polygon offset, AA sample locations/masks/config, line control, conservative rasterization, binner controls, NGG mode, and the first color-buffer base/extension/attribute register.

This block is the user-visible graphics pipeline state surface that command submission and context restore paths program around draw calls.

## Control Flow and State Behavior

There is no runtime control flow in this file. All behavior is indirect: C code includes this header and compiles symbolic constants into register reads and writes.

The state represented by the constants is hardware state. Examples include CP ring buffer pointers and doorbells, HQD queue activation and packet queue pointers, MQD base addresses, GCEA address decode and priority programming, GDS per-VMID resource allocations, CAC/DIDT/EDC throttle configuration and counters, graphics pipeline render state, viewports, scissors, shader input state, blend state, and performance counter selection/results.

Some registers are durable configuration until reset or reprogramming, such as ring base/control, address decode, VMID resource allocations, viewport and blend registers. Some are status or diagnostic reads, such as busy/stalled status, instruction pointers, EDC counters, error status, context-switch counters, and performance counter results. Some are command or write-pointer style registers where write ordering matters, such as CP/HQD doorbells, dequeue requests, resets, soft reset, read/write pointers, and counter result control. The header does not encode sequencing, timeouts, privilege checks, or side effects; those rules live in the AMDGPU/KFD driver code and the hardware specification.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register layout convention and is normally included as part of a matching GC 9.4.2 register set:

- `gc_9_4_2_sh_mask.h` provides bit shifts and masks for fields within the registers named here.
- Any GC 9.4.2 default/reset header provides reset/default values for selected registers.
- AMDGPU SOC15 helpers use the `reg*` plus `reg*_BASE_IDX` constants to compute MMIO addresses from hardware IP, instance, segment, and register number.
- Indexed register helpers use `ix*` constants for indirect DIDT/CAC/SQ register windows.

Important consumers are the AMDGPU graphics and compute initialization paths, KFD queue management, command processor ring setup, MES/MEC/HQD queue programming, power/EDC/CAC/DIDT management, GDS resource partitioning, performance/debug tooling, reset handling, and command submission/context programming. The repeated aliases in this file, such as `regCP_RB0_BASE` and `regCP_RB_BASE`, allow shared code to address a default ring while still exposing per-ring variants.

The chunk is only the first part of `gc_9_4_2_offset.h`. It stops in the middle of `gc_gfxdec0` after `regCB_COLOR0_ATTRIB2`; later chunks must cover the remaining color-buffer, shader, RLC, GRBM, VM, cache, texture, and other GC 9.4.2 offsets before a complete per-file report can reconcile the entire header.

## Risks

- Register offset drift is high impact. A wrong numeric offset or base index can read or write the wrong hardware register, causing GPU hangs, lost interrupts, broken queue setup, bad rendering, or incorrect diagnostics.
- The `_BASE_IDX` value is part of the ABI. Confusing base index `0` and `1` changes the SOC15 aperture used for access even if the register number is correct.
- The file contains repeated and aliased register families. Mechanical edits can accidentally update one alias or per-ring/per-VMID/per-viewport entry while leaving its companion inconsistent.
- CP and HQD registers are sequencing-sensitive. Doorbells, write pointers, dequeue requests, MQD bases, active bits, and context-save fields must be programmed in the order expected by firmware and hardware.
- GCEA address decode, priority, and harvest-style registers are topology-sensitive. Incorrect values can route memory traffic incorrectly or expose disabled/unavailable resources.
- DIDT/CAC/EDC and power-break registers affect throttling and protection behavior. Treating them as harmless debug counters can destabilize power management or mask hardware error conditions.
- Graphics context offsets are consumed by command streams and context restore code. A single offset mismatch in DB/PA/SPI/SX/CB/VGT state can produce subtle rendering faults rather than an immediate compile failure.
- This generated header has no type safety. Consumers can pass any constant to low-level read/write helpers, so review and hardware validation must catch semantic mixups.

## Test and Validation Signals

Useful validation is mostly integration-oriented:

- Build AMDGPU and KFD code that includes the GC 9.4.2 headers; this catches missing, renamed, or syntactically invalid macros.
- Boot/probe a GC 9.4.2 ASIC or emulator and verify CP ring initialization, write pointer updates, doorbell handling, interrupts, and queue scheduling.
- Exercise compute queue creation/destruction through KFD or MES/MEC paths to validate HQD, MQD, PQ, IB, EOP, VMID, and context-save offsets.
- Run suspend/resume, GPU reset, and firmware reload tests to cover CP soft reset, VMID reset/preempt/status, UTCL1 error/status, ECC/EDC, and MQD/ring restoration paths.
- Run graphics workloads that vary depth/stencil, HTILE, scissors, viewport transforms, clip planes, PS inputs, blend modes, streamout, tessellation, geometry shader, AA sample positions, conservative rasterization, binner, and NGG state.
- Use performance/debug tests for DIDT/CAC/EDC, GDS performance counters, GCEA performance counters, and context-switch counters to verify offsets and status/result readback.
- Exercise per-VMID GDS/GWS/OA allocation and reset paths, especially VMIDs 0-15, to catch off-by-one errors in repeated register families.
- Compare generated offsets against AMD's source register database or a known-good upstream header when updating this file; hand-edited changes should be treated as suspect unless backed by hardware documentation.

### subset-b-002664: lines 2473-4919

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

### subset-b-002665: lines 4920-7410

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h lines 4920-7410

## Scope

This chunk is a generated AMDGPU GC 9.4.2 register-offset header segment. It contains C preprocessor constants only: each `reg*` macro names a GC MMIO register word offset and each matching `*_BASE_IDX` selects the SOC15 base-index slot. The final `gccacind` lines use the `ix*` naming convention for GC CAC indirect-register indexes. The matching bitfield definitions are in `gc_9_4_2_sh_mask.h`.

The source path is under the local `ceph-client` mirror, but this file is AMDGPU hardware metadata for Aldebaran/GC 9.4.2 graphics and compute blocks, not Ceph filesystem code.

## Purpose

The purpose of this slice is to provide stable symbolic offsets for low-level GC register programming, debug, RAS, compute queue setup, virtual memory, and cache/translation controls on GC 9.4.2 hardware. Driver code includes this header through `amdgpu/gfx_v9_4_2.c` and `amdgpu/amdgpu_amdkfd_aldebaran.c`, then passes these symbols to helpers such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_RLC`.

Because these constants feed table-driven register access, offset or base-index drift can compile cleanly while programming the wrong hardware register. In this chunk that is especially relevant for shader dispatch state, TCP watchpoint stride assumptions, EDC/RAS counter tables, SQ indirect access, UTCL2/VM controls, and SR-IOV PF/VF aperture registers.

## Address Blocks and Register Families

The range begins in the `gc_rlcpdec` block, whose address-block comment appears just before the chunk. These `regRLC_*` registers cover RLC interrupt/status, load balancing, microcode/GPM thread controls, clock counters, dynamic and static power-gating state, CU masks, SERDES read/write windows, SPM/GPM logging, SRM command/status and indexed control/data registers, UTCL1/prewalker controls, semaphores, CP EOF interrupts, DSM controls, and RLC EDC counters. `gfx_v9_4_2.c` directly uses `regRLC_EDC_CNT` and `regRLC_EDC_CNT2` in RAS poison/EDC tables.

`gc_rmi_rmidec` maps the render/memory-interface block: general control/status, subblock status, XBAR configuration and arbitration, UTC/UTCL1 controls, TCIW formatter controls, scoreboard control/status, clock control, and spare registers.

`gc_shdec` is the largest shader-programming window in this chunk. It defines pixel, vertex, geometry, export, hull/local, common, and compute shader state: `SPI_SHADER_PGM_*`, `SPI_SHADER_USER_DATA_*`, `COMPUTE_DISPATCH_*`, `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, `COMPUTE_PGM_*`, `COMPUTE_RESOURCE_LIMITS`, static thread-management masks for SE0..SE7, relaunch/restart registers, checksum, and `COMPUTE_USER_DATA_0..15`. `gfx_v9_4_2.c` uses several `COMPUTE_*` offsets when assembling the Aldebaran register-init IB for GPR/LDS initialization.

`gc_shsdec` contributes shader/SPI shared state: SPI debug and graphics controls, DSM and EDC counters, PS CU enable, wave-lifetime limit/status registers, load-balance counters, GDS/SX buffer sizing, active-wave counters, and trap-screen registers for debug state.

`gc_spipdec` maps SPI arbitration, work-control percentages for GFX/HP3D/CS0..CS7, graphics debug trap registers, compute queue reset, and per-CU resource reserve registers. `amdgpu_amdkfd_aldebaran.c` and `gfx_v9_4_2.c` build `SPI_GDBG_PER_VMID_CNTL` values with the paired mask header, and `gfx_v9_4_2.c` writes `SPI_GDBG_TRAP_DATA0/1`.

`gc_sqdec` covers shader-queue and SQC controls. It includes `SQ_CONFIG`, `SQC_CONFIG`, LDS and register credits, random wave priority, debug/status/cmd/timestamp registers, indirect access through `SQ_IND_INDEX` and `SQ_IND_DATA`, instruction-format decode aliases, load-balance counters, EDC/parity counters, thread-trace word aliases, buffer/image/sampler resource words, flat scratch, M0/GPR index metadata, and SQC ICACHE/DCACHE UTCL1 controls. `gfx_v9_4_2.c` reads and writes `SQ_CONFIG1`, accesses `SQ_IND_INDEX/DATA`, and uses many SQ/SQC EDC offsets in RAS tables.

`gc_tcdec`, `gc_tcpdec`, and `gc_tpdec` cover texture/cache and texture pipeline registers. `gc_tcdec` includes TCP invalidation/status/channel steering/address config, L1/L2 cache policy registers, TCI/TCC/TCA/TCX controls, soft reset, writeback/invalidate, DSM, and EDC counters. `gfx_v9_4_2.c` applies per-die golden settings to `TCP_CHAN_STEER_0..5`, uses `TCP_EDC_CNT_NEW`, `TCC_EDC_CNT`, `TCC_EDC_CNT2`, `TCA_EDC_CNT`, `TCX_EDC_CNT`, and `TCX_EDC_CNT2` in RAS tables. `gc_tcpdec` defines four TCP watchpoint high/low/control triplets plus GATCL1/UTCL1 controls; `amdgpu_amdkfd_aldebaran.c` depends on `regTCP_WATCH1_ADDR_H - regTCP_WATCH0_ADDR_H` as the watchpoint stride. `gc_tpdec` exposes TD status, scratch, DSM, and EDC registers; `gfx_v9_4_2.c` uses `TD_EDC_CNT`.

The UTCL2 and VM blocks map GPU address translation. `gc_utcl2_atcl2dec` and its performance-counter subblocks define ATC L2 control/cache data/status, DSM index/control registers for 2M/32K/4K caches, performance counter configuration, and high/low result registers. `gc_utcl2_l2tlbdec` and its counter blocks expose L2 TLB status, GPUVA/VMID translation-assist request/response, and performance counters. `gfx_v9_4_2.c` lists the ATC L2 DSM index/control offsets in its UTC RAS block descriptors.

`gc_utcl2_vml2pfdec`, `gc_utcl2_vml2pldec`, `gc_utcl2_vml2prdec`, and `gc_utcl2_vml2vcdec` define VM L2 controls, status, dummy-page fault handling, protection-fault status/default address, invalidate request/ack/status, context TLB control, walker controls/status, MMU control, per-context `VM_CONTEXT0..15_*` controls, page-table start/end/base registers, protection-fault default addresses, per-context performance counters, and VMID/PASID mapping. These offsets integrate with the broader `gmc_v9_0.c` VM setup and KFD VMID/PASID programming paths for GC 9.4.2.

`gc_utcl2_vmsharedhvdec`, `gc_utcl2_vmsharedpfdec`, and `gc_utcl2_vmsharedvcdec` map shared VM aperture state. The hypervisor block includes per-VF framebuffer size offsets, MARC base/relocation/length windows, per-VF PCIe ATS controls, active function ID, and XGMI GPUIOV enable. The PF and VC shared blocks provide framebuffer offsets/location, default system aperture addresses, steering, virtual reset request, memory power, cacheable DRAM and local HBM windows, XGMI LFB controls, host mapping, AGP windows, and L1 TLB control.

The chunk ends at the beginning of `gccacind`, an indirect GC current/activity counter register block. The visible `ixGC_CAC_*` macros cover CAC control, override select/value, and early weight registers for BCI, CB, CP, DB, GDS, IA, LDS, PA, and PC. Other CAC indirect registers continue after this chunk.

## Important APIs, Types, and Functions

This header defines no functions, structs, enums, or runtime storage. Its exported API is the generated macro namespace:

- `reg<REGISTER>` is the word offset consumed by SOC15 GC register helpers.
- `reg<REGISTER>_BASE_IDX` selects the hardware base slot. Most blocks in this chunk use base index `0`; the opening RLC block uses base index `1`; the generated VM hypervisor block also uses base index `1`.
- `ix<REGISTER>` is an indirect-register index, not a direct MMIO offset. In this range that applies to the visible `GC_CAC` registers.
- Address-block comments such as `gc_shdec`, `gc_sqdec`, and `gc_utcl2_vml2vcdec` document the generator's hardware grouping and base address.

The paired `gc_9_4_2_sh_mask.h` file supplies field shifts and masks. Consumers combine the offset macros here with mask helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`.

## Control Flow

There is no executable control flow in this file. Runtime sequencing is implemented by consumers:

1. GC 9.4.2 device setup includes the offset and mask headers.
2. Initialization code programs golden registers, including TCP channel steering and TCI controls.
3. Compute/GPR/LDS initialization code builds indirect buffers containing `COMPUTE_*` register writes.
4. KFD debug paths build SPI debug/trap register values, program TCP watchpoint address/control registers, and use inherited GFX v9 queue, VMID, and wave-control helpers.
5. RAS code uses RLC, SPI, SQC, SQ, TCP, TCC, TCA, TCX, and TD EDC counters to query and clear error counts.
6. GMC/KFD VM paths program VM context, PASID/VMID, protection fault, invalidate, and shared aperture registers through the same generated offsets.

The header does not encode ordering, locking, reset behavior, or access type. Consumers still need to hold the correct SRBM/GRBM selection locks, choose the right VMID/context, and follow hardware-defined write, poll, invalidate, clear, and indirect-access sequences.

## State and Persistence Behavior

The macros are compile-time constants and hold no software state. The described hardware registers are volatile GPU state with several persistence categories:

- RLC, SPI, SQ, TCP, TCC, TCA, TCX, TD, UTCL2, and VM registers retain programmed hardware state until reset, power transition, firmware action, or another driver write changes them.
- Shader and compute registers represent per-dispatch or per-queue execution state. Bad offsets can break program address, resource limits, static CU masks, relaunch/restart, or user-data programming until the queue/context is rebuilt.
- VM context and aperture registers define GPU address translation and fault behavior. Incorrect values can persist as invalid page-table ranges, wrong PASID/VMID ownership, broken XNACK/ATS behavior, or bad PF/VF aperture setup.
- EDC, status, performance-counter, protection-fault, thread-trace, and trap registers are diagnostic latches or counters. Some are sticky or clear-on-write according to hardware rules not visible in the offset header.
- CAC `ix*` entries are indirect-indexed hardware state; using them as direct MMIO addresses would be incorrect.

## Dependencies and Integration Points

This chunk depends on the generated AMDGPU register ecosystem: `gc_9_4_2_sh_mask.h` for field layout, SOC15 register-offset tables, GC IP discovery identifying `IP_VERSION(9, 4, 2)`, and the GFX/KFD/GMC code that selects Aldebaran-specific paths.

Direct include users in this tree are `amdgpu/gfx_v9_4_2.c` and `amdgpu/amdgpu_amdkfd_aldebaran.c`. Broader integration includes:

- `gfx_v9_4_2.c` golden-register programming, SQ setup, debug trap setup, GC CAC indirect writes, EDC/RAS counter metadata, UTC RAS block descriptors, and SQ timeout/indirect access.
- `amdgpu_amdkfd_aldebaran.c` KFD debug trap setup and TCP address-watch programming.
- Shared GFX v9 KFD helpers for shader memory settings, VMID/PASID mapping, HQD loading/dumping/destroy, wave control, trap handler programming, and queue reset.
- `gmc_v9_0.c` and related GMC/VM code for VM context, protection fault, invalidation, aperture, XGMI, ATS, and SR-IOV handling on GC 9.4.2-class devices.
- Firmware-mediated paths for RLC, MEC/MES-style queue handling, power management, and SR-IOV/GPUIOV ownership.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong offset or base index can silently target another GC register while preserving a valid C symbol.
- This chunk starts in the middle of `gc_rlcpdec` and ends in the early `gccacind` block, so the final per-file report must merge neighboring chunks for complete block coverage.
- Direct `reg*` offsets and indirect `ix*` indexes have different access paths. Mixing them can corrupt CAC programming.
- TCP watchpoint code assumes contiguous register spacing derived from `regTCP_WATCH1_ADDR_H - regTCP_WATCH0_ADDR_H`; register reordering would break watch slots even if individual macro names remain present.
- `*_BASE_IDX` values are part of the ABI with `adev->reg_offset`. Copying an offset with the wrong base index can hit a different aperture or fail on multi-die/SR-IOV hardware.
- VM and shared aperture registers are high impact. Wrong context, PF/VF, MARC, ATS, XGMI, AGP, HBM, or system-aperture offsets can cause faults, memory isolation failures, or device reset loops.
- EDC/RAS counters require correct instance counts, clear semantics, and block mapping. A wrong register can under-report poison events or clear unrelated diagnostic state.
- Debug/trap, SQ indirect, and thread-trace aliases include many same-address decode views. Consumers must know whether a register is a command, status, data, alias, or formatted trace word before reading or writing.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU with GC 9.4.2/Aldebaran and KFD enabled so generated symbols are checked in `gfx_v9_4_2.c`, `amdgpu_amdkfd_aldebaran.c`, shared GFX v9 KFD helpers, and GMC v9 code.
- Mechanically compare this line range against the authoritative generated GC 9.4.2 register database and the paired `gc_9_4_2_sh_mask.h`.
- Boot or emulate on Aldebaran-class hardware and verify golden TCP channel-steering values, SQ init, GPR/LDS init IB submission, debug trap configuration, and TCP address watchpoints.
- Exercise compute queue creation, dispatch, preemption/reset, VMID/PASID mapping, shader memory setup, and wave-control/debug workflows through KFD.
- Run VM stress with page faults, XNACK/ATS paths, SR-IOV PF/VF aperture setup, XGMI peer mappings, invalidate requests, and protection-fault reporting.
- Run RAS/EDC diagnostics for RLC, SPI, SQC, SQ, TCP, TCC, TCA, TCX, and TD counters; verify counts, clear behavior, and block labels match hardware.
- Inspect register dumps before and after reset, suspend/resume, queue teardown, VM context teardown, and RAS counter clearing to catch persistent bad state or wrong-address writes.

### subset-b-002666: lines 7411-7687

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h lines 7411-7687

## Purpose

This chunk is the tail of the generated GC 9.4.2 register-offset header. It defines symbolic offsets for three indirect register address spaces and then closes the include guard:

- `gccacind`: graphics-core CAC/LCAC weighting, accumulator, override, throttling-pattern, and fixed-pattern performance-counter offsets.
- `secacind`: shader-engine CAC control/override offsets.
- `sqind`: shader-queue debug, wave-state, trap/status, temporary register, execution-mask, and SQ interrupt-word offsets.

The definitions are compile-time constants only. They let AMDGPU and KFD code address GC 9.4.2 hardware registers through named macros instead of hard-coded numeric indices. In this generated header, the `ix*` prefix marks indexed/indirect register offsets rather than ordinary memory-mapped `reg*` offsets. Earlier in the same source file, the real MMIO index/data ports are defined as `regGC_CAC_IND_INDEX`, `regGC_CAC_IND_DATA`, `regSE_CAC_IND_INDEX`, `regSE_CAC_IND_DATA`, `regSQ_IND_INDEX`, and `regSQ_IND_DATA`; this chunk supplies the values written into those index ports.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or callable APIs in this chunk. The API surface is the set of preprocessor names exported to AMDGPU/KFD code and sibling generated headers:

- `ixGC_CAC_WEIGHT_*` maps CAC contribution weights for many GC blocks: `SC`, `SPI`, `SQ`, `SX`, `SXRB`, `TA`, `TCC`, `TCP`, `TD`, `VGT`, `WD`, `CU`, `EA`, `RMI`, `UTCL2_ATCL2`, `UTCL2_ROUTER`, `UTCL2_VML2`, and `UTCL2_WALKER`.
- `ixGC_CAC_ACC_*` maps CAC accumulator readouts for the same broad set of blocks, including split lower/upper SQ accumulators (`ixGC_CAC_ACC_SQ0_LOWER` through `ixGC_CAC_ACC_SQ8_UPPER`) and per-CU accumulators (`ixGC_CAC_ACC_CU0` through `ixGC_CAC_ACC_CU13`).
- `ixGC_CAC_OVRD_*` maps per-block CAC override selectors for BCI, CB, CP, DB, GDS, IA, LDS, PA, PC, SC, SPI, CU, SQ, SX, SXRB, TA, TCC, TCP, TD, VGT, WD, EA, RMI, and UTCL2 subblocks.
- `ixEDC_STALL_PATTERN_*`, `ixPCC_STALL_PATTERN_*`, `ixPCC_THROT_*`, `ixPWRBRK_STALL_PATTERN_*`, and `ixPCC_PWRBRK_HYSTERESIS_CTRL` expose power/throttling pattern registers in the same GC CAC indirect space.
- `ixFIXED_PATTERN_PERF_COUNTER_CTRL` and `ixFIXED_PATTERN_PERF_COUNTER_1` through `_10` expose fixed-pattern performance-counter control and count slots.
- `ixSE_CAC_CNTL`, `ixSE_CAC_OVR_SEL`, and `ixSE_CAC_OVR_VAL` are the minimal shader-engine CAC indirect register set.
- `ixSQ_*` names expose SQ-local debug and wave registers: `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_INST_DW0`, `ixSQ_WAVE_INST_DW1`, `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_FLUSH_IB`, `ixSQ_WAVE_TTMP*`, `ixSQ_WAVE_M0`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI`.
- `ixSQ_INTERRUPT_WORD_AUTO_CTXID`, `_AUTO_HI`, `_AUTO_LO`, `_CMN_CTXID`, `_CMN_HI`, `_WAVE_CTXID`, `_WAVE_HI`, and `_WAVE_LO` are all aliases for offset `0x20c0`; the companion mask header gives different field interpretations for the same interrupt payload.

The companion `gc_9_4_2_sh_mask.h` provides the field contract. For the CAC and CAC-index data ports, the masks are mostly full-width 32-bit data fields. For SQ wave state, the masks describe decoded wave status (`VALID`, `HALT`, `TRAP`, `ECC_ERR`, `EXECZ`, `VCCZ`, etc.), hardware identity (`WAVE_ID`, `SIMD_ID`, `CU_ID`, `SH_ID`, `SE_ID`, `VM_ID`, `QUEUE_ID`), allocation fields, instruction-buffer counters, program-counter halves, `TTMP` data, `M0`, and `EXEC` halves. The interrupt-word masks define the GC 9 encoded SQ interrupt payload used by KFD.

## Control Flow

This header has no runtime control flow. The runtime access pattern is created by call sites that combine these offsets with index/data register helpers.

For SQ wave inspection, local AMDGPU call sites show the intended flow clearly. In `amdgpu/gfx_v9_0.c`, `wave_read_ind()` writes `mmSQ_IND_INDEX` with selected `WAVE_ID`, `SIMD_ID`, the supplied `ixSQ_WAVE_*` address, and `SQ_IND_INDEX__FORCE_READ_MASK`, then reads `mmSQ_IND_DATA`. `gfx_v9_0_read_wave_data()` calls that helper for `ixSQ_WAVE_STATUS`, `PC_LO`, `PC_HI`, `EXEC_LO`, `EXEC_HI`, `HW_ID`, instruction words, allocation registers, trap status, IB status/debug, `M0`, and wave mode. `amdgpu/gfx_v9_4_3.c` uses the same pattern with `GET_INST(GC, xcc_id)` and `regSQ_IND_INDEX`/`regSQ_IND_DATA` for multi-XCC hardware.

For SQ interrupts, `amdkfd/kfd_int_process_v9.c` decodes interrupt-ring `context_id0/context_id1` with `SQ_INTERRUPT_WORD_*` field masks. The code first extracts the `ENCODING` field, then treats the payload as `AUTO`, `INST`, or `ERROR`; wave-encoded interrupts are further decoded into SE, shader array, privilege, wave, SIMD, CU, and data fields. The offset aliases in this chunk describe the hardware source register for those payload shapes, while the non-generated KFD path usually works with the captured IH context words.

For GC CAC and SE CAC, the expected flow is analogous to SQ indirect access: code writes a `ixGC_CAC_*` or `ixSE_CAC_*` offset to the relevant CAC index register and reads or writes the matching data register. Earlier offsets in the same header expose those index/data MMIO ports; this chunk defines the tail of the CAC table that callers select through them.

## State And Persistence Behavior

The macros themselves are stateless and disappear after preprocessing. The named hardware registers are stateful:

- CAC weight and override registers configure how hardware estimates or overrides per-block graphics-core power/current contribution. These values can persist in hardware until reset, power-gating, firmware reinitialization, or explicit driver/SMU programming.
- CAC accumulator registers are telemetry/state readouts. They are volatile hardware counters or accumulated values whose meaning depends on CAC enablement, snapshot, and reset behavior outside this chunk.
- EDC/PCC/PWRBRK stall-pattern and hysteresis registers influence hardware throttling behavior. Writes can change throttling response and must be coordinated with power-management policy.
- Fixed-pattern performance counters are hardware telemetry slots controlled by `ixFIXED_PATTERN_PERF_COUNTER_CTRL`.
- SQ wave registers describe live shader wave execution state. They are only meaningful while a selected wave/SIMD exists and may change as the GPU runs. Debug reads must select the intended wave and handle idle/invalid states.
- `ixSQ_WAVE_FLUSH_IB` is a control-style SQ indirect register; using it can alter instruction-buffer state rather than just observe it.
- SQ interrupt-word registers and IH context payloads are transient event state. KFD consumes captured values from the interrupt handler rather than persisting them.

No software persistence, file storage, or cached kernel object is implemented by this header.

## Dependencies

This chunk depends on the generated GC 9.4.2 register set remaining synchronized with AMD's ASIC specification. Important local dependencies are:

- `gc_9_4_2_offset.h` earlier sections, which define the ordinary MMIO index/data ports used to reach these indirect offsets.
- `gc_9_4_2_sh_mask.h`, which defines fields and masks for the register names in this chunk.
- SOC15 access helpers such as `RREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_RLC_SHADOW_EX`.
- GFX9/GFX9.4 AMDGPU debug paths that read wave state through `SQ_IND_INDEX`/`SQ_IND_DATA`.
- KFD GC 9 interrupt-processing code that decodes `SQ_INTERRUPT_WORD_*` payload fields.
- Power-management and firmware policy code that may own CAC, PCC, PWRBRK, EDC, and fixed-pattern performance-counter programming.

The offsets are generation-specific. Similar macro names exist in GC 9.0, GC 9.4.3, GC 10.x, GC 11.x, and GC 12.x headers, but the numeric indices and available wave registers differ. For example, GC 10+ wave register tables introduce additional `HW_ID1/HW_ID2`, scratch, and scheduling registers, and GC 12 interrupt decoding uses a wider/two-word layout. Code must include the correct ASIC header for the selected IP block.

## Integration Points

The main integration points are generated AMD register include consumers:

- AMDGPU GFX debug and devcoredump paths call `wave_read_ind()` and `wave_read_regs()` with `ixSQ_WAVE_*` offsets to collect live wave state.
- KFD interrupt processing decodes SQ interrupt context words with the matching `SQ_INTERRUPT_WORD_*` masks, which correspond to the `0x20c0` SQ interrupt-word aliases in this chunk.
- Power-management, SMU, and diagnostic tooling can select `ixGC_CAC_*` and `ixSE_CAC_*` offsets through CAC indirect index/data ports to program CAC weights/overrides or read accumulator/performance-counter telemetry.
- Hardware validation or bring-up code can compare offset definitions in this file with `gc_9_4_2_sh_mask.h` field definitions and with sibling GC generation headers.

Because this is a header-only metadata fragment, all integration is compile-time inclusion plus runtime register access by other modules.

## Risks

- A wrong `ix` offset silently targets the wrong indirect register. For CAC/PCC/PWRBRK registers, that can misprogram throttling or power estimation; for SQ registers, it can produce misleading wave dumps or disturb debug state.
- `gccacind`, `secacind`, and `sqind` use separate index/data mechanisms. Reusing a macro with the wrong index port can read meaningless data or affect unrelated hardware.
- Several registers are control/override registers, not passive telemetry. Writes to `ixGC_CAC_OVRD_*`, `ixSE_CAC_OVR_*`, `ixPWRBRK_*`, or `ixSQ_WAVE_FLUSH_IB` can change hardware behavior.
- SQ wave reads are inherently racy with GPU execution. A wave may advance, terminate, trap, or be rescheduled between selecting the index and reading the data.
- The `ixSQ_INTERRUPT_WORD_*` names alias the same `0x20c0` offset with multiple semantic views. Consumers must choose the field layout according to the `ENCODING` bits, as KFD does.
- Cross-generation copy/paste is unsafe. The macro names look stable, but GC 9.4.2 offsets and field widths are not a universal contract across AMD GPU IP generations.
- Manual edits to generated register headers can desynchronize offset and mask headers, creating compile-time success with runtime register corruption.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware-facing:

- Build AMDGPU/KFD configurations that include GC 9.4.2 generated headers and exercise GFX9-era debug and KFD interrupt code.
- Static checks that every `ixSQ_WAVE_*` and `ixSQ_INTERRUPT_WORD_*` offset used by GFX/KFD has a matching field definition in `gc_9_4_2_sh_mask.h`.
- Static checks that `ixGC_CAC_*` and `ixSE_CAC_*` macros are only used with the corresponding CAC index/data ports, and `ixSQ_*` macros only with SQ indirect access.
- Runtime wave-dump smoke tests on supported GC 9.x hardware: selected waves should return plausible `STATUS`, `PC`, `EXEC`, `HW_ID`, allocation, trap, and instruction-buffer values without invalid register access faults.
- KFD SQ interrupt tests should show correct decoding of automatic, instruction, and error encodings, including SE/wave/SIMD/CU fields.
- Power-management regression tests should verify that CAC/PCC/PWRBRK programming still applies expected throttling policy and that accumulator/performance-counter reads behave as 32-bit volatile telemetry.
- Header consistency checks should compare this chunk against adjacent generated GC 9.4.2 mask definitions and sibling GC 9.x offset tables to catch missing aliases or accidental numeric drift.
