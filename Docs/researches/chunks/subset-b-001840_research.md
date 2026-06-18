# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 17020-19538

## Scope

This chunk is part of AMDGPU Display Core Next 3.1.4 ASIC register metadata. It contains C preprocessor constants for register field shifts and masks, not executable code. The covered range starts in the global DCN VM register area and then defines display hub pipe register fields for HUBP/HUBPREQ/HUBPRET/CURSOR/perfmon instances 0 and 1, plus HUBP2 and the first portion of HUBPREQ2.

The file is paired with `dcn_3_1_4_offset.h`: offset macros identify where a register is in MMIO space, while this header gives `REG__FIELD__SHIFT` and `REG__FIELD_MASK` values used to pack and unpack individual bitfields.

## Purpose

The purpose of this chunk is to describe hardware-visible state for the DCN 3.1.4 display memory-fetch path:

- DCN VM contexts 10-15, default VM address registers, and VM fault control/status/address fields.
- HUBP surface configuration fields for pipes 0, 1, and 2, including pixel format, rotation, mirroring, tiling, viewport coordinates, request sizes, blanking behavior, clock enable/gating, virtual memory page configuration, and debug/measurement controls.
- HUBPREQ surface request fields for pipes 0, 1, and the start of 2, including surface pitch, VMID, primary/secondary luma and chroma addresses, metadata addresses, TMZ/DCC controls, flip control, flip interrupts, in-use address latches, TTU/QoS controls, VM aperture/TLB fields, destination/vblank/nominal/flip timing parameters, prefetch configuration, cursor timing settings, and request-memory power state.
- HUBPRET return-path controls for pipes 0 and 1, including detile buffer control, blank-enable flow control, detile buffer power gating, read-line controls/status, and HUBPRET interrupt status/mask/clear fields.
- Cursor 0 fields for pipes 0 and 1, including enable/mode/pitch, address, size, position, hotspot, stereo control, destination offset, memory power state, DMDATA address/control/QoS/status/software data fields.
- DC perfmon blocks 6 and 7, with event selection, counter state, active windows, manual trigger, interrupt, mode, and counter value fields.

## Important APIs, Types, and Macros

There are no functions or C types in this chunk. The exported interface is macro names consumed by DC register-helper macros:

- `*_SHIFT` constants give the field low-bit position.
- `*_MASK` constants give the field bit mask.
- Register/field naming follows `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, for example `HUBPREQ0_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING_MASK`.

Integration code commonly expands these through helper macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `HUBP_SF(...)`, `REG_SET`, `REG_UPDATE`, and related MMIO accessors. In this source tree, `dmub/src/dmub_dcn314.c` includes this header and uses `DMUB_DCN31_FIELDS()` with `FD_MASK`/`FD_SHIFT` to initialize the DMUB register field tables. `dc/irq/dcn314/irq_service_dcn314.c` also includes it alongside the matching offset header for DCN 3.1.4 IRQ register metadata. Generic HUBP resource code follows the same pattern: register lists are built with `SRI(...)`, and field mask/shift structures are built with `HUBP_MASK_SH_LIST_DCN31(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN31(_MASK)`.

## Register Groups Covered

The VM portion completes higher-numbered display VM contexts:

- `DCN_VM_CONTEXT10_*` through `DCN_VM_CONTEXT15_*` define page-table depth, block size, page-directory base address, and logical page start/end fields.
- `DCN_VM_DEFAULT_ADDR_MSB/LSB` defines default address and SPA/snoop bits.
- `DCN_VM_FAULT_CNTL` defines status-clear, status mode, interrupt enable, range-fault disable, and PRQ-fault disable bits.
- `DCN_VM_FAULT_STATUS` exposes fault status, error VMID, translation-response error VMID, table level, pipe, and interrupt status.
- `DCN_VM_FAULT_ADDR_MSB/LSB` captures the faulting address.

Each HUBP instance defines static surface interpretation:

- `DCSURF_SURFACE_CONFIG`: pixel format, rotation, horizontal mirroring, alpha plane enable.
- `DCSURF_ADDR_CONFIG` and `DCSURF_TILING_CONFIG`: pipe/interleave/compressed-fragment/packer fields plus swizzle mode, dimensionality, metadata linearity, and pipe alignment.
- Primary/secondary viewport start/dimension pairs, including chroma `_C` variants.
- `DCHUBP_REQ_SIZE_CONFIG` and `_C`: chunk dimensions, minimum chunk size, meta chunk dimensions, DPTE group sizing.
- `DCHUBP_CNTL`: hubp enable, blank enable, detile-buffer flush, underflow and mem-power status flags, stall controls, data return flags, clock-gate disable, and request-limit controls.
- `HUBP_CLK_CNTL`: clock enable/force bits and DCFCLK/DPPCLK force-on flags.
- `DCHUBP_VMPG_CONFIG`, debug registers, and DCFCLK/DPPCLK measurement-window controls.

Each HUBPREQ instance defines the dynamic fetch programming surface:

- Pitch and VMID settings.
- Primary/secondary surface address and high-address registers for luma and chroma planes.
- Primary/secondary metadata surface address and high-address registers for luma and chroma metadata.
- `DCSURF_SURFACE_CONTROL`: trusted memory zone bits, DCC enable bits, DCC independent-block fields, and equivalent chroma/metadata security bits.
- `DCSURF_FLIP_CONTROL`, `DCSURF_FLIP_CONTROL2`, and `DCSURF_SURFACE_FLIP_INTERRUPT`: update locks, flip type, pending/away status, stereo sync, pending delay/min-time, GSL, triple-buffering, interrupt masks/status, and write-one-clear style clear bits.
- Surface in-use and earliest-in-use address latches, with high address and VMID fields for luma/chroma.
- TTU/QoS controls (`DCN_TTU_QOS_WM`, `DCN_GLOBAL_TTU_CNTL`, surface/cursor TTU controls), VM DMDATA status/clear bits, VM aperture low/high address fields, and L1 TLB enable/system-access/VMID fields.
- Timing/prefetch registers: blank offsets, destination dimensions, after-scaler dimensions, vblank parameters, flip parameters, nominal parameters, per-line delivery, cursor settings, ref-frequency-to-pixel-frequency ratio, and destination Y delta request limit.
- Memory power control/status bits for light sleep, shutdown, force, and disallow status.

HUBPRET and cursor/perfmon blocks cover complementary status and instrumentation state:

- `HUBPRET*_HUBPRET_CONTROL` configures detile-buffer size, crossbar source selection, blank-enable acknowledgement, and global clocks.
- `HUBPRET*_HUBPRET_MEM_PWR_*` mirrors request-side memory power controls for detile buffers.
- `HUBPRET*_HUBPRET_READ_LINE_*` and `*_INTERRUPT` define read-line compare/control, occurrence/status/mask/clear fields, and read-line/current-vblank/flip status.
- `CURSOR0_*` registers define cursor fetch address, geometry, blending mode, stereo behavior, destination offset, memory power state, and DMDATA sideband fetch/control/status/software-write fields.
- `DC_PERFMON6_*` and `DC_PERFMON7_*` define counter event selection, increment/run modes, trigger mode, window state, region/window selection, manual triggers, interrupt control/status/clear, and 64-bit counter values split across low/high registers.

## Control Flow and State Behavior

This header has no runtime control flow. Runtime behavior is induced by display driver code that writes or reads registers using these field constants:

1. Resource initialization builds per-block register address tables from offset macros and builds shift/mask tables from this header.
2. Atomic display programming writes HUBP/HUBPREQ fields to describe framebuffer format, tiling, addresses, metadata, viewport, VMID, QoS, cursor state, and prefetch/deadline timing.
3. Page flips update surface address and flip-control fields, then hardware reports pending/occurred/in-use state through `DCSURF_FLIP_CONTROL`, `DCSURF_SURFACE_FLIP_INTERRUPT`, and in-use address registers.
4. VM faults and DMDATA faults persist in status registers until cleared through explicit clear fields.
5. Underflow, memory-power, read-line, and perfmon fields expose hardware status for diagnostics, interrupt handling, and performance measurement.

The persistence is hardware state, not kernel memory persistence. Register writes remain in the display engine until reset, power gating, mode reprogramming, or later MMIO writes alter them. Several fields are status/clear pairs, so a stale or missed clear can cause repeated interrupt/status observations.

## Dependencies and Integration Points

This chunk depends on exact DCN 3.1.4 hardware register layout. The most direct dependencies are:

- Matching register offsets from `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`.
- AMD display register access macros that combine offset, shift, and mask metadata.
- HUBP resource and implementation code under `drivers/gpu/drm/amd/display/dc/hubp/` and `drivers/gpu/drm/amd/display/dc/resource/`, which expect field names such as `DCSURF_SURFACE_PITCH`, `DCSURF_FLIP_CONTROL`, `CURSOR_CONTROL`, and `DCN_TTU_QOS_WM` to exist for each pipe instance.
- DMUB support in `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes this header to populate field arrays used by the display microcontroller service layer.
- DCN 3.1.4 IRQ service code, especially page-flip and vblank/vupdate IRQ source mapping; flip interrupt state is represented by the HUBPREQ surface flip interrupt fields in this chunk.

The instance naming is important. The chunk covers concrete prefixes (`HUBP0`, `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, `DC_PERFMON6`, then corresponding instance 1 and partial instance 2). Generic code relies on macro expansion to map logical pipe IDs to these concrete register names.

## Risks and Edge Cases

- Bitfield drift is the main risk. These generated constants must match the ASIC specification exactly; an incorrect mask or shift silently writes the wrong hardware bits.
- Instance skew is risky because fields are repeated with only prefixes changed. A typo in one instance can affect only a subset of pipes, producing display failures that depend on pipe allocation.
- Split 64-bit addresses require coordinated low/high writes and correct high-bit masks. Surface, metadata, cursor, fault, in-use, and VM page-table addresses can become invalid if high fields are truncated or paired with stale low fields.
- Security and memory-protection bits are sensitive. TMZ, VMID, VM aperture, TLB, default address, and fault-control fields affect how display fetches memory and how faults are reported or suppressed.
- Flip status fields mix control, pending, interrupt status, and clear semantics. Incorrect clear/mask usage can lose page-flip completion events or leave page flips appearing stuck.
- QoS/TTU/prefetch timing fields are performance and correctness critical. Bad values can lead to underflow, visible corruption, missed vblank deadlines, or unnecessary memory-clock pressure.
- Memory power control fields can affect wake latency and data availability if light-sleep/shutdown force or disallow bits are programmed inconsistently with active fetches.
- Perfmon fields are observational but can still perturb diagnostics if counter selection, active windows, or clear/restart bits are wrong.

## Test Signals

Useful signals for changes touching these masks are mostly integration and hardware behavior checks:

- Build coverage for AMDGPU display code with DCN 3.1.4 enabled; missing or renamed macros should fail compilation where register tables expand.
- Boot and modeset on matching hardware/APU, with multiple active pipes to exercise instance 0, 1, and 2 register names.
- Page-flip stress tests checking that page-flip IRQs arrive, pending bits clear, and no stuck `SURFACE_FLIP_PENDING` state remains.
- Cursor tests across formats, sizes, stereo/rotation/mirroring cases, and cursor movement while page flips are active.
- VM fault injection or fault telemetry checks verifying that `DCN_VM_FAULT_STATUS`, fault address, VMID, and clear behavior report expected values.
- Display underflow and DCC/TMZ test coverage for compressed/protected framebuffers.
- Power-management tests that enter/exit display memory power states while scanout, cursor, and DMDATA fetches remain correct.
- Perfmon smoke tests validating event selection, counter start/stop, interrupt/status, and high/low counter reads for perfmon blocks 6 and 7.
