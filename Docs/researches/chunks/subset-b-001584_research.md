# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 7309-9956

## Purpose

This chunk is generated AMD DCN 1.0 register field metadata. It defines `_SHIFT` and `_MASK` macros for bitfields in display-core MMIO registers, pairing with `dcn_1_0_offset.h` register addresses so the DC driver can use typed register/field tables and `REG_*` helpers instead of hard-coded bit arithmetic.

The covered range starts in the middle of the `MCIF_WB1` writeback block and then spans these DCN 1.0 address blocks:

- `dce_dc_mmhubbub_mmhubbub_dispdec` and `dce_dc_mmhubbub_vgaif_dispdec`: writeback interface, VGA interface, MMHUBBUB memory power, clock gating, soft reset, write-combine, and outstanding-counter fields.
- `dce_dc_mmhubbub_mmhubbub_dcperfmon_dc_perfmon_dispdec`: DC perfmon instance 5.
- HDA/Azalia display-audio blocks: stream index/data windows for streams 0-15, endpoint and input-endpoint indirect windows, controller DMA/DTO/CRC/memory-power controls, root codec parameters, channel/power state, connectivity, and GTC offsets.
- `dce_dc_dchubbub_hubbub_sdpif_dispdec`, `ret_path`, and `hubbub`: framebuffer/aperture routing, MARC remap windows, pipe security levels, DCC return-path config, CRC values, arbitration/watermarks, VTG controls, soft reset, clocking, DCFCLK gating, and performance measurement fields.
- `dce_dc_dchubbub_dchubbub_dcperfmon_dc_perfmon_dispdec`: DC perfmon instance 7.
- `dce_dc_dcbubp0_dispdec_hubp`, `hubpreq`, `hubpret`, and `cursor`: HUBP0 surface format/tiling/viewport, request sizing, clocks, VM/page-table/protection fault registers, flip/in-use status, TTU/QoS/prefetch timing, read-line/vblank interrupts, cursor memory/address/size/position/hotspot/stereo fields, and cursor memory power.
- `dce_dc_dcbubp0_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: the beginning of DC perfmon instance 8.

There are no C functions or data objects in this range. Its purpose is to make hardware register layouts available to the rest of the DCN 1.0 display driver at compile time.

## Important APIs, Types, And Macros

The public surface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit field mask.
- Full-width address/data registers use mask `0xFFFFFFFFL`; high-address halves commonly use `0x0000FFFFL`.
- Repeated register instances preserve hardware instance names, for example `AZF0STREAM0` through `AZF0STREAM15`, `VTG0` through `VTG5`, `SURFACE_CHECK0` through `SURFACE_CHECK3`, and perfmon instances `DC_PERFMON5`, `DC_PERFMON6`, `DC_PERFMON7`, and partial `DC_PERFMON8`.

Important field families in this chunk include:

- Writeback and MMHUBBUB: `MCIF_WB1_MCIF_WB_BUF_[2-4]_ADDR_[Y/C]`, buffer offsets, VCE buffer-manager lock/interrupt fields, NB P-state watermark/control fields, client watermark, warmup pitch, self-refresh, QoS, luma/chroma buffer sizes, `WBIF[0-1]_SMU_WM_CONTROL`, `MMHUBBUB_MEM_PWR_*`, `MMHUBBUB_CLOCK_CNTL`, and `MMHUBBUB_SOFT_RESET`.
- Audio/Azalia: stream and endpoint indirect access fields, `AZ_CLOCK_CNTL`, `AZALIA_AUDIO_DTO`, DMA non-snoop/isochronous controls, CORB/RIRB/BDL controls, payload capability, CRC/input-CRC controls/results, memory power controls/status, root codec parameters, and port-connectivity overrides.
- DCHUBBUB: SDPIF framebuffer/AGP/aperture bounds, MMIO and MARC mappings, pipe security level, memory power, DCC return-path configuration per pipe, CRC values, arbitration outstanding/saturation/QoS/DRAM state, watermark sets A-D, watermark-change request/status/ack, timeout enable, global timer, surface checkers, VTG controls, soft reset, clock control, DCFCLK gate delays, and latency measurement fields.
- HUBP/HUBPREQ/HUBPRET: primary/secondary viewport and chroma viewport dimensions, surface pixel format/rotation/mirroring, address/tiling configuration, request size, VM system aperture and context0 page-table registers, primary/secondary surface and metadata addresses, flip control/interrupt/in-use state, TTU and prefetch timing, blank/nominal/vblank parameters, cursor settings, ref-to-pixel frequency ratio, read-line windows, and vblank/read-line interrupt state.
- Cursor: enable/mode/snoop/system/pitch/lines-per-chunk, cursor surface address high/low, size, screen position, hotspot, stereo offset, destination X offset, and cursor RAM power fields.
- Perfmon: control, control2, per-counter state, run-enable, count-off interrupt, counter interrupt status/ack, current value, high/low counter reads, and read select fields.

These macros are consumed through AMD DC register-list macros such as `SR`, `SRI`, `SRII`, and field-list macros such as `HWS_SF`, `HUBP_SF`, `HUBBUB_SF`, `IPP_SF`, `TF_SF`, and irq field tables. The include is visible in DCN 1.0 resource and IRQ setup, including `display/dc/resource/dcn10/dcn10_resource.c` and `display/dc/irq/dcn10/irq_service_dcn10.c`.

## Control Flow

This header has no runtime control flow. The effective flow happens at compile time and at driver initialization:

1. DCN 1.0 code includes `dcn_1_0_offset.h` for register addresses and this file for field positions.
2. Register-list macros build per-block register structures from address macros.
3. Field-list macros build per-block mask/shift structures from this file's `_SHIFT` and `_MASK` macros.
4. Runtime code uses generic register helpers to compose read-modify-write values, poll status bits, acknowledge interrupts, and unpack hardware state.

Because this chunk is a schema, every macro is an input to later generated or hand-written initialization paths. There are no local branches, loops, allocations, or calls here, but incorrect metadata directly changes register programming in the consumers.

## State And Persistence Behavior

The header itself has no mutable state and persists no software data. The state it describes is hardware state in the display engine:

- Writeback, HUBP, HUBPREQ, and DCHUBBUB address fields point display scanout/writeback traffic at VRAM/system apertures and metadata surfaces.
- Watermark, QoS, prefetch, TTU, and arbitration fields control when the memory hub asks for bandwidth, enters/exits self-refresh, or permits DRAM clock changes.
- Flip and in-use fields describe pending/current surfaces and are synchronized to display timing.
- Interrupt fields mask, clear, acknowledge, and report vblank, read-line, perfmon, and watermark-change events.
- Memory power, clock-gate, and soft-reset fields alter persistent hardware block state until another driver write or hardware reset.
- Perfmon and CRC fields accumulate hardware measurement or validation results until reset/acknowledged/reprogrammed.

These definitions do not enforce ordering. Ordering requirements live in the consumers: for example, addresses and tiling must be programmed coherently before a flip is armed, VM aperture/page-table state must match the memory manager's view, and interrupt status/ack bits must be handled according to the hardware protocol.

## Dependencies

This chunk depends on the generated DCN 1.0 register address header, `dcn_1_0_offset.h`, because masks and shifts are useful only when paired with the matching `mm...` addresses and base-index macros. It also depends on the AMD display core register helper conventions that expect exact macro names in the `<REGISTER>__<FIELD>_{SHIFT,MASK}` form.

Important code-level dependencies include:

- DCN 1.0 resource construction in `display/dc/resource/dcn10/dcn10_resource.c`, which includes this header and builds register tables for HUBP, HUBBUB, DPP/IPP, DWB, audio, timing, and IRQ services.
- DCN 1.0 IRQ service setup in `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes this header to map interrupt control/status fields.
- Hardware block headers under `display/dc/dcn10/`, `display/dc/dpp/dcn10/`, `display/dc/hwss/dce/`, and related DCE/DCN components that declare the field-list macros consumed by resource setup.
- The ASIC-specific hardware contract for DCN 1.0; later DCN/DCE generations carry similar macro names but not always identical masks, shifts, or field presence.

## Integration Points

Display bring-up and mode programming use the HUBP/HUBPREQ/HUBPRET and DCHUBBUB definitions heavily. Surface programming relies on fields such as `SURFACE_PIXEL_FORMAT`, tiling mode, viewport start/dimensions, primary/secondary luma/chroma surface addresses, metadata addresses, flip control, and in-use status. Memory-system programming relies on VM aperture, page-table base/start/end, protection fault status/address, L1 TLB control, request-size, prefetch, TTU, and watermark fields.

Power and bandwidth management integrate through MMHUBBUB/DCHUBBUB and writeback fields: NB P-state controls, self-refresh, SMU watermark-change request/ack, DCHUBBUB watermark sets A-D, DRAM state controls, DCFCLK gating, MMHUBBUB/DCHUBBUB clock gating, memory-power force/disable/status, and soft reset.

Audio integration uses the Azalia register map. DTO fields configure the display audio clock ratio, stream/endpoint index-data windows expose codec/stream registers indirectly, DMA control fields select snoop/isochronous behavior, payload capability and channel-count fields advertise stream capacity, CRC fields support validation, and memory-power fields control audio SRAM blocks.

Diagnostics and validation integrate through perfmon and CRC blocks. Perfmon instances 5, 6, 7, and the start of 8 provide event selection, run control, counter state, interrupt status/ack, and 48-bit-ish high/low counter readout fields for MMHUBBUB, audio, DCHUBBUB, and HUBP-related measurement paths. DCHUBBUB and Azalia CRC controls expose frame/audio data validation signals.

Cursor and scan-position integration uses `CURSOR0_*` and `HUBPRET0_*`: cursor address, size, position, hotspot, stereo offsets, vblank/read-line windows, interrupt masks/types/clears, status, and read-line snapshots.

## Risks And Edge Cases

- This is generated hardware metadata, so small numeric errors have large blast radius. A bad mask or shift can cause register helpers to preserve the wrong bits, overwrite adjacent fields, fail to clear interrupts, or program invalid addresses.
- The chunk starts mid-`MCIF_WB1` block and ends mid-`DC_PERFMON8` block. Final file-level reconciliation must combine it with neighboring chunks before drawing conclusions about full block coverage.
- Several fields are single-bit control/status/ack fields packed near each other, especially interrupt and power-control registers. Confusing status bits with clear/ack bits can create lost interrupts or repeated interrupt storms in consumers.
- Address fields are split across low and high registers with 16-bit high masks. Consumers must keep low/high luma, chroma, and metadata addresses consistent, especially around atomic flips.
- VM and aperture fields in `HUBPREQ0_DCN_VM_*` are security- and stability-sensitive. Wrong masks can expose incorrect memory, report misleading faults, or break page-table walks.
- Repeated hardware instances invite copy/paste or generator drift. Stream, endpoint, VTG, surface-checker, watermark-set, and perfmon instances should remain structurally symmetric except where the hardware intentionally differs.
- Some names contain hardware spelling quirks, such as `PREFETCH_SETTINS`. Consumers must use the exact generated macro names; "fixing" spelling locally would break table expansion.
- Register definitions are generation-specific. Similar DCE/DCN headers nearby may define additional fields or different widths; cross-generation code must not assume these DCN 1.0 masks match later ASICs.
- Full-width masks use `L`-suffixed constants. Refactors should preserve unsigned 32-bit register semantics and avoid sign-extension surprises in helper code.

## Test Signals

Useful validation for this chunk is mostly integration and hardware-oriented:

- Build coverage for DCN 1.0 display code should compile all field-list users that include `dcn_1_0_sh_mask.h`; missing or renamed macros are caught at compile time.
- Static checks can pair every `_SHIFT` with a matching `_MASK`, verify masks fit within 32 bits, and ensure repeated instances such as `AZF0STREAM[0-15]`, endpoint/input-endpoint windows, `VTG[0-5]`, surface checkers, and perfmon blocks remain consistent.
- Register read/write helper tests or trace validation should confirm that field updates preserve unrelated bits in packed registers such as watermark-change control, clock gating, memory power, flip interrupt, HUBPRET interrupt, cursor control, and perfmon control.
- Display mode-set smoke tests should exercise scanout with primary/chroma surfaces, viewport changes, flips, cursor enable/move/disable, vblank/read-line interrupts, and power-gating transitions.
- VM fault and aperture tests should confirm HUBPREQ aperture bounds, context0 page-table programming, fault address/status reporting, and L1 TLB control behave as expected.
- Bandwidth/power tests should watch for stable watermark changes, self-refresh/DRAM-clock-change behavior, DCFCLK gating, and no underruns under stress.
- Audio tests should cover HDMI/DP audio stream setup, DTO programming, endpoint index/data access, DMA controls, payload capability, channel count, CRC result paths, and audio memory power transitions.
- Perfmon/CRC diagnostics should be able to start counters, observe active/state/status bits, acknowledge interrupts, read low/high values, and validate CRC complete/result fields without corrupting adjacent fields.
