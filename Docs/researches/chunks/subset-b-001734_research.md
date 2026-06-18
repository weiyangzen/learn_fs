# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 29756-32176

## Scope

This chunk is a generated AMD DCN 3.0.1 ASIC register bitfield header segment. It contains preprocessor constants only: for each hardware register field, one `__SHIFT` macro gives the bit offset and one `_MASK` macro gives the bit mask. The chunk spans 2,421 source lines and includes 1,083 shift/mask pairs. It starts in the tail of the `DIG0` TMDS/DIG block and ends in the middle of the `DP1_DP_ALPM_CNTL` field list, so the file-level merge must reconcile this chunk with neighboring chunks for complete register coverage.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN display I/O MMIO programming. Driver code elsewhere can build, mask, read, or update register fields without open-coded numeric constants. The covered register groups are display encoder front/back end (`DIG0` tail and `DIG1`), DisplayPort stream/link/PHY/secondary-data registers (`DP0` and `DP1`), video packet generator registers (`VPG1`), audio formatter registers (`AFMT1`), and metadata engine registers (`DME1`).

The chunk is data-like source rather than executable logic. Its correctness depends on exact alignment with AMD hardware register specifications and with companion register-address headers for the same ASIC/IP version.

## Address Blocks And Register Surface

Visible address blocks:

- `dce_dc_dio_dp0_dispdec`: full `DP0` DisplayPort mask set from link control through GSP enable double-buffer status.
- `dce_dc_dio_dig1_vpg_vpg_dispdec`: `VPG1` generic packet, MPEG/ISRC data, update, status, and memory-power masks.
- `dce_dc_dio_dig1_afmt_afmt_dispdec`: `AFMT1` HDMI/DP audio formatter packet, IEC 60958 channel status, CRC, ramp-test, status, source, and memory-power masks.
- `dce_dc_dio_dig1_dme_dme_dispdec`: `DME1` metadata engine control and memory-power masks.
- `dce_dc_dio_dig1_dispdec`: `DIG1` encoder, HDMI packet/control, ACR, AFMT clock, TMDS, lane, and force-disable masks.
- `dce_dc_dio_dp1_dispdec`: `DP1` DisplayPort masks, mirroring most of `DP0`, through the partial `DP1_DP_ALPM_CNTL` section at this chunk boundary.

The chunk also includes the final `DIG0` definitions for TMDS DC balancer, sync DC-balance characters, DIG version, lane enables, and force-disable state.

## Important Macros And Register Families

`DIG0_*` and `DIG1_*` define digital encoder controls. Important fields include source selection, stereosync routing, start gating, digital bypass, input pixel selection, Dolby Vision enable/missed metadata indication, symbol-clock status, TMDS pixel/color format, output CRC control/result, FIFO status, HDMI metadata packet enable/line/missed state, HDMI scrambling/deep-color/error state, ACR packet fields, generic packet controls, double-buffer state, backend mode/HPD selection, lane enables, and force-disable controls.

`DP0_*` and `DP1_*` define DisplayPort link and stream controls. They cover link training completion/status, embedded-panel mode, pixel encoding/component depth/combine mode, MSA colorimetry/misc/timing/VBID fields, lane count, video stream enable/status/deferred disable/keepout, steer FIFO overflow and transfer-unit overflow status, M/N timing values, framing, HBR2 eye pattern, video interrupts, DPHY control/training/symbol/8b10b/PRBS/scrambler/CRC/MST CRC/fast-training fields, secondary packet enables and line references, audio M/N and readbacks, timestamp, packet control, MST stream allocation table (`MSE_SAT*`) programming/status, MSO secondary stream enables, DSC mode/slice width/bytes-per-pixel, metadata transmission, generic secondary packet (`GSP8`-`GSP11` for `DP0`), double-buffer control, and ALPM sleep/standby request state.

`VPG1_*` defines the video packet generator surface for generic packet access/data, GSP frame-update and immediate-update triggers for packets 0 through 14 plus Dolby Vision and HDR10 control points, generic packet pending/status, memory power state, ISRC packet access/data, and MPEG info payload bytes.

`AFMT1_*` defines audio formatter fields: VBI packet control, audio sample packet layout and HBR/flat-line/override controls, HDMI audio infoframe byte fields, IEC 60958 channel status words, audio CRC source/channel/count/result, ramp test counters, audio enable/HBR/FIFO-overflow/status-change flags, sample-send/test/channel-swap/update/ack fields, infoframe source/update controls, audio source select, and memory power.

`DME1_*` defines metadata engine control, including HUBP requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable state, and DME memory power state/default low-power state.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: display driver code includes this header and uses these macros with register-access helpers, usually through generated `*_SHIFT`/`*_MASK` tables or macros, to program MMIO registers.

The hardware-oriented flows represented by the bitfields are:

- Display enable sequencing: `DIG*_DIG_FE_CNTL`, `DIG*_DIG_BE_CNTL`, `DIG*_DIG_BE_EN_CNTL`, `DIG*_DIG_LANE_ENABLE`, and `DIG*_FORCE_DIG_DISABLE` expose source routing, encoder start, backend enable, lane clocking, and forced disable.
- DisplayPort stream setup: `DP*_DP_PIXEL_FORMAT`, `DP*_DP_CONFIG`, `DP*_DP_VID_TIMING`, `DP*_DP_VID_M`, `DP*_DP_VID_N`, MSA timing registers, and stream control macros provide the register fields needed before enabling a DP stream.
- Link training and PHY verification: `DP*_DP_LINK_CNTL`, DPHY training, fast training, PRBS, HBR2 pattern, CRC, and MST CRC masks expose training state, test pattern selection, and validation signals.
- Secondary packet delivery: `DP*_DP_SEC_CNTL*`, `DP*_DP_SEC_FRAMING*`, `DP*_DP_SEC_PACKET_CNTL`, `VPG1_*`, `AFMT1_*`, and `DIG1_HDMI_GENERIC_PACKET_CONTROL*` define packet enable, send, pending, active, missed-deadline, line-number, and double-buffer bits for audio/video metadata packets.
- MST/MSO allocation: `DP*_DP_MSE_*`, `DP*_DP_MSO_CNTL*`, and `DP*_DP_MSE_SAT*_STATUS` provide slot allocation, update, timing, and status bitfields.
- Power and low-power flows: `VPG1_VPG_MEM_PWR`, `AFMT1_AFMT_MEM_PWR`, `DME1_DME_MEMORY_CONTROL`, and `DP*_DP_ALPM_CNTL` expose memory power and DP main-link sleep/standby request/status fields.

## State And Persistence

The macros themselves hold no mutable state and introduce no storage. They describe persistent hardware state in memory-mapped display registers. Writes through these fields can affect persistent device state until the register is changed again, the display block is reset, or the GPU resumes/reinitializes.

Several field groups represent latched or handshake state:

- Double-buffer state: `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_LOCK`, `*_DB_DISABLE`, and `*_VUPDATE_DB_*` fields indicate pending/taken updates and require correct clear/lock sequencing.
- Interrupt/status acknowledgement: `DP*_DP_VID_INTERRUPT_CNTL`, `DIG1_HDMI_CONTROL`, `DIG1_HDMI_STATUS`, `DIG1_HDMI_DB_CONTROL`, `AFMT1_AFMT_AUDIO_PACKET_CONTROL`, and DPHY fast-training/CRC status fields include flags and ack bits that must be handled according to write-one-to-clear or hardware-specific semantics in the register spec.
- Packet send state: GSP, HDMI generic, metadata, and secondary packet send/pending/active/deadline-missed fields model hardware packet schedulers and can reflect transient per-frame activity.
- Power state fields: `*_MEM_PWR_STATE`, `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, and ALPM pending bits expose hardware power-management state; stale or incorrect writes can block low-power entry or wake paths.

## Dependencies And Integration Points

This chunk depends on companion generated headers that define register addresses, base indices, and aggregate field lists for DCN 3.0.1. The naming convention matches AMDGPU display code patterns where register access macros combine a register symbol with `__FIELD__SHIFT` and `__FIELD_MASK` constants.

Likely integration points include:

- AMDGPU DC resource, link encoder, stream encoder, HDMI, DP, MST, DSC, audio, metadata, and power-management code that includes DCN ASIC register headers.
- Register helper macros/functions that read-modify-write fields by applying `MASK` and `SHIFT` constants.
- ASIC-version dispatch tables that choose the DCN 3.0.1 register layout for compatible GPUs.
- Diagnostics and self-test paths that use CRC, PRBS, FIFO error, packet status, fast-training status, and HDMI/AFMT overflow/error fields.

Because this is an include header, compile-time consumers are sensitive to exact macro names. Any rename, missing field, or changed mask silently redirects or breaks low-level hardware programming at all call sites that reference it.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong bit mask or shift can corrupt unrelated fields in the same 32-bit register, causing display blanking, audio packet failure, DSC/MST misconfiguration, or power-management regressions.
- Repeated instance blocks (`DP0` vs `DP1`, `DIG0` vs `DIG1`) are mostly parallel but not byte-for-byte identical in this chunk. For example, `DP1_DP_VID_TIMING` in this slice lacks the visible `DP_VID_M_N_GEN_EN` field that appears for `DP0`, and `DP1_DP_ALPM_CNTL` is cut off at the chunk boundary. Merge/review must avoid assuming all instances are identical.
- Fields ending in `_MASK_MASK` are legitimate generated names for fields whose logical name includes `MASK`; tooling that splits on `_MASK` naively can misparse `DP*_DP_VID_INTERRUPT_CNTL__DP_VID_STREAM_DISABLE_MASK_MASK`, `DP*_DP_DPHY_CRC_CNTL__DPHY_CRC_MASK_MASK`, and similar definitions.
- Many packet-control groups use dense repeated fields for generic packet indexes. Off-by-one mistakes in generated constants or table consumers could route metadata/audio packets to the wrong slot or line.
- Status/ack fields and double-buffer clear fields have hardware-specific write semantics not represented in this header. Consumers must not infer safe write values from the masks alone.
- The chunk begins after the start of a `DIG0` register group and ends before the full `DP1_DP_ALPM_CNTL` mask list, so file-level research must include adjacent chunks before drawing whole-file completeness conclusions.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/display regression signals:

- Compile coverage for AMDGPU DCN 3.0.1 paths catches missing or renamed macros used by driver code.
- Generated-header consistency checks can compare each `__SHIFT` field with a matching `_MASK` field, verify masks fit within 32 bits, and verify that repeated instance families retain expected parity where the hardware spec requires it.
- Display bring-up tests should exercise DP0 and DP1 link training, stream enable/disable, mode changes, MST slot allocation, MSO, DSC, HDMI deep-color/scrambling, audio packet output, metadata packets, and ALPM transitions.
- Runtime diagnostics should watch FIFO overflow, steer/TU overflow, HDMI audio/VBI packet errors, AFMT FIFO overflow, DPHY CRC validity, MST CRC phase errors, fast-training completion, GSP deadline-missed flags, and double-buffer pending/taken bits.
- Suspend/resume and power-gating tests should verify `VPG1`, `AFMT1`, `DME1`, and DP ALPM memory/power fields are restored or reprogrammed correctly.

## Open Questions For Merge Lane

- Confirm adjacent chunks include the full opening context for `DIG0_TMDS_DCBALANCER_CONTROL` and the remaining `DP1_DP_ALPM_CNTL` mask definitions.
- Compare the DCN 3.0.1 generated masks with the matching address header and any `*_DEFAULT` or field-list headers to identify whether differences between `DP0` and `DP1` are intentional hardware differences or chunk-boundary artifacts.
- Identify actual consumers of the `DIG1`, `DP0`, `DP1`, `VPG1`, `AFMT1`, and `DME1` macros in the AMDGPU display driver before the final per-file report describes concrete call sites.
