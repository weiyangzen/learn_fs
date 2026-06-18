# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h

Chunk: `subset-b-001578`
Covered source range: lines 7969-10476 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

## Purpose

This chunk is part of a generated AMD DCN 1.0 MMIO register offset header. It contains preprocessor constants only; there are no executable functions, structs, enums, or storage objects. Its purpose is to publish register addresses and register-base-index selectors used by AMDGPU display code when programming DCN 1.0 display I/O, stream encoder, link encoder, AUX, and DCIO global hardware blocks.

The source tree path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The covered range starts inside the `dce_dc_dio_dp_aux1_dispdec` address block. Lines 7969-7986 provide the tail of `DP_AUX1` DPHY and GTC sync offsets; the earlier `DP_AUX1_AUX_CONTROL`, software-control, arbitration, interrupt, status, and data offsets are in the previous chunk. The range then covers:

- complete DisplayPort AUX instance blocks `DP_AUX2` through `DP_AUX6`;
- DIO digital/HDMI/audio-format/TMDS blocks `DIG0` through `DIG6`;
- DisplayPort link/stream/secondary-packet blocks `DP0` through `DP6`;
- the global `DCIO` block containing generic display I/O controls, UNIPHY crossbar/link controls, LVTMA power sequencing, backlight PWM, genlock/swaplock pads, impedance calibration, DPCS interrupts, semaphores, and USB-C flip selection.

The chunk ends cleanly at `mmDCIO_USBC_FLIP_EN_SEL_BASE_IDX`. The next chunk begins after this DCIO block.

## Important APIs, Types, And Macros

There are no C APIs in this header section. The public interface is the generated offset macro convention:

- `mm<REGISTER>` gives the register's MMIO offset within the selected ASIC register aperture.
- `mm<REGISTER>_BASE_IDX` gives the base-segment selector used by SOC15 register helpers. Every macro in this chunk uses base index `2`.
- Register prefixes identify repeated hardware instances: `DP_AUX1..6`, `DIG0..6`, `DP0..6`, `UNIPHYA..G`, and global `DC`, `DCIO`, `LVTMA`, `BL`, `AUXP`, and `AUXN` registers.

Important macro families in this chunk include:

- `mmDP_AUX1_AUX_DPHY_*` and `mmDP_AUX1_AUX_GTC_SYNC_*`: the tail of AUX instance 1, covering DPHY TX/RX control/status and GTC sync status/control offsets.
- `mmDP_AUX2..mmDP_AUX6_AUX_*`: full AUX controller instance offsets for software transaction control/status/data, AUX arbitration, interrupts, line-status capture, DPHY TX/RX tuning/status, and GTC sync controller/error/status registers.
- `mmDIG0..mmDIG6_DIG_*`: digital encoder front-end and back-end control, output CRC, clock/test/random patterns, FIFO status, version, lane enable, and DIG back-end enable/control offsets.
- `mmDIG0..mmDIG6_HDMI_*`: HDMI control/status, audio packet, ACR packet and CTS/N values, VBI packet controls, infoframe controls, generic packet controls, GCP/AVMUTE, data-block control, and related status offsets.
- `mmDIG0..mmDIG6_AFMT_*`: audio-format and infoframe packet metadata, ISRC packets, MPEG/generic packet payload/header registers, audio info/channel-status registers, audio CRC, ramp controls, audio source selection, and VBI/infoframe packet-control offsets.
- `mmDIG0..mmDIG6_TMDS_*`: TMDS control, control-character, sync-character pattern, stereosync, generated control bits, feedback, and DC balancer offsets.
- `mmDP0..mmDP6_DP_*`: DisplayPort link control, pixel format, MSA colorimetry/timing/misc/VBID, stream control, timing M/N values, link framing, DPHY control/training/scrambler/CRC/fast-training, secondary-data packet controls, audio M/N/readback, timestamp, MST stream allocation table registers, MSO, DSC, data-block control, and extended secondary-packet controls.
- `mmDC_*`, `mmDCIO_*`, `mmUNIPHY*`, `mmLVTMA_*`, and `mmBL_*`: global display I/O controls for reference clocks, GPIO debug, pin straps, DVO data, panel power sequencing, backlight PWM, genlock/swaplock pads, clocking, soft reset, DPHY selection, impedance calibration, DPCS interrupts, eight DCIO semaphores, and USB-C flip enable selection.

The matching field masks and shifts are in the companion `dcn_1_0_sh_mask.h` header. Consumers pair these offset macros with field macros through AMD display register helper tables.

## Control Flow

This chunk has no internal control flow. Every meaningful line is a `#define` consumed by C preprocessor substitution.

Runtime control flow is in the AMD display code that builds register tables from these macros:

1. DCN 1.0 modules include `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. Table-building macros such as `SRI(...)` concatenate a block name, instance id, and register name, then add the SOC15 base segment selected by `mm..._BASE_IDX`.
3. Object constructors store the resulting offsets in typed register tables such as `struct dcn10_link_enc_registers`, `struct dcn10_link_enc_aux_registers`, and `struct dcn10_stream_enc_registers`.
4. Runtime paths call register helpers such as `dm_read_reg`, `generic_reg_update`, and related DC helper macros to read, modify, write, or poll hardware registers.

Concrete local integration paths include:

- `display/dc/dio/dcn10/dcn10_link_encoder.h` builds AUX, DIG, TMDS, and DP link-encoder register lists using `SRI(AUX_CONTROL, DP_AUX, id)`, `SRI(DIG_BE_CNTL, DIG, id)`, `SRI(DP_LINK_CNTL, DP, id)`, `SRI(DP_DPHY_CNTL, DP, id)`, `SRI(DP_MSE_SAT*, DP, id)`, and related macros defined in this chunk.
- `display/dc/dio/dcn10/dcn10_link_encoder.c` programs output setup, DP link training patterns, lane settings, MST allocation tables, PSR fast training, secondary packets, AUX receiver controls, and output disable/enable paths through the register tables derived from this chunk.
- `display/dc/dio/dcn10/dcn10_stream_encoder.h` maps DIG/HDMI/AFMT and DP stream registers such as `DIG_FE_CNTL`, `DIG_FIFO_STATUS`, `HDMI_CONTROL`, `AFMT_*`, `DP_PIXEL_FORMAT`, `DP_SEC_CNTL*`, `DP_VID_M/N`, `DP_MSA_*`, `DP_MSE_RATE_*`, and `DP_DB_CNTL`.
- `display/dc/irq/dcn10/irq_service_dcn10.c` includes this offset header with the companion mask header and uses the same base-index/address convention while mapping DCN 1.0 interrupts to DAL IRQ sources.
- Resource construction in DCN 1.0 display code uses these register-list macros to instantiate per-link and per-stream hardware objects for up to seven digital link encoders.

The header itself does not express sequencing. Consumers must perform the correct hardware order around stream enable, link training, AUX transactions, HPD/link ownership, PLL/PHY setup, packet update pending bits, resets, and power-domain state.

## State And Persistence Behavior

The header is stateless. It does not allocate memory, perform I/O, or persist data. Its macros become compile-time constants in driver objects.

The hardware registers addressed by these macros represent state that persists in GPU display hardware until changed by driver writes, firmware, hotplug activity, link retraining, power management, display block reset, suspend/resume, or GPU reset. State categories represented in this chunk include:

- AUX controller state: software transaction buffers, transaction start/control, arbitration ownership, interrupt state, line-status/error capture, DPHY TX/RX tuning and status, and GTC sync status.
- DIG and HDMI state: front-end source/start, back-end enable/mode, clock/test patterns, FIFO status, lane enable, HDMI packet generation, deep color, data scrambling, generic packets, infoframes, AVMUTE, and audio packet controls.
- AFMT/audio state: audio source selection, channel status words, 60958 data, audio CRC, ISRC/MPEG/generic packet contents, ramp controls, VBI packet state, and frame/immediate packet update behavior.
- DP link and stream state: link training completion/status, lane configuration, DPHY training pattern/symbol/scrambler/CRC/fast-training controls, video stream enable/status, M/N timing generation, MSA timing/colorimetry/VBID values, secondary packet scheduling, audio M/N values, MST stream allocation table slots/status, DSC/MSO controls, and data-block controls.
- DCIO global state: reference-clock and clock-control selection, soft reset, DPHY selection, UNIPHY crossbar routing, panel power sequencing, backlight PWM timing/lock state, impedance calibration controls, DPCS interrupt latches, global semaphores, and USB-C flip routing.

Access type and side effects are not encoded here. Some registers are durable configuration bits; others are read-only status, sticky interrupt/status bits, write-one-to-clear/acknowledge bits, self-clearing update requests, or power-domain-gated registers. The generated names hint at behavior (`*_STATUS`, `*_CONTROL`, `*_CNTL`, `*_INTERRUPT`, `*_READBACK`, `*_UPDATE`, `*_SOFT_RESET`, `*_SEMAPHORE`), but callers must rely on the register specification and existing DC helper sequences.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor and the AMD generated-register naming scheme. Practical dependencies include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h` for the bit masks and shifts matching the offsets in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_hw_ip.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_ip_offset.h` for SOC15 base segment metadata used with `_BASE_IDX`.
- AMD display register helpers and table macros, especially `SRI`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `dm_read_reg`, and generic register update/read helpers.
- DCN 1.0 DIO/link/stream encoder code under `display/dc/dio/dcn10/`.
- DCN 1.0 IRQ service under `display/dc/irq/dcn10/`.

The instance layout is a key integration contract. The chunk defines seven DIG/DP instances (`0..6`) with regular 0x100 register-spacing in the generated offsets, and seven AUX-visible instance numbers across the file (`0..6`, with this chunk containing the tail of `1` and full `2..6`). Consumers often write field/mask tables against instance `0` names, then use `SRI` and instance ids to select the matching offset. If the repeated offsets drift, generic per-instance code can silently program the wrong physical encoder or link.

The `DCIO` block integrates across several display subsystems rather than one stream: UNIPHY link routing, DPHY selection, panel/backlight sequencing, genlock/swaplock pad control, impedance calibration, DPCS interrupt reporting, semaphores, and USB-C flip routing affect link encoders, GPIO/HPD routing, panel power, and low-level PHY bring-up.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong offset or base index can compile cleanly while reading or writing an unrelated MMIO register.
- The chunk starts mid-block. `DP_AUX1` is incomplete here; final file-level reconciliation must merge this chunk with the previous chunk before treating AUX1 as fully described.
- The repeated `DIG0..6`, `DP0..6`, and `DP_AUX2..6` definitions are highly regular. A single copied instance number, address, or base-index error can affect only one connector path and may appear as a port-specific black screen, AUX timeout, audio failure, MST failure, or bad link-training behavior.
- `DIG` and `DP` blocks share an instance id and base address comments, but they are separate register families. Mixing a DIG address with a DP mask/field table, or vice versa, is not type-checked by C.
- AUX DPHY and DP DPHY controls are timing- and board-sensitive. Incorrect offsets can cause intermittent EDID/DPCD failures, link-training failures, PSR failures, MST sideband instability, or hotplug/link recovery problems that are hard to reproduce.
- HDMI/AFMT packet registers are protocol-sensitive. Wrong offsets can corrupt infoframes, audio channel status, ACR values, generic packet payloads, AVMUTE behavior, or deep-color/scrambling setup while the display link otherwise appears active.
- DP secondary-packet, MSA, M/N, MST allocation, MSO, and DSC registers are mode-sensitive. Misprogramming can break high-bandwidth modes, audio, MST topologies, DSC-enabled modes, or data-block-disable behavior without affecting simpler modes.
- DCIO global registers have broad blast radius. Soft reset, DPHY selection, UNIPHY crossbar, impedance calibration, panel power sequencing, PWM, semaphores, and USB-C flip selection can affect multiple connectors or the whole display I/O fabric.
- The header does not encode register access restrictions, locking, reserved bits, reset values, or power-domain requirements. Callers must use established helper paths rather than ad hoc MMIO writes.

## Test Signals

Useful validation signals include:

- compile coverage for DCN 1.0 display code that includes `dcn_1_0_offset.h`, especially `irq_service_dcn10.c`, `dcn10_link_encoder.c`, `dcn10_link_encoder.h`, `dcn10_stream_encoder.c`, `dcn10_stream_encoder.h`, and DCN 1.0 resource construction files;
- generated-header consistency checks ensuring every `mm<REGISTER>` used by `SRI` register-list macros exists with a matching `_BASE_IDX`, and every referenced field in `dcn_1_0_sh_mask.h` has a matching address macro in this offset header;
- per-instance duplicate-pattern checks across `DIG0..6`, `DP0..6`, and `DP_AUX2..6` to verify intended register spacing and to catch a single bad copied address;
- hardware smoke tests across every physical connector path, including modeset, blank/unblank, stream enable/disable, suspend/resume, and rapid hotplug;
- DisplayPort tests for DPCD/EDID AUX reads, link training at all supported link rates/lane counts, test patterns, scrambler/training-pattern changes, PSR fast training, MST stream allocation, audio over DP, DSC/MSO modes where supported, and link recovery after disconnect;
- HDMI/DVI tests for TMDS output, deep color, scrambling, audio packets, ACR values, AVI/audio/vendor/generic infoframes, AVMUTE, and mode switches between common pixel formats;
- debug/readback checks for FIFO status, DPHY CRC/status, MSE SAT status, audio M/N readback, AFMT status, DPCS interrupts, DCIO semaphores, backlight PWM readback, and panel power sequencing state;
- negative signals in logs or display behavior: AUX timeouts, HPD/RX IRQ anomalies, link-training retries, black screens, missing audio, corrupted infoframes, MST payload failures, underflow/FIFO errors, stuck packet-update pending bits, bad backlight/panel sequencing, or failures limited to one encoder instance.
