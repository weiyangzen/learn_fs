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
