# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 10216-12711

## Purpose

This chunk is generated AMDGPU DCE 12.0 display-controller register metadata. It contains no executable C code; it publishes preprocessor constants that name memory-mapped display registers and their SOC15 base-index segment. Driver code combines each `mm...` offset with `DCE_BASE__INST0_SEG...` to form the final MMIO address for Vega/DCE120 display hardware.

The selected range covers the digital-output and PHY-facing part of the DCE register map. It starts inside the `DP0` register block, then defines complete repeated `DIG1` through `DIG6` and `DP1` through `DP6` blocks, then continues into `DCIO_UNIPHY0`, combo-PHY common/TX/PLL registers, and the beginning of `DCIO_UNIPHY1`. The file path lives under a local `ceph-client` source mirror, but this header is AMDGPU display hardware metadata; it has no Ceph filesystem semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or storage objects in this chunk. The macro namespace is the API surface.

Each hardware register is represented by paired macros:

- `mm<register>`: register offset within a generated DCE address space.
- `mm<register>_BASE_IDX`: SOC15 base segment selector, usually `2` in this chunk.

Important register families in this line range are:

- `mmDP0_*`: the tail of the DisplayPort 0 block, beginning at `DP_LINK_FRAMING_CNTL` and covering HBR2 eye pattern controls, VBID/video interrupts, DPHY training/scrambling/CRC, DisplayPort secondary-data packets, audio `M`/`N` values, MST/MSE slot allocation timing/status registers, and DPHY byte/symbol swap or HBR2 pattern controls.
- `mmDIG1_*` through `mmDIG6_*`: repeated digital front-end and HDMI/AFMT register groups. Each instance defines DIG control/status/test/CRC/FIFO registers, HDMI control/status/audio/ACR/infoframe/generic-packet registers, AFMT interrupt/audio/ISRC/AVI/MPEG/generic/60958/audio-source registers, TMDS control/debug/sync/balancer registers, `DIG_VERSION`, `DIG_LANE_ENABLE`, and `AFMT_CNTL`.
- `mmDP1_*` through `mmDP6_*`: repeated DisplayPort link/stream register groups matching the DP0 tail plus the full block start. They include link control, pixel format, MSA colorimetry/config/misc/timing, video stream timing and `M`/`N`, DPHY training and diagnostic controls, secondary-data/audio packet controls, MST/MSE rate and slot-allocation controls, and SAT status registers.
- `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159`: reserved or macro-control aperture entries for UNIPHY0. The names do not expose field intent, but they preserve the generated hardware address layout.
- `mmDC_COMBOPHYCMREGS0_*`: combo-PHY common registers for fuse values, bias/impedance, test muxes, spare control, AFE common control, PDDQ, OPM control, mailbox, and display reserved-for-future-use registers.
- `mmDC_COMBOPHYTXREGS0_*`: combo-PHY transmitter lane registers for lanes 0-3, including command-bus TX control, DFX observation, transmitter control, coefficient/current/slew-rate control, BIST control/status, and lane-specific RFU registers.
- `mmDC_COMBOPHYPLLREGS0_*`: combo-PHY PLL registers for frequency control, spread-spectrum fractional values, debug bus control, clock/control/test, calibration controls, loop and regulator configuration, observation, and DFT output.
- `mmDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED87`: the beginning of the UNIPHY1 reserved macro-control aperture. Later lines continue this block.

The chunk is heavily repetitive by design. Counts from the requested range show 164 `#define` entries per `DIG1`-`DIG6` family, 112 per `DP1`-`DP6` family, 320 for `DCIO_UNIPHY0`, 32 for combo-PHY common, 128 for combo-PHY TX, 24 for combo-PHY PLL, and 176 for the partial `DCIO_UNIPHY1` slice. Counts include both offset and `_BASE_IDX` macros.

## Control Flow

This header has no runtime control flow. Runtime behavior appears in consumers that expand register-list macros into static register-address tables and then pass those addresses to SOC15 register helpers.

The typical DCE120 flow is:

1. A display module includes `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`.
2. Resource setup macros such as `SR(reg_name)` and `SRI(reg_name, block, id)` concatenate tokens like `mmDIG1_AFMT_AVI_INFO0` or `mmDP2_DP_SEC_CNTL`, add `DCE_BASE__INST0_SEG<BASE_IDX>`, and store the resulting address in a hardware object register table.
3. Higher-level stream encoder, link encoder, IRQ, timing-generator, or memory-controller code reads or writes those addresses through `dm_read_reg_soc15()`, `generic_reg_set_soc15()`, `generic_reg_update_soc15()`, or related register-helper paths.
4. Field-level packing/unpacking uses the companion `dce_12_0_sh_mask.h` masks and shifts, not this offset header.

For this specific chunk, `dce120_resource.c` maps `DIG` and `DP` instance offsets into `stream_enc_regs[]` and `link_enc_regs[]`. `dce_stream_encoder.h` consumes many of the `DIG` AFMT/HDMI and `DP` video/audio/MSE registers to program HDMI/DP packet generation, audio metadata, DisplayPort stream timing, and MST-related state.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes stateful hardware registers in the DCE display block.

The hardware state represented here includes digital front-end enable/status, output CRC/test-pattern state, HDMI packet and audio clock-recovery programming, AFMT infoframe and audio-channel metadata, TMDS encoding/control state, DisplayPort link and stream format, MSA timing/colorimetry/VBID, DPHY training/scrambling/CRC diagnostics, secondary-data packet scheduling, DisplayPort audio `M`/`N` values, MST/MSE slot-allocation tables/status, UNIPHY macro-control space, and combo-PHY common/TX/PLL controls.

Persistence depends on the underlying register. Some registers are read-only status snapshots, some are sticky interrupt/status bits or diagnostic counters, and many are control registers that remain programmed until the display driver, firmware/BIOS, hotplug handling, link retraining, stream disable, suspend/resume, power-gating, GPU reset, or full system reset changes them. The offset header does not encode access permissions, reset values, write-one-to-clear behavior, polling requirements, or ordering constraints.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h`, which supplies field masks and shifts for the register addresses defined here. SOC15 base constants are supplied by `soc15_hw_ip.h` and ASIC offset headers such as `vega10_ip_offset.h`.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The most relevant consumers for this chunk are display resource and encoder construction. `dce120_resource.c` uses `SRI()` to build per-instance stream encoder and link encoder register tables. `dce_stream_encoder.h` lists `DIG` AFMT/HDMI and `DP` registers that map directly to this chunk, including AVI/generic/audio infoframes, HDMI ACR controls, DP pixel format, DP video timing, DP secondary/audio packet controls, and DP MSE controls. Link encoder setup also depends on DP DPHY-related addresses, including a local fallback for `DP_DPHY_INTERNAL_CTRL` when the generated header does not define it.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. A wrong offset or `_BASE_IDX` can compile successfully while making the display stack program the wrong register, the wrong instance, or the wrong SOC15 segment.

High-risk areas include repeated instance blocks. `DIG1`-`DIG6` and `DP1`-`DP6` are structurally similar, so generation or copy errors can swap an engine instance while preserving plausible names and values. Such errors may only show when a specific display pipe, connector, or MST topology uses the affected instance.

The line boundaries are not semantic boundaries. The chunk begins after the start of `DP0`; earlier lines define the first DP0 offsets. The chunk ends in the middle of `DCIO_UNIPHY1`; later lines continue `RESERVED88` onward. The final per-file merge should treat these as chunking artifacts, not missing hardware support.

PHY and DPHY registers are especially sensitive. Incorrect DP training, scrambling, CRC, HBR2 pattern, UNIPHY macro-control, combo-PHY TX, or combo-PHY PLL addresses can break link bring-up, cause unstable high-rate DisplayPort links, corrupt lane mapping, or make diagnostic/test controls touch unintended lanes. Reserved UNIPHY macro-control names also carry risk because the generated names do not document semantics; consumers must rely on AMD hardware documentation and established driver sequences.

Packet-generation registers can create user-visible failures even when the display link stays lit. Bad HDMI/AFMT/DP secondary-packet offsets may break audio, AVI infoframes, colorimetry metadata, HDR/vendor packets carried through generic-packet paths, or MST stream allocation.

## Test Signals

Useful validation signals include:

- Kernel build coverage for DCE120/Vega display code that includes `dce_12_0_offset.h`; malformed or missing macros should fail compile-time token expansion in `SR()`/`SRI()` register tables.
- Static register-map comparison against AMD's generated DCE 12.0 source database, especially for the repeated `DIG`/`DP` instance deltas and the partial chunk boundaries.
- Display bring-up tests across all available encoders/connectors, including HDMI and DisplayPort outputs mapped to different DIG/DP instances.
- HDMI audio and infoframe validation, including ACR `N`/`CTS` behavior, channel status, AVI/MPEG/generic packets, and AFMT update/conflict status.
- DisplayPort link-training and high-bit-rate tests that inspect negotiated lane count/rate, DPHY training status, scrambling/CRC diagnostics, HBR2 patterns, and recovery after hotplug.
- MST tests that validate MSE rate, SAT programming/update/status, link timing, and multiple stream allocation.
- Suspend/resume, runtime power-management, and GPU reset tests that confirm DCE register tables still address the intended hardware after power transitions.
- Hardware debug or register-dump checks that read selected `DIGn`, `DPn`, UNIPHY, combo-PHY TX, and PLL addresses and confirm expected per-instance spacing.

Regression symptoms from bad constants include blank displays on only one connector, audio loss while video remains active, wrong colorimetry/infoframe metadata, MST stream allocation failures, DP links stuck at lower rates, repeated retraining, hotplug IRQ side effects from misaddressed display blocks, or PHY diagnostics showing activity on the wrong lane or encoder.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_offset.h` define the file guard, copyright, display performance, CRTC, HPD, DCP, AUX/I2C, DIG0, and the beginning of DP0. Later chunks continue `DCIO_UNIPHY1` and the rest of the DCE 12.0 offset namespace. The final per-file research document should describe the full header as one generated DCE register-address contract paired with `dce_12_0_sh_mask.h`.
