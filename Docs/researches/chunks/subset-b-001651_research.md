# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 2688-5235

## Scope And Purpose

This chunk is part of a generated AMD DCN 2.1 register offset header. It contains no executable C code, structs, enums, storage, or functions. Its interface is a set of `#define` constants that map symbolic display-engine register names to MMIO register offsets plus matching `_BASE_IDX` segment identifiers.

The path is under a local `ceph-client` source mirror, but this file belongs to the Linux AMDGPU display stack. In this range the content describes DCN display pipeline hardware blocks for HUBP/HUBPREQ/HUBPRET instances 2 and 3, cursor instances 1 through 3, DPP instances 0 through 3, color conversion, scaling, color management, and associated display performance monitors.

The chunk starts at the tail of cursor instance 1 DMDATA software-access registers and ends in the middle of DPP3 color-management degamma RAM A definitions. Adjacent chunks are required for the complete cursor1 and CM3 register sets.

## Important APIs, Types, And Macro Families

There are no callable APIs in this chunk. The public contract is the generated register-address macro naming scheme:

- `mm<REGISTER>` gives the register offset within the base segment selected by the companion `_BASE_IDX` macro.
- `mm<REGISTER>_BASE_IDX` gives the segment index used by DCN register-list macros to add the correct ASIC base address.
- Consumers combine this header with `dcn_2_1_0_sh_mask.h`, where matching field shift and mask macros live.
- Register-list helpers such as `SR`, `SRI`, `SRII`, `SRIR`, `DCCG_SRII`, and `DMUB_SR` concatenate names like `mmHUBP2_DCSURF_SURFACE_CONFIG` and `mmHUBP2_DCSURF_SURFACE_CONFIG_BASE_IDX` into per-block register tables.

The chunk contains 2,412 `#define` lines, representing 1,206 register offsets and 1,206 base-index constants. Every visible base index is `2`, which routes these offsets through the DCN/DMU register base segment used by the DCN21 display code.

Major macro families in this range:

- `HUBP2` and `HUBP3`: hub pipe front-end registers for surface configuration, tiling, primary/secondary viewport dimensions, request sizing, HUBP control, clock control, VM page settings, debug, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: hub request registers for surface pitches, VMID settings, primary/secondary luma/chroma surface and metadata addresses, flip control, in-use and earliest-in-use readbacks, TTU/QoS controls, VM aperture/TLB controls, prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor timing, reference-to-pixel frequency conversion, DRQ limits, and memory power state.
- `HUBPRET2` and `HUBPRET3`: hub return/read-line controls, memory power state, interrupt register, read-line value, and read-line status.
- `CURSOR0_1`, `CURSOR0_2`, and `CURSOR0_3`: cursor surface address, size, position, hot spot, stereo, destination offset, memory power, dynamic metadata address/control/QoS/status, and DMDATA software data registers. Instance 1 is only partially visible at the start of this chunk.
- `DC_PERFMON8` through `DC_PERFMON13`: performance counter control, state, perfmon control, current-value interrupt/misc, and high/low counter readback registers associated with HUBP/DPP perfmon address blocks.
- `DPP_TOP0` through `DPP_TOP3`: DPP control, soft reset, CRC value/control, and host-read control.
- `CNVC_CFG0` through `CNVC_CFG3`: color conversion surface format, format control, floating-point bias/scale by channel, color-keyer controls and values, and alpha 2-bit LUT registers.
- `CNVC_CUR0` through `CNVC_CUR3`: cursor color/conversion controls in the DPP color conversion path.
- `DSCL0` through `DSCL3`: scaler coefficient RAM access, scaler mode/tap/manual replicate controls, horizontal and vertical scale ratios and initial phases for luma/chroma, black offset, update/autocal, overscan, OTG blanking dimensions, recout/MPC size, line-buffer format/memory control, vertical counter, scaler memory power, and output-buffer controls.
- `CM0`, `CM1`, `CM2`, and partial `CM3`: color-management controls including input CSC matrices, gamut remap matrices, bias, degamma LUT programming, RAM A/B curve segment controls, blend gamma LUTs, HDR multiplier coefficient, CM memory power, dealpha, coefficient format, shaper LUTs, 3D LUT controls, output normalization/offset, and debug index/data. CM3 coverage ends before the full CM3 set is complete.

## Control Flow

This header has no runtime control flow. Runtime behavior is produced by AMD display code that includes the generated offset and shift/mask headers and uses register helper macros to build tables or perform MMIO accesses.

Typical flow for DCN21 register access:

1. A hardware object definition names a logical register, often through a macro list such as a HUBP, DPP, scaler, color-management, or perfmon register list.
2. `dcn21_resource.c` expands helper macros such as `SR`, `SRI`, and `SRII` against this header, computing `BASE(mm..._BASE_IDX) + mm...` for each register table entry.
3. Higher-level DC code stores those computed offsets in per-block register structs for HUBP, DPP, DSCL, color management, cursor, IRQ, and related hardware objects.
4. Runtime functions use those register structs with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and paired field masks from `dcn_2_1_0_sh_mask.h`.
5. The final effect is an MMIO read, write, or read-modify-write against DCN21 display hardware.

For HUBP/HUBPREQ, the flow is driven by plane programming and flips: the display core computes surface addresses, tiling, viewport, VMID, prefetch, QoS, and flip parameters, then writes the corresponding pipe instance registers. For DPP/DSCL/CM, the flow is driven by stream and plane color/scaler programming: the driver sets pixel format conversion, scaler ratios and taps, CSC/gamut matrices, gamma/shaper/3D LUTs, and memory power controls. Perfmon registers are used by diagnostic and performance paths to enable, select, and read display block counters.

## State And Persistence Behavior

The macros themselves are compile-time constants and store no state. The state they identify is hardware register state inside the DCN21 display engine.

The represented hardware state includes:

- Plane fetch state: surface addresses and metadata addresses, pitch, tiling, viewport, surface-in-use readbacks, flip controls, flip interrupt state, VMID and VM aperture controls.
- Timing and bandwidth state: TTU/QoS watermarks, prefetch parameters, vblank/flip/nominal timing registers, per-line delivery, destination dimensions, and reference-frequency conversion.
- Cursor state: cursor enable/configuration, memory addresses, position, hot spot, stereo control, memory power, dynamic metadata control/status, and software DMDATA access.
- DPP processing state: top-level enable/reset/CRC state, pixel format conversion, color keying, cursor color conversion, scaler taps/ratios/initial phases, line-buffer/output-buffer state, color-management matrices, LUT programming indices/data, 3D LUT controls, shaper/blend/degamma curve RAMs, and memory power/status.
- Readback and status state: HUBPRET read-line values/status, memory power status registers, scaler vertical counter, debug index/data ports, CRC values, and perfmon high/low counter values.

Some registers are durable configuration until the next modeset, plane update, power transition, or hardware reset. Others are latched status, debug selectors, counter readbacks, memory power state readbacks, interrupt/status registers, or index/data ports with side effects. This offset header does not encode write ordering, side effects, reset values, or read-modify-write rules; those semantics live in hardware documentation and in the consuming driver code.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_1_0_offset.h` supplies the offsets covered here.
- `dcn_2_1_0_sh_mask.h` supplies matching field masks and shifts.
- `renoir_ip_offset.h` supplies the DCN/DMU base segment definitions used by `BASE(mm..._BASE_IDX)`.
- `reg_helper.h` and DMUB register helpers provide the token-concatenation and MMIO access macros that consume these names.

Direct local integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes this header and expands register-list macros into DCN21 hardware object register tables.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same generated headers for DMUB common/internal register table construction, though this specific chunk is mostly display-pipe rather than DMUB register coverage.
- `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the headers for interrupt-source register definitions and maps HUBP flip/vblank/vupdate/DMCUB sources into DAL IRQ sources.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, which share the same generated DCN21 register namespace for GPIO/DDC/HPD-related hardware tables.
- DCN20/DCN21 shared hardware modules such as HUBP, DPP, MPC, OPP, DSC, DCCG, VMID, DCE audio, DMCU, DMUB PSR/ABM, and hardware sequencing code that are instantiated from the DCN21 resource file.

## Risks And Maintenance Notes

- This is generated hardware ABI data. A wrong offset or base index can compile cleanly while directing a valid register helper to the wrong MMIO address.
- The repeated instance layout is easy to damage manually. `HUBP2` and `HUBP3`, `DPP_TOP0` through `DPP_TOP3`, `DSCL0` through `DSCL3`, and `CM0` through `CM3` have similar names but different offsets; instance drift can create failures that appear only when a specific pipe is used.
- The chunk boundary is not semantic. It starts after the beginning of cursor instance 1 and ends before the end of CM3, so a whole-file merge must combine adjacent chunk reports before claiming complete cursor1 or CM3 coverage.
- Surface address, metadata address, VMID, VM aperture, and TLB offsets are security- and stability-sensitive because they determine what memory the display engine fetches.
- Flip, in-use, earliest-in-use, and interrupt offsets must stay aligned with IRQ and page-flip code. Incorrect values can cause missed page-flip completion, stale buffers being scanned out, or interrupt storms.
- Scaler, CSC, gamut, gamma, shaper, blend, and 3D LUT registers are packed hardware programming surfaces. Bad offsets can cause visual corruption, wrong color output, HDR/SDR conversion regressions, or LUT writes landing in unrelated registers.
- Index/data style LUT and debug registers require correct sequencing in consumers. This header identifies the ports but does not prevent concurrent or out-of-order access.
- Memory power control/status offsets are power-management sensitive. Wrong register addresses can leave blocks powered down during use or prevent expected power savings.
- Perfmon offsets affect diagnostics and validation. Counter programming bugs may not affect scanout directly but can hide performance, bandwidth, or underflow issues during debugging.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU/DC with DCN21 support enabled; missing or renamed macros should fail in DCN21 resource, IRQ, GPIO, or DMUB compilation units.
- Compare regenerated `dcn_2_1_0_offset.h` output against the committed/generated source and adjacent ASIC families to catch accidental offset or instance drift.
- Exercise DCN21 hardware with at least four active display pipes where possible, so HUBP/DPP/DSCL/CM instances 0 through 3 are all used.
- Run modeset, hotplug, suspend/resume, page-flip, cursor movement, cursor format/size changes, and multi-plane overlay scenarios; watch for page-flip timeouts, stale frames, cursor corruption, or HUBP flip interrupt anomalies.
- Validate high-bandwidth and memory-pressure display modes that stress HUBPREQ prefetch, TTU/QoS, per-line delivery, and VM settings; watch for underflow, blanking artifacts, or bandwidth validation mismatches.
- Check color pipeline behavior with scaling, CSC/gamut remap, degamma/blend gamma, shaper LUT, 3D LUT, HDR, color keying, and alpha use cases; visual output should match expected color-management results.
- Confirm memory power transitions do not break active scanout or LUT/scaler programming and that related status registers report plausible state.
- Use display CRC and perfmon/debug readbacks where available to verify CRC counters and perfmon high/low values move as expected during active scanout.
