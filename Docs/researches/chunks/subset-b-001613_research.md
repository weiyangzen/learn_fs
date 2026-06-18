# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 7155-9821

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 2.0.0 register shift/mask header. It is not executable C; it exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for display-controller MMIO fields. These macros are paired with register addresses from `dcn_2_0_0_offset.h` and consumed by AMD display helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI`.

The range starts inside the `MMHUBBUB_CLOCK_CNTL` field list, covers MMHUBBUB reset/error/client-ID controls, VGAIF/MCIF counters, DC perfmon instances, the HDA/Azalia display-audio register blocks, DCHUBBUB SDPIF/return-path/arbitration/VM blocks, DCN VM request contexts 0-15, the beginning of HUBP0, and most of the first HUBPREQ0 surface/request programming block. It ends at the chunk boundary on the `HUBPREQ0_NOM_PARAMETERS_6` comment before that register's field definitions.

## Purpose

The header range describes the bit layout for DCN 2.0 display hub, memory-request, VM, audio, and performance-monitor hardware. Its purpose is to let generic DCN20 code use stable logical field names while the generated register database supplies ASIC-specific bit positions and masks.

Major hardware areas covered here are:

- `MMHUBBUB_*`, `MCIF_*`, `WBIF0_*`, and `DMU_IF_*` fields for MMHUBBUB clock gating, soft reset, outstanding counters, write-combine timeout, memory power state, client unit IDs, and DMU interface error reporting.
- `DC_PERFMON4_*`, `DC_PERFMON5_*`, and `DC_PERFMON6_*` fields for performance-counter event selection, counter state, run/stop control, interrupts, counted values, high/low reads, and control selection.
- `AZF0STREAM*`, `AZF0ENDPOINT*`, `AZF0INPUTENDPOINT*`, and `AZALIA_*` fields for display HDA/Azalia stream-index/data windows, codec endpoint windows, controller clocking, audio DTO, DMA, cyclic buffer, payload capability, CRC diagnostics, memory power, codec root parameters, audio port connectivity, stream formats, power/reset state, and GTC group offsets.
- `DCHUBBUB_SDPIF_*`, `DCN_VM_*`, and local memory aperture fields for display hub access to framebuffer, AGP/system apertures, HBM/local ranges, pipe security levels, and SDPIF power status.
- `DCHUBBUB_RET_PATH_*` fields for DCC return-path configuration, memory power, and CRC capture/readback.
- `DCHUBBUB_ARB_*`, `VTG*_CONTROL`, `DCFCLK_CNTL`, timeout, timer, soft reset, performance-measurement, status, interrupt, and FMON fields for the common display hub's arbitration and timing behavior.
- `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` fields for page-table depth/block-size and per-context page table base/start/end programming, plus system/protection-fault default addresses and fault status/address fields.
- `HUBP0_*` fields for surface configuration, address/tiling layout, primary/secondary viewport dimensions, request-size calculation, HUBP control, clock gating, VM page configuration, debug DB, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ0_*` fields for pitch, VMID, surface and metadata addresses, flip control, queue behavior, frame pacing, flip interrupt status/ack/mask, current and earliest in-use addresses, request expansion modes, TTU/QoS, aperture and context0 VM defaults, L1 TLB control, blanking/destination geometry, prefetch settings, and vblank/flip/nominal request timing parameters.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent software objects in this chunk. The macro namespace is the API surface:

- `*_SHIFT` values provide the low bit number for a field.
- `*_MASK` values provide the already-positioned mask used for extraction and read/modify/write.
- Address-block comments identify generated hardware blocks such as `dce_dc_mmhubbub_vgaif_dispdec`, `dce_dc_hda_azf0controller_dispdec`, `dce_dc_dchubbub_hubbub_dispdec`, `dce_dc_dchubbub_hubbub_vmrq_if_dispdec`, `dce_dc_dcbubp0_dispdec_hubp_dispdec`, and `dce_dc_dcbubp0_dispdec_hubpreq_dispdec`.

The MMHUBBUB/MCIF macros expose low-level infrastructure controls. `MMHUBBUB_CLOCK_CNTL` gates display, VGAIF, VGA, WBIF0, and XFC clocks. `MMHUBBUB_SOFT_RESET` can reset VGA, VGAIF, WBIF0, and DMUIF. `MMHUBBUB_MEM_PWR_CNTL` and `MMHUBBUB_MEM_PWR_STATUS` describe VGA and display writeback memory power state. `MCIF_*` phase counters and write-combine controls expose memory-interface diagnostics for the VGAIF-side block.

The DC perfmon macros are repeated for perfmon instances 4, 5, and 6. Each instance has `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. These fields select events and count modes, gate counting by run-enable or hardware start/stop selectors, report active/counter state, raise or acknowledge interrupts, and expose counter values.

The Azalia/HDA macros include simple index/data windows for streams 0-15 and endpoint/input-endpoint 0-7, plus controller-wide fields. Controller fields cover clock gating, DTO module/phase, SOCCLK controls, underflow filler samples, DMA enable/response, BDL/RIRB/CORB settings, payload capability, stream arbitration, CRC controls/results, and memory power force/disable/status. Codec-root fields expose vendor/device/revision IDs, channel count, resync FIFO, supported rates/formats/power states, reset/power control, subsystem ID response, converter synchronization, audio port connectivity, and GTC group offsets.

The DCHUBBUB macros define common display hub and memory-fabric behavior. SDPIF fields program framebuffer and AGP apertures, VM physical request mode, forced IO status, local HBM ranges, per-pipe security levels, and memory power. Return-path fields carry DCC configuration for up to twelve slices/pipes, CRC enable/mode/mask/region controls, and CRC readbacks. Arbiter fields expose outstanding-request limits, saturation levels, QoS forcing, DRAM state counters, watermarks A-D for data urgency, PTE/meta urgency, self-refresh entry/exit, DRAM clock changes, watermark-change request/done status, timeout enabling, global timers, VTG enable/field/status, DCHUBBUB reset, clock control, DCF clock deep-sleep, performance measurements, vline snapshots, timeout detection, timeout interrupts, indexed debug access, and FMON measurements.

The `DCN_VM_CONTEXT<n>` macros are a generated set for VM request contexts 0-15. Each context has a control register with page-table depth and block size, plus high/low page-table base, start, and end address fields. The shared VM fields include default system/protection-fault addresses, fault control bits for dummy page handling and retry/default behavior, fault status bits for invalid/PDE/PTE/read/write/faulted context, and fault address capture.

The `HUBP0_*` macros describe the first hub pipe's surface-facing programming. Important fields include surface type, alternate metadata usage, surface array mode, pipe/number-of-banks/bank-width/bank-height/tile-split/meta layout, viewport x/y/width/height for luma/chroma and primary/secondary planes, chunk/min-chunk/meta/PTE-group request sizing for luma and chroma, hubp enable/blanks/underflow/urgent state, deadlock detection, clock gating, VMPG enable, debug DB, and DCFCLK/DPPCLK measurement windows.

The `HUBPREQ0_*` macros describe the first hub pre-request generator. Surface-address fields cover primary/secondary luma/chroma and metadata addresses, high address words, current in-use address readbacks, and earliest-in-use readbacks. `DCSURF_SURFACE_CONTROL`, `DCSURF_FLIP_CONTROL`, `DCSURF_FLIP_CONTROL2`, `DCSURF_QUEUE_CONTROL`, `FRAME_PACING_TIME`, and `SURFACE_FLIP_INTERRUPT` define flip timing, swap locking, immediate/near/immediate-disable behavior, queue depth, pacing, interrupt status, interrupt type, ack, and masks. TTU/QoS and timing fields include expansion mode, TTU watermarks, fixed QoS and ramp disable for surfaces and cursors, VM aperture defaults, context0 fault/default/page-table fields, L1 TLB control, blank offsets, destination dimensions, after-scaler coordinates, prefetch ratios, vblank parameters, flip parameters, and nominal PTE/meta request timing through `HUBPREQ0_NOM_PARAMETERS_5`.

## Control Flow

This header has no runtime control flow. Runtime behavior appears only in consumers that combine these generated fields with register addresses and MMIO helper functions.

A typical control sequence is:

1. A DCN20 resource, DMUB, IRQ, VMID, hubbub, HUBP, IPP, audio, or GMC file includes `dcn_2_0_0_offset.h` and this shift/mask header.
2. Register tables are built with macros such as `SRI(...)`, `SF(...)`, `HWS_SF(...)`, `FD_MASK(...)`, and `FD_SHIFT(...)`.
3. Driver code calls helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_WAIT`, `RREG32_SOC15`, or `REG_GET_FIELD`.
4. The helpers use these generated shifts and masks to extract a field, clear a field, or insert a new field value in a read/modify/write sequence.
5. Hardware then performs the real state transition: reset, clock gate, VM translation, page fault capture, surface flip, request scheduling, watermark change, audio DMA update, CRC capture, or perf counter update.

Control-sensitive flows represented by this chunk include DMUB reset through `MMHUBBUB_SOFT_RESET__DMUIF_SOFT_RESET`, framebuffer base/offset discovery through `DCN_VM_FB_LOCATION_BASE` and `DCN_VM_FB_OFFSET`, VMID page-table setup through `DCN_VM_CONTEXT0_*` field aliases, HUBPREQ flip interrupt/ack handling through `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT`, hubbub soft reset and arbitration/watermark programming, HDA/Azalia audio clock/DMA setup, DCHUBBUB CRC capture, timeout detection, and display writeback/MMHUBBUB memory power management.

The macros do not encode ordering constraints. Callers must still know when a field is read-only, write-one-to-clear, self-clearing, sticky, double-buffered, safe only during blank, safe only while disabled, or owned by firmware.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware register state that persists according to DCN/MMIO semantics until rewritten, reset, power-gated, or changed by hardware/firmware.

State represented in this chunk includes:

- MMHUBBUB and MCIF state: clock gate disables, soft resets, memory power force/disable/status, outstanding-request counters, write-combine timeout, DMU read outstanding error and clear bits, and client unit IDs.
- Performance-monitor state: selected events, count modes, run-enable and start/stop selectors, active state, interrupt enable/status/ack bits, high/low counter values, and count-off behavior.
- Audio/HDA state: stream index/data ports, endpoint command windows, controller clocking and DTO, DMA enable/status, cyclic buffer position, payload capabilities, arbitration policy, CRC settings/results, Azalia memory power, codec identity/capability/power/reset registers, and port connectivity.
- DCHUBBUB state: framebuffer/aperture address windows, HBM/local-memory ranges, security levels, return-path DCC configuration, CRC windows/results, arbitration watermarks, DRAM/self-refresh/clock-change controls, timeout and interrupt status, global timer/VTG state, clock/DCFCLK controls, and performance measurement readbacks.
- VM state: per-context page-table base/start/end ranges for contexts 0-15, context depth/block-size, default addresses for system and protection-fault handling, fault enable/default behavior, fault status, faulted context, and fault address capture.
- HUBP/HUBPREQ0 state: surface format/tiling/viewport, request sizing, underflow/urgent/deadlock status, clock gating, VM page config, surface and metadata addresses, flip locks and flip timing, queue and pacing state, flip interrupt status/ack/mask, current and earliest in-use addresses, TTU/QoS policy, TLB and aperture configuration, and vblank/flip/nominal prefetch request timing.

Some fields are latched programming values, some are live status readbacks, some are counters, and some are sticky interrupt/fault bits that require explicit clear or acknowledgement. Reset, suspend/resume, runtime power management, display mode set, page flip, DMUB firmware execution, memory-controller setup, HDA audio handling, and GPU VM faults can all alter the underlying hardware state. The generated header does not document access permissions, default values, lock ordering, or volatility.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`, which provides the register addresses and base indexes. This file provides the bit positions inside those addresses.

Direct include and usage points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`, which includes the DCN 2.0 offset and mask headers, builds DMUB register field tables through `FD_MASK`/`FD_SHIFT`, reads DCN VM framebuffer base/offset fields, and toggles `MMHUBBUB_SOFT_RESET.DMUIF_SOFT_RESET` during DMUB reset/release.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`, which includes this header and uses `HUBPREQ0_DCSURF_SURFACE_PITCH.PITCH` to derive visible framebuffer pitch.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.h`, which maps `DCN_VM_CONTEXT0_*` shift/mask fields into DCN20 VMID register tables used by VM page-table setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`, which includes the header and builds IRQ register entries for DCN20 display interrupts, including HUBP/HUBPREQ flip-related sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` and `.c`, which map MMHUBBUB/MCIF writeback fields used for display writeback buffer management, watermarking, address programming, security, and memory power behavior.
- Shared DCE/DCN hardware sequencing and audio code, including `display/dc/hwss/dce/dce_hwseq.h` and `display/dc/dce/dce_audio.c`, which use DCHUBBUB, Azalia, and display-audio field families through generation-specific register tables.
- HUBP/HUBPREQ and IPP-related code, including `display/dc/dcn10/dcn10_ipp.h` and later IRQ services, which rely on the repeated `HUBPREQ0_*` field shape for cursor settings and page-flip interrupt handling across DCN generations.

Although the repository path sits under `sources/distributed-fs/ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph protocol logic, filesystem cache state, network messaging, or distributed-storage persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A generated shift or mask can be wrong while all C code still compiles, causing a read/modify/write helper to alter the wrong bit, fail to clear a sticky bit, corrupt an adjacent field, or poll a status bit that never changes.

High-risk reset and clock fields include `MMHUBBUB_SOFT_RESET`, `MMHUBBUB_CLOCK_CNTL`, `DCHUBBUB_SOFT_RESET`, `DCHUBBUB_CLOCK_CNTL`, and `DCFCLK_CNTL`. Incorrect masks here can leave display firmware, hubbub, VGAIF, writeback, or request fabric blocks stuck in reset, ungated at the wrong time, or clock-gated while active.

VM and aperture fields are especially sensitive. Incorrect masks in `DCN_VM_FB_LOCATION_BASE`, `DCN_VM_FB_OFFSET`, `DCN_VM_CONTEXT<n>_*`, `DCN_VM_FAULT_*`, `HUBPREQ0_DCN_VM_SYSTEM_APERTURE_*`, `HUBPREQ0_DC_VM_CONTEXT0_*`, or `HUBPREQ0_DCN_VM_MX_L1_TLB_CNTL` can translate display memory through the wrong page tables, hide protection faults, trigger dummy-page behavior unexpectedly, display stale/wrong memory, or break DMUB address translation.

Surface and flip fields can fail visibly. Bad constants in `HUBP0_DCSURF_*`, `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCSURF_FLIP_CONTROL*`, `HUBPREQ0_DCSURF_QUEUE_CONTROL`, or `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT` can cause black frames, corrupted tiling, wrong chroma addresses, page flips at the wrong vblank, missed flip interrupts, hung page flips, underflow, or frame-pacing errors.

Watermark, TTU, and arbitration fields affect bandwidth and power. Incorrect `DCHUBBUB_ARB_*`, `HUBPREQ0_DCN_TTU_QOS_WM`, `HUBPREQ0_DCN_GLOBAL_TTU_CNTL`, `HUBPREQ0_*_TTU_CNTL*`, vblank/flip/nominal parameter, and prefetch masks can allow self-refresh or clock changes too aggressively, block power savings, or cause underflow/flicker under memory pressure.

Audio and Azalia fields have protocol-visible risk. Errors in stream index/data, endpoint index/data, audio DTO, DMA, payload capability, CRC, codec capability, power/reset, and connectivity fields can produce missing HDMI/DP audio, wrong channel/rate advertisement, endpoint access failures, CRC diagnostic mismatches, or audio power-management regressions.

The range contains several repeated generated patterns: DC perfmon instances, Azalia streams/endpoints, DCC return-path instances, VM contexts 0-15, VTG controls, and luma/chroma surface-address families. Instance suffix mistakes are hard to catch at compile time because the macro names remain valid and structurally similar.

Chunk-boundary risk is present at both ends. The chunk begins inside the existing `MMHUBBUB_CLOCK_CNTL` register's shift/mask group and ends at the `HUBPREQ0_NOM_PARAMETERS_6` comment before that register's definitions. The final merge lane should treat those as artificial chunk boundaries, not missing source content.

## Test Signals

Useful validation signals are mostly generated-header checks plus DCN20 display behavior:

- Build coverage for DCN20 display, DMUB, GMC, VMID, IRQ, hubbub/MMHUBBUB, HUBP/HUBPREQ, and audio code that includes `dcn_2_0_0_sh_mask.h`.
- Generated-register validation that every `*_MASK` in this chunk matches its corresponding `*__SHIFT`, does not overlap unintended fields, and matches AMD's authoritative DCN 2.0.0 register database and the companion `dcn_2_0_0_offset.h`.
- DMUB boot/reset tests that exercise `MMHUBBUB_SOFT_RESET.DMUIF_SOFT_RESET`, framebuffer base/offset translation, inbox/outbox pointer reset, and firmware response handling.
- GPU memory-controller and framebuffer tests that verify `HUBPREQ0_DCSURF_SURFACE_PITCH.PITCH`, VM framebuffer base/offset, AGP/system aperture, and local/HBM address handling.
- VMID tests that program DCN VM contexts, validate page-table base/start/end ranges, trigger expected display VM faults, and confirm fault status/address fields identify invalid, PDE/PTE, read/write, and context information correctly.
- Display modeset, page-flip, and cursor stress tests that exercise HUBP0 surface config, viewport, tiling, request sizing, HUBPREQ0 address flips, flip locks, queue controls, flip interrupts, current/earliest in-use readbacks, and cursor timing.
- Bandwidth and power-management tests under high-resolution, multi-plane, cursor, writeback, and memory-clock-change workloads, watching for underflow, timeout, watermark-change, self-refresh, and TTU/QoS regressions.
- HDA/HDMI/DP audio tests that validate Azalia controller clocking, DTO, endpoint access, stream DMA state, advertised codec capabilities, channel/rate handling, hotplug audio enablement, and audio CRC diagnostics.
- DCHUBBUB CRC, performance counter, timeout, VTG, FMON, and debug-index/data diagnostics that confirm status bits, interrupt ack/clear behavior, counter values, and readback fields move as expected.

Regression symptoms from bad constants include blank display, corrupted scanout, wrong framebuffer pitch, missed page-flip completion, flip timeout, display underflow, VM faults on valid scanout buffers, failure to report VM faults, DMUB reset/load failure, bad display audio, broken suspend/resume, excessive display power, unreliable memory-clock changes, or perf/CRC/debug tools reporting impossible values.

## Cross-Chunk Notes

This is not a standalone source module; it is one chunk of a large generated DCN 2.0.0 register layout contract. Neighboring chunks own the preceding MMHUBBUB/WBIF register definitions and the continuation of `HUBPREQ0_NOM_PARAMETERS_6` plus the remaining HUBPREQ/HUBP/DCN register families. The later merge/reconciliation lane should combine the chunks into a single per-file view and avoid treating this artificial line range as a hardware boundary.
