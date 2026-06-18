# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 7887-10409

## Purpose

This chunk is generated AMD DCN 3.5 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets and companion base-index selectors. Consumers combine each `reg...` offset with its matching `reg..._BASE_IDX` to form the absolute register address for DCN 3.5 display hardware.

The requested range is a mid-file slice of `dcn_3_5_0_offset.h`. It starts inside the tail of the `DP_AUX4` AUX block, then covers display I/O stream-output register groups for `DIG0` through `DIG4`, `DP0` through `DP4`, `VPG0` through `VPG4`, `AFMT0` through `AFMT4`, and `DME0` through `DME4`. It then covers common DCIO/DIO, GPIO, AUX/DDC, clock/pad, DCIO chip, and UNIPHY register-offset ranges through `DCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57`.

Although this tree is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The interface is the generated macro namespace:

- `reg<block>_<register>`: a DCN 3.5 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: the base-address segment selector used by helper macros such as `BASE(reg..._BASE_IDX) + reg...`, `SR(...)`, `SRI(...)`, and DMUB register-offset builders.

The chunk contains 2,394 `#define` lines: 1,197 register-offset macros and 1,197 matching `_BASE_IDX` macros. Every `_BASE_IDX` value in this range is `2`, which is part of the address contract with the SOC/DCN base-address tables; the numeric offset alone is not enough to address hardware safely.

Major macro families in this slice:

- `DP_AUX4` tail: AUX software/low-speed status and data, AUX DPHY TX/RX controls and status, GTC sync control/status/error registers, and PHY wake control.
- `VPG0` through `VPG4`: generic packet access/data, generic-stream-packet frame/immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers used for stream secondary-data packet generation.
- `AFMT0` through `AFMT4`: audio/VBI packet control, audio info, IEC 60958 channel-status words, ramp controls, audio CRC, status/interrupt, audio source selection, infoframe control, and AFMT memory power.
- `DME0` through `DME4`: Display Micro Engine control and memory-control offsets.
- `DIG0` through `DIG4`: stream-encoder front-end/back-end enable/clock/control, output CRC, test and clock patterns, FIFO controls, HDMI metadata/audio/ACR/generic-packet/control/status registers, AFMT bridge control, TMDS controls/symbols, lane enable, version, and force-disable registers.
- `DP0` through `DP4`: DisplayPort stream and link controls including MSA colorimetry/timing/VBID fields, video `M/N`, DPHY/link framing, video interrupt control, training and lane status, PHY test/debug controls, secondary-data packet controls, MST and payload allocation, CRC, pixel format, and AUX-less ALPM controls.
- Common DIO/DCIO registers: link controls for links A through E, DIO clock control, DIO memory power control, DCIO debug/mux and test debug registers, clock/pad controls, soft reset, AUX/I2C status, AFE low-power controls, PHY power status, and intercept control.
- GPIO and pad-control registers: DC GPIO masks/data/enables for generic DC GPIO, sync, generation lock, swap lock, DDC, HPD, DP AUX, and related pad-pull/pad-power-good controls.
- UNIPHY families: legacy `UNIPHYA/B/C/D/E` test/debug/data/indirect-access names plus `DCIO_UNIPHY0` through partial `DCIO_UNIPHY4` macro-control reserved offsets. The requested range ends at `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57` and the matching base-index line is outside the chunk.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.5 resource, IRQ, DIO, GPIO, and DMUB code includes `dcn_3_5_0_offset.h` together with the matching shift/mask header.
2. Register-list macros paste instance IDs into names such as `regDIG3_HDMI_CONTROL`, `regDP2_DP_LINK_CNTL`, `regVPG1_VPG_GENERIC_PACKET_DATA`, or `regAFMT4_AFMT_AUDIO_PACKET_CONTROL`.
3. Helper macros add the base segment selected by `*_BASE_IDX` to the offset and store the result in per-block register tables.
4. Driver code later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, wait/poll helpers, or DMUB register structures to program links, packet generators, audio formatting, AUX/DDC, GPIO, panel/link power, and display debug paths.

The macros do not encode ordering requirements. Consumers must still sequence clock enablement, memory/power gating, stream enable/disable, link training, AUX arbitration, hotplug handling, audio packet setup, packet double-buffer updates, interrupt clear/ack behavior, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes MMIO-backed GPU state. The represented hardware state includes:

- AUX channel state for DisplayPort DPCD/EDID transactions, low-speed data movement, DPHY TX/RX status, GTC sync, wake control, and AUX status reporting.
- Stream encoder state for HDMI/TMDS and DP output: front-end/back-end enablement, lane enables, clocking, test patterns, output CRC capture, FIFO state, HDMI metadata and generic packets, audio clock regeneration, TMDS symbols, and force-disable/version registers.
- DP stream/link state for timing, colorimetry, VBID, video `M/N`, framing, link training, lane status, MST payload allocation, secondary-data packets, PHY debug, CRC, and AUX-less ALPM.
- Infoframe/audio packet state in `VPG*` and `AFMT*`, including generic packets, ISRC/MPEG metadata, audio-info fields, channel-status words, CRC/status, and memory-power state.
- DCIO and GPIO state for link routing, DIO clocking, DIO memory power, debug muxes, pad controls, DDC/AUX/HPD GPIO masks/data/enables, pull-up/power-good configuration, and UNIPHY macro-control reserved registers.

Persistence is hardware-defined. Configuration registers usually retain values until modeset, link reconfiguration, display-block power gating, suspend/resume, ASIC reset, or firmware/driver reprogramming. Status, interrupt, debug, counter, clear/ack, wake, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This offset header does not distinguish those behaviors; the companion shift/mask header and consuming driver code provide field-level semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h` for field shifts and masks.
- SOC/DCN base-address definitions consumed by `BASE(reg..._BASE_IDX)`.
- The stream encoder, link encoder, GPIO, IRQ, resource, and DMUB register-list macros that construct typed register tables from these generated names.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`

The primary integration pattern is token-pasting register construction. `dcn35_resource.h` defines register-list macros for `VPG`, `AFMT`, `DIG`, stream encoder, link encoder, DIO, and DC global register blocks; those macros expand through `SR`, `SRI`, `SR_ARR`, and `SRI_ARR` style helpers to pair offsets from this header with masks from the matching `dcn_3_5_0_sh_mask.h`. `dmub_dcn35.c` includes this header and uses `REG_OFFSET_EXP(reg_name)`, `DMUB_SR(reg)`, and related macros to populate DMUB-facing register offsets.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These macros are untyped constants, so a wrong `reg...` value or `_BASE_IDX` can compile cleanly while programming the wrong MMIO register or segment.
- Repeated instance families are copy-sensitive. `DIG0`-`DIG4`, `DP0`-`DP4`, `VPG0`-`VPG4`, `AFMT0`-`AFMT4`, and `DME0`-`DME4` are structurally similar but not interchangeable; an instance-specific typo may only fail on one connector, one pipe, or a multi-display configuration.
- The chunk boundaries are artificial. The first line is only the `regDP_AUX4_AUX_SW_STATUS_BASE_IDX` tail of a block that starts before line 7887. The final line is `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57`; its `_BASE_IDX` pair and the following PWRSEQ block are outside this chunk.
- AUX/DDC, HPD, GPIO, pad, and wake registers are side-effect-sensitive. Incorrect status/interrupt/clear/wake handling can break hotplug, EDID reads, DPCD transactions, panel wake, low-power resume, or pad-power sequencing.
- Link-training and stream-packet registers interact with timing and link state outside this header. Bad DP/TMDS/HDMI/AFMT/VPG offsets can cause blank displays, audio loss, CRC mismatch, infoframe corruption, MST payload errors, or failures limited to specific link rates and lane counts.
- DCIO, DIO memory-power, clock, soft-reset, and UNIPHY macro-control offsets are high risk because writes may be ignored or harmful when the relevant display block is gated, reset, firmware-owned, or clock-disabled.
- Reserved `DCIO_UNIPHY*_*RESERVED*` names provide addresses without semantic field names. They are especially dependent on matching the generated database and companion mask definitions; ad hoc writes are risky unless guided by ASIC documentation or existing driver code.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.5 support enabled; missing or renamed macros should fail in resource, IRQ, DIO, GPIO, stream-encoder, link-encoder, and DMUB register-table construction.
- Mechanically verify that every non-`_BASE_IDX` macro in lines 7887-10409 has exactly one matching `_BASE_IDX` macro and that all base-index values remain `2`. The requested chunk intentionally ends before the `_BASE_IDX` for `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57`, so the full-file or adjacent-chunk reconciliation should validate that pair across the boundary.
- Diff this slice against AMD's authoritative DCN 3.5 register database and nearby generated headers where compatibility is expected.
- Exercise systems with enough active displays to use high-numbered instances: DP/HDMI link training on `DIG`/`DP` instances 0 through 4, hotplug, EDID/DDC, AUX DPCD reads/writes, MST, link-rate/lane-count changes, and suspend/resume.
- Validate stream packets and audio: HDMI and DP audio playback, audio clock regeneration, infoframes, metadata packets, generic packets, ISRC/MPEG metadata, CRC capture, and packet update timing.
- Test GPIO/DCIO paths for DDC/AUX/HPD pad routing, genlock/swaplock pins, pull-up controls, pad power-good reporting, DIO clock/memory-power transitions, and low-power wake.
- Watch kernel logs and display diagnostics for AUX timeouts, hotplug storms, link-training failures, audio dropouts, CRC mismatches, FIFO/underflow issues, MST payload failures, stuck interrupts, and resume failures.

## Cross-Chunk Notes

Previous chunks own the start of `DP_AUX4`, including `AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, and the `regDP_AUX4_AUX_SW_STATUS` offset paired with this chunk's first `_BASE_IDX` line. Later chunks own the `_BASE_IDX` for `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57` and continue into the PWRSEQ register blocks. The final per-file research document should merge adjacent chunks before making complete claims about all AUX channels, all UNIPHY instances, or the complete `dcn_3_5_0_offset.h` hardware map.
