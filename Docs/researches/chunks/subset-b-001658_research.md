# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 4727-7156

## Purpose

This chunk is part of AMDGPU's generated DCN 2.1 register field shift/mask header. It contains no executable C logic; it publishes compile-time bit layout constants for DCN display hardware registers. Each field is exposed as paired preprocessor macros: `REGISTER__FIELD__SHIFT` gives the low bit position and `REGISTER__FIELD_MASK` gives the already-positioned bit mask used by AMD display register helpers.

The assigned range starts in the middle of `DMU_INTERRUPT_DEST` and then covers a large set of DCN 2.1 display interrupt-routing, writeback, memory-interface, performance-monitor, MMHUBBUB/VGAIF, and HDA Azalia stream fields:

- Interrupt destination registers for DMU/DMCUB, DCPG power domains, MMHUBBUB, writeback, DCHUB, DPP perf counters, MPC, OPP, OPTC, OTG0 through OTG5, DIG, I2C/DDC/HPD, DIO/DCIO, HPD, audio/Azalia, AUX, and DSC blocks.
- DWB/CNV writeback capture fields for writeback enable, clock/power configuration, crop/window/source dimensions, capture rate, stereo/new-content bits, update locking/status, test CRCs, debug access, soft reset, and warmup programming.
- WBSCL writeback scaler fields for coefficient RAM addressing/data, scaler mode, taps, destination size, horizontal/vertical ratios and initial phases, rounding/clamping, overflow and host-conflict interrupt status/ack/mask bits, CRC/debug, backpressure counters, and outside-pixel strategy.
- `DC_PERFMON3` and `DC_PERFMON4` fields for writeback/MMHUBBUB performance counter control, counter state, monitor control, captured values, interrupt status/ack, and readback selection.
- `MCIF_WB0` and `MCIF_WB1` fields for writeback buffer-manager control/status, buffer addresses and offsets, pitches, dimensions, buffer status, arbitration, SCLK/p-state/self-refresh behavior, VCE coordination, watermarks, QoS, security, and high address bits.
- MMHUBBUB/VGAIF fields for WBIF control, SMU watermark control, outstanding counters, VGA split source, memory power status/control, clock gating, soft reset, DMU interface error status, and client-unit ID.
- HDA Azalia stream indexed register access for stream instances 0 through the first line of stream 7 in this chunk.

Although the repository path is under a `ceph-client` source tree, this chunk is AMD GPU display hardware metadata. It has no Ceph protocol behavior, distributed filesystem state, block I/O path, or storage persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or global objects defined in this chunk. The public surface is the generated macro namespace consumed by display driver register tables.

Important macro families include:

- `DMU_INTERRUPT_DEST__*`: routes DMCUB timers, GPINTs, inbox/outbox events, perfmon interrupts, ABM events, undefined-address faults, RBBMIF timeouts, DMCU internal interrupts, and SCP interrupts toward interrupt handling destinations.
- `DCPG_INTERRUPT_DEST*__*`: describes power-up and power-down interrupt destination bits for DCPG domains 0 through 21, split between `DCPG_INTERRUPT_DEST` and `DCPG_INTERRUPT_DEST2`.
- `*_INTERRUPT_DEST__*`: field layouts for display interrupt routing across MMHUBBUB, WB/WBSCL, DCHUB, DCHUB perf counters, DPP perf counters, MPC, OPP, OPTC, OTG, DIG, DDC/HPD, DIO/DCIO, Azalia, AUX, and DSC. These route many classes of hardware events before normal IRQ source decoding sees them.
- `WB_ENABLE`, `WB_EC_CONFIG`, `WB_SOFT_RESET`, `WB_WARM_UP_MODE_CTL1`, and `WB_WARM_UP_MODE_CTL2`: enable, power/clock, reset, and warmup fields for the display writeback block.
- `CNV_MODE`, `CNV_WINDOW_START`, `CNV_WINDOW_SIZE`, `CNV_UPDATE`, `CNV_SOURCE_SIZE`, `CNV_TEST_*`, `WB_DEBUG_CTRL`, `WB_DBG_MODE`, `WB_HW_DEBUG`, and `CNV_TEST_DEBUG_*`: writeback converter and capture-control metadata for source sizing, cropping, output depth, frame capture, stereo/interlaced mode, update locking, CRC signatures, and debug indexing.
- `WBSCL_*`: writeback scaler metadata for coefficient RAM programming, output format/depth, tap counts, destination size, scale ratios, initial phases, rounding, overflow/host-conflict handling, CRC/debug, clamping, backpressure, and outside-pixel behavior.
- `DC_PERFMON3_*` and `DC_PERFMON4_*`: generic performance-monitor fields for event selection, compare/count modes, run/stop/restart control, interrupt enable/status/ack, counter state, captured-value high/low readback, and monitor state.
- `MCIF_WB0_*` and `MCIF_WB1_*`: memory-client interface writeback fields for buffer manager enable/lock/interrupts, VMID/fencing/security, current line/status, per-buffer tiling/rotation/burst/packing/address/pitch/resolution, arbitration, watermarks, p-state/self-refresh, QoS, VCE handshake, and 64-bit address high halves.
- `WBIF0_*`, `MMHUBBUB_*`, `MCIF_*`, `DMU_IF_ERR_STATUS`, and `MMHUBBUB_CLIENT_UNIT_ID`: MMHUBBUB and VGAIF fields for memory power/clock/reset control, write-combine controls, outstanding counters, client identifiers, and DMU interface error state.
- `AZF0STREAM[0-6]_AZALIA_STREAM_INDEX`, `AZF0STREAM[0-6]_AZALIA_STREAM_DATA`, and the first `AZF0STREAM7_AZALIA_STREAM_INDEX` field in this range: indexed HDA stream register access fields, with an 8-bit index, write-enable bit, and 32-bit data payload for completed stream instances.

These constants are normally paired with address macros from `dcn_2_1_0_offset.h`. Runtime register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `FN`, and `FD` combine an address with the shift/mask pair to pack or extract a field value.

## Control Flow

This header chunk has no runtime control flow. It influences runtime behavior when included by DCN 2.1 code that builds register tables and manipulates hardware registers.

A typical control path is:

1. DCN 2.1 resource setup includes `dcn_2_1_0_offset.h` and this shift/mask header.
2. Per-block register tables select addresses for a hardware instance, often through macros such as `SR`, `SRI`, `SRI2_DWB`, or `SRI_DMUB`.
3. Matching shift and mask tables are initialized from the generated `*_SHIFT` and `*_MASK` macros.
4. Operational code calls register helpers such as `REG_UPDATE(CNV_MODE, CNV_FRAME_CAPTURE_EN, ...)` or `REG_GET(CNV_UPDATE, CNV_UPDATE_LOCK, ...)`.
5. The helper uses the field shift and mask from this header to update or read the correct bits in a memory-mapped hardware register.

The main behavioral control sequences represented by this chunk are interrupt routing, writeback capture setup, writeback scaler programming, MCIF writeback buffer operation, performance-monitor setup/readback, MMHUBBUB power/clock/reset control, and Azalia stream indexed access. The macros do not encode sequencing rules; those are enforced by consumers such as DWB code, IRQ service code, resource construction, DMUB support, and audio code.

For writeback specifically, `dcn20_dwb.c` uses these field names through `struct dcn20_dwbc_shift` and `struct dcn20_dwbc_mask`. It enables `WB_ENABLE`, programs `CNV_SOURCE_SIZE`, crop window fields, capture rate/depth, `WBSCL_MODE`, destination size, taps, ratios, init phases, rounding, clamping, and outside-pixel strategy, then enables capture through `CNV_FRAME_CAPTURE_EN`. Updates may lock `CNV_UPDATE_LOCK` while changing CNV/WBSCL fields. Disable clears frame capture and writeback enable, then toggles `WB_SOFT_RESET`.

For interrupts, `irq_service_dcn21.c` includes this file and uses generated masks in `IRQ_REG_ENTRY` style tables. The chunk's interrupt destination fields are lower-level routing metadata, while the IRQ service maps source IDs and context IDs to DAL interrupt sources such as vblank, vline, page flip, HPD, HPD RX, vupdate, and DMCUB outbox.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It describes state held in DCN 2.1 hardware registers.

The represented hardware state includes:

- Interrupt routing and interrupt status/control bits for many display blocks.
- Writeback enablement, capture mode, crop/source/window geometry, update lock/pending/taken bits, stereo/interlace/new-content flags, test CRC results, debug selectors, soft reset, and warmup programming.
- Writeback scaler coefficient RAM contents/selectors, scaler mode, tap counts, destination size, ratios, initial phases, rounding, clamps, outside-pixel strategy, backpressure counters, overflow flags, host-conflict flags, and acknowledgements.
- MCIF writeback buffer manager state, current line, buffer availability/active/overrun/frame-captured status, buffer addresses and dimensions, pitch, tiling/swap/rotation metadata, VMID/fence/security level, watermarks, arbitration, p-state controls, self-refresh, and QoS.
- Performance monitor configuration, active/run/restart state, counted values, compare/counter-off behavior, interrupt status/ack bits, and high/low readback registers.
- MMHUBBUB power, clock, soft-reset, memory-power, outstanding-counter, write-combine, client ID, and DMU interface error state.
- Azalia stream indexed-register address/data state.

Persistence is entirely hardware-defined. Some fields are latched programming values that remain until reprogrammed, reset, power-gated, or overwritten during a modeset. Some fields are live status bits. Some are sticky interrupt/status bits that require explicit acknowledgement. Some are request, lock, update, or reset bits whose effects depend on hardware timing. This generated header does not indicate which fields are read-only, write-one-to-clear, self-clearing, double-buffered, or safe to change while active.

## Dependencies And Integration Points

The companion address header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`. The shift/mask constants in this chunk are only meaningful when paired with those register addresses and the DCN base offset macros from `renoir_ip_offset.h`.

Direct DCN 2.1 include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`

The most direct integration point for the writeback section is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h`, which defines `DWBC_COMMON_REG_LIST_DCN2_0` and `DWBC_COMMON_MASK_SH_LIST_DCN2_0`. Those lists map the generated `WB_*`, `CNV_*`, and `WBSCL_*` macros into `struct dcn20_dwbc_registers`, `struct dcn20_dwbc_shift`, and `struct dcn20_dwbc_mask`. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.c` then uses those tables to implement `dwb2_enable`, `dwb2_disable`, `dwb2_update`, `dwb2_is_enabled`, `dwb2_set_stereo`, `dwb2_set_new_content`, `dwb2_set_warmup`, and scaler setup.

Resource construction in `dcn21_resource.c` includes this generated header and constructs DCN 2.1 block register, shift, and mask tables for clock sources, DMCU/ABM/audio/DCCG/OPP/timing generators, DPP/HUBP/HUBBUB, DWB, GPIO, AUX/I2C, link encoders, and related display objects. This chunk contributes fields for several of those tables, especially DWB and audio/interrupt-related surfaces.

The DMCUB/DMUB integration includes this header in `dmub_dcn21.c`; DMUB register helpers use `FD_MASK` and `FD_SHIFT` to populate common DMUB field layouts. The chunk's `DMU_INTERRUPT_DEST` fields are adjacent to DMUB/DMCUB event routing, while common DMUB enable/ack registers are handled elsewhere in the generated file.

The audio integration uses Azalia register index/data fields through display audio code and resource tables. This chunk covers per-stream indexed access fields for streams 0 through 6 and begins stream 7; the rest of stream 7 is outside this chunk and should be covered by the following chunk.

## Risks And Edge Cases

- Generated-header drift is high risk: a wrong shift or mask compiles cleanly but writes the wrong hardware bits, causing silent display, capture, interrupt, power, audio, or diagnostic failures.
- This chunk starts and ends mid-register-family. `DMU_INTERRUPT_DEST` begins before line 4727, and `AZF0STREAM7_AZALIA_STREAM_INDEX` continues after line 7156. Any per-file summary must reconcile adjacent chunks before treating those families as complete.
- Interrupt destination fields are easy to confuse with interrupt enable, ack, and status fields. Destination routing mistakes can make otherwise-correct IRQ enable/ack code ineffective.
- MCIF writeback fields touch addresses, VMID, security, fencing, buffer status, arbitration, and p-state/self-refresh behavior. Bad masks here can lead to memory writeback corruption, hangs, overrun status storms, or security-domain mistakes.
- WBSCL coefficient and update fields are timing sensitive. Programming coefficient RAM or scaler geometry while the wrong buffer is active can cause host-conflict flags, visual corruption in captured frames, or stale scaler state.
- Some status and ack fields share registers with control bits. Consumers must preserve unrelated bits and use the correct write semantics; this header only supplies bit geometry.
- The writeback code has capability checks that reject luma scaling in DCN2-era DWB paths, but the register fields still expose scaler programming. Tests should distinguish unsupported policy from missing field definitions.
- Performance-monitor fields have repeated layouts across `DC_PERFMON3` and `DC_PERFMON4`; instance mix-ups can read or arm the wrong counter block.
- HDA Azalia stream registers use indexed access. Wrong index/write-enable masks can target the wrong indirect register even if the data register field is correct.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver runtime checks:

- Build coverage for DCN 2.1 display code that includes `dcn_2_1_0_sh_mask.h`, especially `dcn21_resource.c`, `irq_service_dcn21.c`, GPIO translation/factory code, and `dmub_dcn21.c`.
- Compile-time initialization of DWB register, shift, and mask structs from `DWBC_COMMON_MASK_SH_LIST_DCN2_0`; missing or renamed macros should fail the build.
- Runtime DWB smoke tests: enable capture, program source/crop/window geometry, toggle `CNV_UPDATE_LOCK`, program WBSCL mode/taps/ratios, enable frame capture, verify `dwb2_is_enabled`, then disable and check `WB_SOFT_RESET` behavior.
- Captured-frame validation for DWB crop, output depth, stereo/new-content paths, WBSCL clamping, outside-pixel strategy, and scaler coefficients when supported.
- WBSCL diagnostic checks for overflow and host-conflict flags/ack/mask behavior under stress or deliberately invalid coefficient programming.
- MCIF writeback tests that verify buffer address high/low programming, pitch/resolution, frame-captured/buffer-active status, overrun handling, watermarks, and backpressure counters.
- IRQ tests for vblank, vline, page flip, HPD/HPD RX, vupdate, DMCUB outbox, AUX, DSC, and DWB-related interrupt delivery, with attention to destination routing versus enable/ack masks.
- Perfmon tests that arm counters, select events, read high/low captured values, and verify counter interrupt status/ack for `DC_PERFMON3` and `DC_PERFMON4`.
- Suspend/resume, modeset, power-gating, and ASIC-reset tests that reinitialize MMHUBBUB, DWB, MCIF, interrupt, and Azalia stream fields without relying on stale hardware state.
