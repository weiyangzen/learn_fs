# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 37372-39766

## Purpose

This chunk is part of AMDGPU's generated DCN 3.1.6 register field mask header. It defines preprocessor constants for hardware register bit positions and masks; it does not contain executable C logic. The constants pair with `dcn_3_1_6_offset.h` address definitions so display code can construct register tables and access fields through AMDGPU register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_UPDATE`, and related macros.

The assigned range contains 2,171 `#define` entries: 1,080 `__SHIFT` values and 1,099 `_MASK` values. The range starts inside the tail of `DP2_DP_SEC_CNTL7`, where only remaining GSP active/idle masks are visible, and ends inside `DP4_DP_DPHY_SYM2`, after the symbol shift fields but before the matching masks appear in the next chunk.

## Covered Hardware Blocks

- `DP2` tail registers: secondary packet status/control for GSP1-GSP7, DP double-buffer controls, MSA/VBID override fields, secondary metadata transmission, DSC bytes-per-pixel, ALPM PHY sleep/standby, GSP8-GSP11 packet controls, and GSP enable double-buffer status.
- `DIG2` display encoder block: front-end control, output CRC, clock/test/random patterns, FIFO status, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffer status, HDMI audio clock regeneration values and status, AFMT selection, backend enable/control, TMDS controls, generated control bits, version, and force-disable.
- `DP3` DisplayPort stream encoder block: link status, pixel format, lane config, stream enable/disable interrupts, steer/TU FIFO status, video M/N timing, link framing, DPHY training/pattern/CRC/FEC/scrambler fields, DP secondary data/audio packet controls, MST/MSE slot allocation tables and status, MSA timing parameters, MSO controls, DSC control, metadata transmission, ALPM, GSP8-GSP11 controls, and GSP enable double-buffer status.
- `DIG3` display encoder block: the same broad DIG/HDMI/TMDS register surface as `DIG2`, for the next hardware instance.
- `DP4` beginning registers: link status, pixel format, lane config, stream control, FIFO overflow/status, MSA misc fields, DPHY internal controls, video M/N timing, link framing, HBR2 eye pattern, MSA/VBID placement, stream-disable interrupt fields, DPHY control/training fields, and the first DPHY symbol fields.

## Important APIs, Types, and Macros

The header exports only macros. Each field is represented by the generated naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register value space.

Important local consumers for this DCN 3.1.6 header include:

- `display/dmub/src/dmub_dcn316.c`, which includes `dcn_3_1_6_offset.h` and this file, then fills `dmub_srv_dcn316_regs` using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- `display/dc/resource/dcn316/dcn316_resource.c`, which includes this file and uses `SRI`, `SRII`, `SE_DCN3_REG_LIST`, `VPG_DCN31_REG_LIST`, `AFMT_DCN31_REG_LIST`, `APG_DCN31_REG_LIST`, and other list macros to build DCN 3.1.6 resource-register tables.
- Stream encoder definitions in `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`, where `SE_DCN3_REG_LIST` and `SE_COMMON_MASK_SH_LIST_DCN30` bind DIO stream encoder code to the `DIG*`, `DP*`, HDMI, TMDS, and secondary-packet fields represented here.
- VPG/AFMT definitions in `display/dc/dcn31/dcn31_vpg.h` and `display/dc/dcn31/dcn31_afmt.h`; while this chunk is mostly DIO/DIG/DP rather than VPG/AFMT payload storage, the same generated-mask mechanism is used by the DCN 3.1.6 resource file for adjacent packet-generation and audio-format blocks.

There are no functions, structs, enums, memory allocations, locks, syscalls, or direct error paths in this slice. The "API" surface is the compile-time set of register field identifiers.

## Control Flow and State

Runtime control flow is indirect. During compilation, resource and DMUB code expands these macros into arrays or structures of register offsets, masks, and shifts. At runtime, AMD display code uses those tables to read, modify, poll, or clear hardware register fields.

The state represented by this chunk is hardware state:

- DP stream state includes link-training completion/status, embedded-panel mode, lane count, pixel encoding/depth, stream enable/status, deferred stream disable, vblank/vupdate double-buffer state, MSA/VBID overrides, MSA timing, video M/N generator fields, DSC bytes-per-pixel, MSO selection, MST/MSE slot allocation tables, and secondary packet enable/send state.
- HDMI/DIG state includes encoder source selection, stereosync, display color depth, TMDS encoding, Dolby Vision metadata status, output CRC, test/random patterns, FIFO underflow/overflow/status, HDMI keepout, deep-color enable, generic packet send/continuous/immediate-send state, packet line numbers, ACR source/select values, and HDMI double-buffer pending/taken flags.
- DPHY state includes training pattern selection, HBR2 eye pattern enable, FEC enable/readiness/active status, scrambler selection, bypass/skew-bypass, custom symbol values, PRBS/scrambler control, CRC enable/control/result, fast-training lane/ack state, and bit/symbol swap controls.
- Interrupt and clear/ack state appears in stream-disable interrupts, steer/TU FIFO overflow ack, HDMI audio-enable change ack, secondary packet missed/overflow bits, metadata transmission missed clear bits, and generic-packet deadline status.
- Power-management and low-power timing state appears in ALPM PHY sleep/standby send/pending/immediate controls and line-number fields.

Hardware fields persist in MMIO/register state until changed by the driver, reset by display hardware sequencing, or affected by power-gating/reset. Pending/taken/status fields are synchronized with hardware update points such as vupdate, packet send timing, stream enable/disable sequencing, or link-training events.

## Dependencies and Integration Points

This file must remain exactly aligned with DCN 3.1.6 hardware layout and with the companion `dcn_3_1_6_offset.h` register address header. A correct field name is not sufficient: its bit position and mask must also match the ASIC register definition for the relevant DIO/DIG/DP instance.

The repeated instance prefixes are integration-critical. `DIG2` and `DIG3` represent separate display encoder instances. `DP2`, `DP3`, and `DP4` represent separate DisplayPort stream/link-facing blocks. The resource layer selects concrete instances through offset-list macros, while common object code often uses shared mask/shift structures whose field names are generated from a representative instance.

Downstream integration paths include DC resource-pool construction for DCN 3.1.6, DMUB service register access, DIO stream encoder programming, HDMI audio and packet programming, DP link training, DP MST/MSO/DSC programming, vblank/vupdate double-buffer update paths, hotplug/IRQ handling, and display suspend/resume or power-management sequences.

## Risks and Edge Cases

- A wrong shift or mask can compile cleanly while programming the wrong hardware bits. Likely symptoms include blank displays, failed DP link training, broken HDMI/DP infoframes, missing HDR/metadata packets, bad audio clock regeneration, corrupted TMDS control patterns, MST slot-allocation errors, DSC setup failures, or spurious display interrupts.
- This chunk has split register definitions at both boundaries. `DP2_DP_SEC_CNTL7` began in the prior chunk, and `DP4_DP_DPHY_SYM2` continues in the next chunk. The merge lane should treat these as boundary artifacts rather than complete-register omissions in the whole-file report.
- Status and clear fields are mixed with control fields in the same generated namespace. Fields ending in `ACK`, `CLR`, or clear-like names may have write-one-to-clear hardware semantics; generic read-modify-write paths must avoid accidentally asserting them.
- Pending/taken/deadline fields depend on display timing. Polling code needs bounded waits and must account for disabled streams, missed vblank/vupdate windows, and power-gated or reset blocks.
- Line-number and slot-allocation fields have fixed masks. Out-of-range values may be truncated before write, producing subtle packet timing failures that surface only as deadline-missed or packet-missed status.
- Instance-copy mistakes are easy in generated headers. A stale `DIG2`/`DIG3` or `DP3`/`DP4` field can still look structurally valid but bind a resource table to the wrong hardware instance.

## Test and Validation Signals

- Kernel build coverage for DCN 3.1.6 display and DMUB code should catch missing macro names in `dmub_dcn316.c`, `dcn316_resource.c`, stream encoder headers, and related register-table initialization.
- Compile-time expansion of `FD_MASK`, `FD_SHIFT`, `SRI`, `SRII`, `SE_DCN3_REG_LIST`, `SE_COMMON_MASK_SH_LIST_DCN30`, `VPG_DCN31_REG_LIST`, and `AFMT_DCN31_REG_LIST` is the first validation that this header remains name-compatible with the driver.
- Display smoke tests should include DP and HDMI mode sets, stream enable/disable, vblank/vupdate programming, suspend/resume, hotplug, and link retraining across the affected encoder instances.
- Feature tests should cover DP link training, FEC, MST/MSE slot allocation, MSO, DSC, ALPM transitions, HDMI audio, ACR values, generic packets, infoframes, HDR/metadata packets, output CRC/test pattern paths, and TMDS modes.
- Useful runtime diagnostics are link-training status, stream-disable interrupt/ack state, FIFO overflow bits, DP secondary packet missed/deadline status, GSP enable pending bits, HDMI generic packet pending/deadline fields, ACR status, DPHY CRC results, and ALPM sleep/standby pending bits.
