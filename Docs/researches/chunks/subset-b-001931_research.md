# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 4914-7581

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice. It contains C preprocessor constants only: every exported definition in this range is a `_SHIFT` or `_MASK` macro for a hardware register field, with comments marking register names and `addressBlock` boundaries. There are no functions, structs, enums, allocations, branches, loops, syscalls, or direct MMIO accesses here.

The range starts in the tail of the MMHUBBUB/wbif warmup and power-control definitions, then covers Azalia display-audio controller/root/stream/endpoint blocks, DCHUBBUB arbitration and VM-related blocks, and the first HUBP/HUBPREQ/HUBPRET instance. It ends at the first field of `HUBPRET0_HUBPRET_READ_LINE_STATUS`; the remaining fields for that register and the following cursor/HUBP1 material are outside this chunk and must be handled by neighboring chunk research.

## Purpose And Hardware Surface

This header provides the bit-layout ABI used by AMDGPU Display Core for DCN 3.2.0 register programming. Companion generated offset headers provide register addresses; this file supplies bit positions and masks consumed by register helper macros to pack values into 32-bit MMIO writes and decode 32-bit MMIO reads.

Major hardware areas represented in this chunk:

- MMHUBBUB and WBIF tail controls: warmup base/region/VMID fields, minimum time-to-outstanding, SoC clock deep-sleep mode, writeback watermark-change control, WBIF outstanding counters, VGA split selection, memory power status/control, clock gating, soft reset, DMU interface error status, and client unit IDs.
- Azalia display-audio controller: clock gating, audio DTO phase/module and forced DTO controls, SoC clock deep-sleep exit enables, DMA snoop/isochronous behavior for data/BDL/CORB/RIRB/DP paths, underflow filler samples, cyclic buffer position/sync, payload capabilities, stream arbitration, CRC controls/results, and Azalia memory power state.
- Azalia codec root and indirection windows: codec/vendor/revision/function parameter fields, power/reset/subsystem/converter controls, GTC group offsets, DC audio port connectivity, 16 stream index/data windows, 8 output endpoint index/data windows, and 8 input endpoint index/data windows.
- DCHUBBUB arbitration and memory-system control: outstanding request thresholds, saturation, QoS force, DRAM and USR retraining controls, watermark sets A through D, fractional urgent bandwidth, watermark-change handshakes, MALL control, timeout enable, global timer, surface check addresses, VTG selection, soft reset, clocking, DCFCLK control, performance measurement, timeout detection/interrupt status, and FMON fields.
- DCHUBBUB SDPIF, return path, and VM request interface: SDPIF config/security/no-allocate settings, VM physical request fields, forced-IO status, framebuffer and AGP apertures, local HBM aperture locking, pipe security levels for data/metadata/cursor/GPUVM, request-rate limiting, memory power controls/status, CRC and DCC statistics, compbuf/DET sizing, debug controls, VM contexts 0 through 15, default address, and VM fault control/status/address fields.
- HUBP0 and HUBPREQ0 scanout programming: surface pixel format, rotation/mirroring/alpha, address and tiling configuration, primary/secondary luma/chroma viewports, request sizing, blank/reset/VTG/underflow status, HUBP clocking, VM page and MALL/SubVP controls, measurement windows, MALL status, pitches, VMID settings, primary/secondary luma/chroma surface and meta-surface addresses, flip controls/interrupts, in-use and earliest-in-use address readback, expansion mode, TTU/QoS timing, VM aperture/TLB settings, prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor timing, UCLK p-state force, and HUBPREQ status.
- HUBPRET0 return-timing fields: DET buffer/crossbar selection, HUBPRET memory power controls/status, read-line control windows, read-line interrupt mask/type/clear/status fields, and the start of read-line status readback.

## Important Definitions

The generated interface follows the standard AMD display register naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for the field.
- `// addressBlock: ...` comments identify hardware register blocks.
- `//<REGISTER>` comments group all following field macros for that register.

Important macro families in this chunk:

- `MMHUBBUB_WARMUP_*`, `MMHUBBUB_MEM_PWR_*`, `MMHUBBUB_CLOCK_CNTL`, and `MMHUBBUB_SOFT_RESET` define display memory-hub warmup addressing, VMID, clock, memory-power, reset, and error/status fields. `WBIF_SMU_WM_CONTROL` and `WBIF0_*` expose writeback watermark-change and outstanding-counter state.
- `AZALIA_*` controller macros define the display-audio transport side: DTO setup, DMA attributes, cyclic-buffer behavior, stream arbitration, payload capability, CRC control/result windows, and audio memory power control/status.
- `AZALIA_F0_CODEC_*`, `CC_RCU_DC_AUDIO_*`, and `REG_DC_AUDIO_*` macros define codec-root parameters, function controls, port connectivity, and GTC group offsets. The `AZF0STREAMn`, `AZF0ENDPOINTn`, and `AZF0INPUTENDPOINTn` index/data pairs provide repeated indirect access windows rather than unique per-field payload layouts.
- `DCHUBBUB_ARB_*` macros define memory arbitration policy and watermark programming. Watermark sets `A` through `D` carry repeated urgency, self-refresh enter/exit, UCLK/FCLK p-state change, USR retraining, trip-to-memory, and fractional bandwidth fields.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCN_VM_FB_*`, `DCN_VM_AGP_*`, and `DCN_VM_LOCAL_HBM_*` define SDPIF routing/security and aperture control fields. Pipe-level security/noalloc definitions separate data, DMDATA, DCC metadata, cursor, and GPUVM request classes.
- `DCHUBBUB_RET_PATH_*`, `DCHUBBUB_CRC_*`, `DCHUBBUB_DCC_STAT*`, `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DETn_CTRL`, `COMPBUF_MEM_PWR_CTRL_*`, and `DCHUBBUB_MEM_PWR_*` define return-path memory power, CRC capture, DCC statistics, compbuf/DET capacity, reserved space, and debug fields.
- `DCN_VM_CONTEXT0_*` through `DCN_VM_CONTEXT15_*`, `DCN_VM_DEFAULT_ADDR_*`, and `DCN_VM_FAULT_*` define VM page-table base/start/end addresses, context controls, default fault address behavior, and fault status/address readback.
- `HUBP0_DCSURF_*` and `HUBP0_DCHUBP_*` define the first hub pipe's surface format, tiling, viewport, request size, blank/reset, clock, VM page, MALL/SubVP, measurement, and status fields.
- `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCN_*`, `HUBPREQ0_PREFETCH_*`, `HUBPREQ0_VBLANK_*`, `HUBPREQ0_FLIP_*`, `HUBPREQ0_NOM_*`, and `HUBPREQ0_PER_LINE_*` define the first hub-pipe request path: surface addresses and metadata, flip/in-use tracking, VM/TLB, TTU/QoS, prefetch, vblank, flip, nominal, per-line delivery, cursor, memory power, p-state force, and status registers.
- `HUBPRET0_HUBPRET_*` defines the first hub-pipe return path: DET-buffer location, component crossbar, memory power, read-line intervals/windows, read-line interrupts, read-line value readback, and the beginning of read-line status.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when Display Core code combines these macros with generated register offsets and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `SF(...)`, and `SRI(...)`.

Typical runtime flow:

1. DCN 3.2 resource construction binds generated register offsets and these mask/shift constants into per-block register tables for hubbub, hubp, audio, IRQ, DMUB, and diagnostic code.
2. Modeset and atomic-commit paths program DCHUBBUB watermarks, compbuf/DET allocation, VM apertures, HUBP0 surface geometry, tiling, addresses, metadata, pitches, request sizes, TTU/prefetch timing, and flip controls.
3. Display-audio paths program Azalia DTO, DMA behavior, codec root controls, stream/endpoint indirect windows, and audio power/clock behavior as connectors and audio streams are enabled or disabled.
4. Interrupt, status, and diagnostics paths decode flip interrupts, timeout/fault status, CRC values, DCC statistics, performance counters, read-line/vblank state, memory power state, underflow flags, MALL status, and VM fault addresses.

The state described here is hardware register state, not persistent driver memory:

- Persistent programmed state includes warmup base/region/VMID, memory-power policies, clock-gating choices, audio DMA/DTO/codec settings, arbitration watermarks, aperture boundaries, VM context page-table ranges, compbuf/DET sizing, surface format/tiling/viewports, surface/meta addresses, TTU/prefetch/vblank/flip/nominal timing, cursor timing, MALL/SubVP policy, and HUBPRET read-line interrupt configuration.
- Volatile readback includes outstanding counters, memory power status, clock-on/busy state, CRC/DCC/performance results, forced-IO status, VM fault status/address, MALL status, surface-in-use and earliest-in-use addresses, HUBPREQ status registers, read-line value/status, underflow/no-outstanding-request status, and timeout interrupt state.
- Side-effecting fields include soft resets, fault/status clear bits, watermark-change request/ack bits, warmup software interrupt ack, flip interrupt clear/status fields, timeout interrupt clear fields, read-line interrupt clear bits, VM fault control, and p-state force enables/values.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.2.0 register header family. It is normally consumed with the matching DCN 3.2.0 offset header and Display Core register helper layer. Compile-time symbol resolution catches missing names, but wrong numeric masks or shifts can compile and only appear as runtime hardware misprogramming.

Important integration points include:

- `drivers/gpu/drm/amd/display/dc/hubbub/dcn32/`, where DCN 3.2 hubbub code programs `DCHUBBUB_ARB_*` watermarks, SDPIF controls, compbuf/DET sizes, memory power, timeout, CRC/DCC, and VM-related fields.
- `drivers/gpu/drm/amd/display/dc/hubp/` and related DCN 3.x hubp register tables, which consume `HUBP0_*`, `HUBPREQ0_*`, and `HUBPRET0_*` fields for plane surface setup, flips, VM/TLB, prefetch/TTU, cursor timing, MALL/SubVP, underflow/status handling, and read-line interrupts.
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/`, where HUBP flip interrupts and DCHUBBUB timeout/fault-style status fields are wired into Display Core interrupt handling.
- Display Mode Library DCN 3.2 code under `drivers/gpu/drm/amd/display/dc/dml/dcn32/`, which computes watermark, p-state, self-refresh, urgent, prefetch, TTU, DET, compbuf, and SubVP values later packed through these fields.
- Display-audio code and codec setup paths under `drivers/gpu/drm/amd/display/`, which rely on Azalia controller, root, stream, and endpoint fields for HDMI/DP audio capability reporting, stream setup, DMA behavior, power state, and CRC/diagnostic behavior.
- DMUB and firmware-facing code that captures or receives fields such as HUBPREQ cursor settings, MALL/SubVP surface address state, and DCN 3.2 register masks/shifts for firmware-assisted display flows.
- Diagnostic/state-dump paths that read DCHUBBUB performance, CRC, DCC, timeout, VM fault, HUBP MALL, surface-in-use, read-line, underflow, and memory-power fields.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.2.0 register specification is the primary risk. A single incorrect mask or shift can corrupt audio setup, memory arbitration, VM addressing, page-table boundaries, surface address programming, flip timing, or power/reset behavior.
- This range contains many repeated families: Azalia stream 0-15, endpoint 0-7, input endpoint 0-7, VM contexts 0-15, watermark sets A-D, and HUBP/HUBPREQ/HUBPRET instance-0 families. Copy-generation mistakes can leave valid C symbols with wrong instance prefixes or bit positions.
- Surface and metadata address fields are security- and stability-sensitive. Incorrect low/high address masks, VMID fields, aperture fields, or TMZ/security/noalloc fields can cause memory faults, display corruption, incorrect protected-content handling, or unintended memory access attributes.
- Watermark, urgent bandwidth, p-state, self-refresh, USR retraining, TTU, prefetch, and per-line-delivery fields are timing-sensitive. Errors may only reproduce under high bandwidth, VRR/SubVP/MALL, low-power transitions, multi-plane scanout, or memory-clock changes.
- Side-effecting clear/ack/reset/force bits require precise masks. Mistakes can drop interrupts, leave stale fault state, trigger resets, force clock/p-state behavior, or hide real timeout/underflow conditions.
- Audio fields combine capability reporting, DMA attributes, power management, and stream/endpoint indirection. Bad masks can appear as missing HDMI/DP audio, corrupted audio, wrong codec responses, or failures only under suspend/resume or stream reconfiguration.
- The chunk starts after the `MMHUBBUB_WARMUP_CONTROL_STATUS` shifts and ends before the full `HUBPRET0_HUBPRET_READ_LINE_STATUS` definition. Final file-level reconciliation must merge neighboring chunks to avoid treating those partial register families as complete here.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU Display Core with DCN 3.2 support enabled and ensure all in-scope `MMHUBBUB`, `AZALIA`, `DCHUBBUB`, `DCN_VM`, `HUBP0`, `HUBPREQ0`, and `HUBPRET0` field names referenced by hubbub, hubp, audio, IRQ, DMUB, and diagnostics code resolve.
- Run generated-register consistency checks that every in-scope field has paired `_SHIFT` and `_MASK` definitions, masks fit within 32 bits, repeated instance families match the hardware spec, and fields within each register do not overlap unexpectedly.
- Compare this range against the authoritative DCN 3.2.0 register specification, focusing on side-effecting clear/ack/reset bits, VM/page-table address fields, protected/TMZ/security fields, audio stream/endpoint indirection, and timing/watermark fields.
- Exercise modesets and atomic flips on the pipe backed by HUBP0, including RGB and YCbCr formats, luma/chroma surfaces, compressed metadata, viewport changes, rotation/mirroring/alpha, page flips, cursor movement, and surface-address changes.
- Stress DCHUBBUB watermarks and memory-system controls with multi-plane, high-resolution, high-refresh, MALL/SubVP, VRR, memory-clock p-state transitions, self-refresh entry/exit, and suspend/resume while watching for underflow, timeout, flicker, or missed flips.
- Validate VM behavior by testing GPUVM/system aperture paths, page-table context setup, fault reporting, default address behavior, protected content/TMZ, and fault clear/status decoding.
- Test HDMI/DP audio enumeration and playback across stream enable/disable, hotplug, suspend/resume, underflow handling, and codec power-state transitions; confirm stream/endpoint indirect register access remains instance-correct.
- Use CRC, DCC statistics, performance measurement, timeout status, VM fault state, MALL status, surface-in-use readback, and HUBPRET read-line/vblank status as diagnostic signals before and after modeset, flip, power, and audio transitions.

## Chunk-Specific Summary

Lines 4914-7581 define DCN 3.2.0 bit shifts and masks for the tail of MMHUBBUB/WBIF controls, the full Azalia display-audio controller/root/stream/endpoint area, DCHUBBUB arbitration/SDPIF/return-path/VM-request areas, and the first HUBP/HUBPREQ/HUBPRET scanout path up to the start of `HUBPRET0_HUBPRET_READ_LINE_STATUS`. The content is generated register ABI, not executable logic. Correctness depends on exact mask/shift values, repeated-family instance correctness, careful handling of side-effecting status/clear/reset/force fields, and hardware validation across display scanout, audio, VM faults, memory arbitration, MALL/SubVP, low-power transitions, interrupts, and diagnostics.
