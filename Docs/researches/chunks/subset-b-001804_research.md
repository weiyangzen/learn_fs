# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 4751-7217

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and bit masks used to access fields inside display-controller MMIO registers. Consumers include this file together with `dcn_3_1_2_offset.h`, build register tables, and then use helpers such as `REG_GET`, `REG_UPDATE`, `REG_SET`, and DMUB `FD_MASK`/`FD_SHIFT` expansions to read or program individual hardware fields.

The requested range starts in the tail of the interrupt-destination field block and then covers complete field definitions for DC interrupt routing, DMU miscellaneous control, display-controller power-gating control, DMCUB memory/window/mailbox/control registers, display writeback top/control/color-processing registers, a writeback perfmon instance, and the beginning of legacy VGA control. The range has 2,153 `#define` lines: 1,077 `__SHIFT` macros and 1,076 `_MASK` macros. The one-count mismatch is caused by the artificial chunk boundary beginning after `DCPG_INTERRUPT_DEST__DCPG_IHC_DOMAIN0_POWER_UP_INTERRUPT_DEST__SHIFT`, while its mask is still present in this chunk.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locks in this range. The public interface is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These macros are consumed through register-helper token pasting. Examples include `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_GET(reg, field, ...)`, and `REG_UPDATE(reg, field, value)`. The offset header identifies which MMIO register to touch; this mask header identifies which bits inside that register are meaningful.

Major field families in this chunk:

- Interrupt destination fields for `DCPG`, `MMHUBBUB`, `WB`, `DCHUB`, `DPP`, `MPC`, `OPP`, `OPTC`, `OTG0` through `OTG5`, `DIG`, `I2C_DDC_HPD`, `DIO`, `DCIO`, `HPD`, `AZ`, `AUX`, `DSC`, and `HPO`. These fields route display, hotplug, audio, AUX, DSC, high-performance output, perfmon, vblank, vline, timeout, underflow, and power-transition interrupts.
- `dce_dc_dmu_dmu_misc_dispdec`: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, SMU/DMCU interrupt controls, zero-shutdown controls/status, and deep-sleep force allowance.
- `dce_dc_dmu_dc_pg_dispdec`: power-gating config/status for domains 0 through 3 and 16 through 18, DCPG interrupt status/control registers, and `DC_IP_REQUEST_CNTL`.
- `dce_dc_dmu_dmcub_dispdec`: DMCUB region offsets/top addresses, region-3 code-window base/top/offset registers, interrupt enable/status/ack/type, external interrupt context, fault-address registers, security and memory control, inbox/outbox ring base/size/read/write pointers, timers, scratch registers, general-purpose interrupt data, low-speed wake enable, processor ID, and DMCUB enable/reset control.
- `dce_dc_wb0_dispdec_dwb_top_dispdec`: DWB clock and memory power, frame-capture mode/flow/window/source geometry, update control, CRC masks/values, output control, backpressure counters, host-read control, overflow status/counter, soft reset, and debug control.
- `dce_dc_wb0_dispdec_dwbcp_dispdec`: DWB HDR multiplier, gamut remap controls and coefficient matrices, output gamma LUT access/control, and RAM A/RAM B piecewise region/start/end/offset fields for red/green/blue channels.
- `dce_dc_wb0_dispdec_wb_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON3` counter-select/control/state/counter-value/high/low fields and interrupt status/ack fields.
- `dce_dc_mmhubbub_vga_dispdec`: initial VGA render, sequencer reset, mode, surface pitch/height, memory base, dispbuf surface address, HDP, cache, and D1/D2 VGA control fields.

## Control Flow

This header has no runtime control flow. Runtime control is supplied by AMDGPU display code that includes the generated register maps:

1. DCN 3.1 resource, IRQ, and DMUB code include `yellow_carp_offset.h`, `dcn/dcn_3_1_2_offset.h`, and `dcn/dcn_3_1_2_sh_mask.h`.
2. Resource and IRQ code build register-address tables with `SR`, `SRI`, `SRII`, and related macros using the offset header.
3. Field tables and register helpers use this chunk's `__SHIFT` and `_MASK` constants to isolate or update register fields.
4. Driver runtime paths sequence operations such as DMCUB reset/release, DMCUB firmware backdoor load, inbox/outbox ring updates, IRQ acknowledgement, display power gating, DWB capture, perfmon setup, hotplug/AUX servicing, and VGA fallback control.

The masks do not encode register ordering. Consumers still must obey hardware sequencing around clock enables, power gating, reset assertion/release, interrupt clear/ack semantics, ring-buffer pointer ordering, secure-window setup, writeback update locking, LUT access sequencing, and suspend/resume restoration.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes fields in MMIO-backed GPU state. The represented hardware state includes:

- Interrupt routing and delivery state for display pipes, hub, writeback, audio, hotplug, AUX/DDC, DSC, HPO, and performance counters.
- DMU and DCPG state for clock control, memory power, zero-shutdown, SMU/DMCU interrupt interaction, display-domain power-gating config/status, and DC IP request handshake bits.
- DMCUB persistent runtime state while the display microcontroller is active: code/data window layout, top/base/offset values, inbox/outbox ring pointers, scratch registers, timer registers, GPINT command/status fields, fault addresses, security control, and reset/enable bits.
- DWB state for capture geometry, output format/alpha/depth/packing, CRC generation, overflow/backpressure accounting, host-read behavior, memory/clock power, and soft reset.
- DWB color-processing state for HDR multiplier, gamut remap coefficients, output gamma LUT index/data, LUT mode, piecewise curve regions, offsets, bases, and slopes.
- Perfmon state for selected counters, event/state selections, repeat count, counter high/low values, overflow/counter-off interrupt status, and ack bits.
- VGA state for blink/render behavior, sequencer reset behavior per display, legacy memory aperture/base/addressing, cache behavior, HDP reset/memory disable, and per-display VGA enable/timing/rotation.

Persistence is hardware-defined. Many configuration fields remain until modeset, power-gating transition, firmware reset, suspend/resume, or ASIC reset. Status, ack, fault, overflow, timer, pointer, and interrupt fields may be sticky, write-one-to-clear, self-clearing, read-only, or sequencing-sensitive. This generated header does not label those semantics; the consuming driver code and hardware programming guide determine safe access patterns.

## Dependencies And Integration Points

This chunk must match the DCN 3.1.2 generated register database and the companion offset file:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`
- SOC base-address headers such as `yellow_carp_offset.h`
- Register helper layers in AMD display and DMUB code that define field-access macros from the `__SHIFT` and `_MASK` constants.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

The integration pattern is field-table construction and token-pasted register access. `dcn31_resource.c` uses field macros for display block setup, including DWB, DMCUB/DMUB-assisted features, pipe/resource programming, and register helper accessors. `irq_service_dcn31.c` maps interrupt sources and uses the same register map for display IRQ status/ack plumbing. `dmub_dcn31.c` builds `dmub_srv_dcn31_regs` with both register offsets and `DMUB_DCN31_FIELDS()` shift/mask arrays, then uses those fields in reset, firmware loading, mailbox/ring, GPINT, scratch, and framebuffer-address translation paths.

## Risks And Edge Cases

- Generated macro drift is the central risk. A wrong shift or mask compiles as an integer constant but can silently read, clear, or update the wrong hardware bits.
- Interrupt destination and ack/status fields are side-effect-sensitive. Bad masks can misroute interrupts, leave sticky status uncleared, acknowledge unrelated events, or break vblank/vline/page-flip/hotplug/AUX/audio/DSC/HPO handling.
- The chunk starts in the middle of `DCPG_INTERRUPT_DEST`; file-level reconciliation must combine adjacent chunks before making complete claims about that register.
- DMCUB fields are high impact. Region windows, top/base/offset values, ring pointers, security/reset controls, fault addresses, scratch registers, and GPINT fields are involved in firmware boot and command exchange. Incorrect fields can cause firmware load failure, hangs, lost mailbox messages, or bad fault diagnosis.
- Power-gating fields interact with active display state. Incorrect domain config/status or DC IP request fields can leave blocks powered unexpectedly, gate active hardware, or break resume/low-power paths.
- DWB and DWBCP fields affect capture correctness. Incorrect window/source/update/output/color/LUT/gamut fields can produce corrupted writeback, wrong color, stale LUT values, CRC mismatches, overflow, or host-read failures.
- Perfmon fields are shared diagnostic infrastructure. Bad event selects, counter status, or ack masks can make performance data misleading or leave interrupts stuck.
- VGA fields are legacy but still risky for fallback and early boot paths; mistakes can disable memory access, blank syncs/de, change aperture addressing, or corrupt legacy display output.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled; missing or renamed macros should fail in `dcn31_resource.c`, `irq_service_dcn31.c`, and `dmub_dcn31.c`.
- Mechanically verify that each complete field in this line range has both a `__SHIFT` and `_MASK` definition, while allowing the known boundary split for `DCPG_INTERRUPT_DEST`.
- Compare this chunk against AMD's authoritative DCN 3.1.2 register database and adjacent generated headers where compatible fields are expected.
- Exercise DMCUB boot and reset paths: firmware backdoor load, code-window setup, inbox/outbox ring traffic, GPINT stop/ack, scratch registers, timer reads, fault reporting, and suspend/resume.
- Exercise IRQ paths: vblank, vline, page flip, hotplug and HPD RX, AUX/DDC, audio, DSC, HPO, perfmon, and power-transition interrupts. Watch for stuck, missing, or misrouted interrupts.
- Exercise power-management paths involving display-domain power gating, zero shutdown, memory power controls, deep sleep, and DC IP request/status handshakes.
- Test DWB capture with varied source sizes, output formats, alpha/depth packing, CRC, host reads, overflow/backpressure counters, and repeated update programming.
- Validate DWB color processing through gamut remap, HDR multiplier, output gamma LUT programming, and RAM A/RAM B curve selection.
- Run perfmon counter setup/read/interrupt tests for `DC_PERFMON3` and verify counter values and clear/ack behavior.
- Check legacy VGA behavior only where hardware and platform firmware still expose it: sequencer reset blanking, aperture/base addressing, cache invalidate, memory disable, and D1/D2 VGA control.

## Cross-Chunk Notes

Previous chunks own the beginning of the interrupt-destination field area, including the missing first `DCPG_INTERRUPT_DEST` shift in this range. Later chunks continue the VGA field block beyond `D2VGA_CONTROL` and cover the remaining DCN 3.1.2 mask namespace. The final per-file research document should merge adjacent chunks before making complete file-level claims about all interrupt fields, all DWB instances, or the full VGA register set.
