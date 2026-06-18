# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 54427-56984

## Scope And Purpose

This chunk is a generated AMD DCN 2.0 register shift/mask header segment. It does not define executable code; it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for hardware registers used by the AMD display driver. The constants are paired with register offsets from `dcn_2_0_0_offset.h` and consumed through display register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and object-specific register tables.

The covered lines begin in the DMCUB interrupt/control area, continue through MCIF writeback buffer-manager instance 2, XFC/MMHUBBUB crossbar and write-buffer controls, and then cover DPP instance 4 top-level, converter, cursor, scaler, output-buffer, and color-management fields. The source-tree contract is that these names exactly match the generated register names expected by DCN 2.0 display code; changing a constant changes how driver field helpers pack and unpack MMIO values.

## Register Groups Covered

The first section completes DMCUB interrupt type masks and then defines DMCUB external interrupt, fault, security, memory, mailbox, timer, scratch, control, GPINT, low-power wake, memory-power, timer-current, and processor-ID fields. Important fields include `DMCUB_EXT_INTERRUPT_STATUS` count/ID extraction, fault address registers for instruction fetch/data write/undefined address faults, `DMCUB_SEC_CNTL` security reset and fault-clear bits, `DMCUB_MEM_CNTL` QoS/read-write address-space fields, inbox/outbox base/size/read-write pointer registers for channels 0 and 1, `DMCUB_CNTL` enable/soft-reset/trace/light-sleep/gating fields, GPINT data in/out registers, and `DMCUB_MEM_PWR_CNTL` force/disable/state fields.

The `dce_dc_mmhubbub_mcif_wb2_dispdec` block defines the writeback buffer-manager instance 2 surface. It includes software control and VCE control bits, current-line/status fields, luma/chroma pitch, buffer 1-4 status and status2 registers, arbitration and SCLK/P-state/watermark controls, test-debug index/data, per-buffer Y/C base addresses and offsets, high address bytes, luma/chroma sizes, and per-buffer resolution. Status fields expose active, locked, overflow, disabled, mode, tag, next-buffer, field, current line, line-length error, frame-length error, color-depth, TMZ, Y/C overrun, and eye-flag state.

The `dce_dc_mmhubbub_xfcp0_dispdec` through `xfcp5_dispdec` blocks repeat an identical XFC per-pipe layout for instances 0 through 5. Each instance has `MMHUBBUB_XFC_CNTL` fields for master/slave enable, 64bpp pixels, XBUF full enable, bandwidth-reduction mode, alpha position, local GPU ID, target pipe ID, and slave-to-master GPU ID. Each instance also supplies two XBUF write base addresses split into LSB/MSB, XBUF software mode and pitch, and XBUF width/height.

The shared `dce_dc_mmhubbub_xfc_dispdec` block defines XFC memory power control, XBUF write surface tiling/configuration, VMID/AWCACHE/QoS/stall controls, backpressure release timing, GPU write attributes, loopback and BRESP flags, VM initialization control and base/pixel values, per-GPU base addresses, and XFC monitor counters for requests and backpressure. These fields are used to configure and observe cross-GPU/display fabric writeback behavior.

The `dce_dc_dpp4_dispdec_dpp_top_dispdec` block defines DPP instance 4 top controls: DPP clock enable, clock-gate disable bits, test clock selection, per-subblock soft reset for CNVC/DSCL/CM/OBUF, CRC value/control fields, and host-read throttling. This is the root control surface for display pipe processor instance 4.

The `cnvc_cfg` and `cnvc_cur` blocks define DPP4 pixel conversion and cursor fields. Conversion fields include surface pixel format, format expansion/CNV16/alpha/bypass/clamp/update-pending state, floating-point bias/scale per channel, color-key enable/mode and low/high thresholds for ARGB channels, and the 2-bit alpha LUT. Cursor fields control enable, expansion, pixel inversion, ROM mode, cursor mode, pixel alpha modulation, update-pending state, two cursor colors, and cursor FP scale/bias.

The `dscl` block defines DPP4 scaler and line-buffer fields. It includes coefficient RAM tap select/data, scaler mode and coefficient bank selection, luma/chroma tap counts, 2-tap sharpen controls, manual replicate controls, horizontal/vertical scale ratios and initial phases for luma/chroma/bottom-field paths, black offsets, update-pending and autocal fields, overscan, OTG blanking, recout/MPC geometry, line-buffer data format and partitioning, line-buffer vertical counters, DSCL memory power state/control, OBUF control, and OBUF memory power state/control.

The final `cm` block defines DPP4 color-management fields. It includes color-management bypass/update state, input CSC mode and matrix coefficients for current and B sets, gamut remap matrices for current and B sets, bias registers, degamma controls and LUT access, blend gamma controls and LUT access, HDR multiplier coefficient, memory power state/control, dealpha enable, coefficient format selectors, and shaper controls/LUT access. The chunk ends in the shaper RAMB region definitions after listing RAMA and part of RAMB region metadata.

## Important APIs, Types, And Macros

There are no C functions, structs, or runtime APIs in this chunk. The important exported interface is the macro namespace itself:

- `<REGISTER>__<FIELD>__SHIFT` constants provide the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` constants provide the already-shifted mask for the same field.
- Register names are paired with `mm<REGISTER>` offsets from `dcn_2_0_0_offset.h`.
- Consumer code expands these constants through generated helper macros such as `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`, then uses register access wrappers to read, write, or update fields safely.

Representative consumers include `display/dmub/src/dmub_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, `display/dc/resource/dcn20/dcn20_resource.c`, and `display/dc/gpio/dcn20/hw_factory_dcn20.c`, all of which include this header alongside the matching DCN 2.0 offset header.

## Control Flow And State Behavior

This header has no local control flow. The control flow is in callers that use these masks to perform MMIO sequences. For example, DMUB DCN 2.0 setup reads `DMCUB_CNTL.DMCUB_SOFT_RESET`, writes GPINT commands, toggles `DMCUB_CNTL.DMCUB_ENABLE` and `DMCUB_CNTL.DMCUB_SOFT_RESET`, resets DMCUB inbox/outbox pointers, programs DMCUB security/memory control, and writes DMCUB window registers. Those operations rely on the DMCUB field positions in this chunk being correct.

The state represented here is hardware state, not persisted kernel data. Writes alter GPU display engine registers, firmware mailbox pointers, buffer-manager state, XFC write/monitor configuration, DPP4 scaler/color/cursor registers, and memory power controls. Some fields are status-only or handshake-like, such as `*_UPDATE_PENDING`, `*_INIT_DONE`, `*_STATS_VALID`, fault address/status bits, current-line counters, CRC values, memory-power state fields, and monitor statistics.

Persistence is limited to the device register state until reset, power-gating, modeset reprogramming, or driver teardown. LUT-related registers (`CM4_CM_DGAM_*`, `CM4_CM_BLNDGAM_*`, `CM4_CM_SHAPER_*`, and scaler coefficient RAM) represent programmed hardware tables and their bank/selection/status bits; callers must follow the correct index/data/write-enable sequencing because this header only supplies bit layout.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register naming scheme and the matching offset header. It is integrated through AMD display register helpers and hardware object initialization tables. The same field names also appear in related ASIC headers for other DCN generations, but the exact masks can differ; consumers must include the header for the selected ASIC generation.

Integration points by subsystem:

- DMUB firmware service: DMCUB control, mailbox, scratch, GPINT, security, memory, timer, and fault fields support firmware boot/reset, window setup, interrupts, and diagnostics.
- IRQ service: interrupt status/type/context fields provide decoding and acknowledge support for DCN 2.0 interrupt handling.
- Display writeback and memory hub: MCIF_WB2 and XFC/MMHUBBUB fields configure display writeback buffers, crossbar routing, write surfaces, VM initialization, QoS, P-state watermarks, and monitoring.
- DPP instance 4: DPP_TOP4, CNVC4, DSCL4, OBUF, and CM4 fields are used by resource construction and pipe programming for one display pipe processor instance.
- Color and scaling programming: LUT index/data/write-enable masks and scaler coefficient RAM masks are the low-level contract for higher-level color-management and scaling algorithms.

## Risks And Failure Modes

The primary risk is silent hardware misprogramming. If a shift or mask is wrong, helper macros can write the wrong bits while the code still compiles. Consequences include failed DMUB boot/reset, stuck mailbox pointers, missed or uncleared interrupts, invalid fault handling, writeback corruption, wrong display format conversion, incorrect scaler coefficients, broken cursor/color-key behavior, invalid color transforms, power-gating hangs, or display pipe underruns.

Generated headers also carry naming and versioning risk. A field name mismatch breaks compile-time macro expansion in register table initializers; a mask copied from a different ASIC generation can compile but program an incompatible register layout. Repeated instance blocks such as XFC0-5 and patterned LUT region blocks are especially prone to mechanical generation or merge errors because most lines look identical except the instance or region number.

Runtime sequencing remains a caller responsibility. This header does not encode whether a field is read-only, write-one-to-clear, latched on update, double-buffered, or requires polling. Fields such as interrupt ACKs, fault clears, LUT write enables, VM init done, stats valid ACK, and update-pending bits require the surrounding driver logic to use the right order and wait conditions.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build signal: AMD display code must compile with this header and `dcn_2_0_0_offset.h`; undefined `FD_MASK`/`FD_SHIFT` expansions reveal missing or renamed fields.
- Static comparison signal: generated DCN 2.0 masks should match the authoritative register database and remain consistent with adjacent instance blocks and matching offset names.
- DMUB signal: DCN 2.0 hardware should boot/reset DMUB, exchange GPINT commands, and move inbox/outbox pointers without hangs or fault interrupts.
- Display pipeline signal: modesets using DPP4 should produce correct CRCs, scaling geometry, cursor rendering, pixel format conversion, color keying, gamma/shaper behavior, and memory power transitions.
- Writeback/XFC signal: MCIF_WB2 and XFC paths should produce valid writeback buffers, report sensible current-line/status/overrun fields, and avoid backpressure or P-state watermark regressions.
- Runtime diagnostics: fault address registers, XFC monitor counters, CRC registers, memory-power status fields, update-pending bits, and interrupt status/ACK fields are observable indicators that the masks line up with real hardware behavior.
