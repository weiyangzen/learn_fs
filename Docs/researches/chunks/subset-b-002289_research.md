# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 2384-4766

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display controller, DisplayPort/HDMI PHY, GPIO, AUX/DDC, hotplug, and UNIPHY register fields. It contains no executable C logic; its public surface is a large set of preprocessor constants that encode field bit positions (`__SHIFT`) and field masks (`_MASK`) for hardware MMIO register programming.

The requested range contains 2,161 `#define` entries over 2,383 source lines and 207 register comment markers. It starts at the tail of the `RDPCSTX3` block with the `RDPCSTX_SPARE` mask whose shift is in the previous chunk, covers the remaining `RDPCSTX3` PHY/DPALT field definitions, covers a full `addressBlock: dpcssys_dpcs0_rdpcstx4_dispdec` transmitter/PHY lane group, then crosses into shared DCIO, GPIO/AUX pad, and UNIPHY reserved-control blocks. It ends after `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED5`, so the rest of the UNIPHY2 reserved sequence is left to the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct register accesses in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used by AMD register helpers to isolate or update that field.

The major register-field families in this chunk are:

- `RDPCSTX3` tail fields: `RDPCSTX_CNTL2`, DMCU DPALT block/clock disable controls, `PHY_CNTL0` through `PHY_CNTL17`, PHY fuse/readback fields, DPALT reserved mirror fields, driver-access blocking controls, byte-order controls, and PLL update override fields.
- `RDPCSTX4` full transmitter/PHY block: soft resets, SRAM reset, lane bit/byte order, interrupt mask and status bits, TX FIFO enables/start delay/start, CR/non-DPALT register block enables, DPALT block status, clock gates/enables/readbacks for TX/SRAM/OCLA clocks, interrupt status/clear/mask fields, TX PLL update data and CR address/data windows, TX SRAM power fields, scratch/spare fields, PHY resets, PHY power gating, lane loopback, per-lane TX reset/disable/clock-ready/data-enable/request/ack handshakes, per-lane termination/invert/equalization-bypass/high-protection bits, lane rate/width/receive-detect fields, pstate/MPLL/ref-clock/DPALT controls, MPLLB fractional-N/SSC/divider/multiplier controls, fuse-derived equalization and analog trim fields, generic in/out buses, and lane byte-order controls.
- Shared DCIO block fields: generic A/B clock selection and enable, test/reference clock selectors, UNIPHY A-E link inversion and power-sequencer selection, UNIPHY A-E channel crossbar source selection, write-command delay, pinstrap status, intercept-state status for power sequencers and RDPCS transmitters, backlight PWM frame-start display selection, genlock/swaplock pad routing masks, and soft-reset controls for UNIPHY A-G, DSYNC A-G, and power sequencers.
- DCIO GPIO/AUX pad block fields: generic GPIO masks/output/input-enable/readback fields, DDC1-DDC5 and DDCVGA clock/data masks, pull-down/pad mode/polarity/hardware pull-down/drive strength fields, genlock/swaplock pad masks and readbacks, HPD1-HPD6 mask/readback/input-enable/schmitt/slew/spare/select fields, power-sequencer GPIO routing, pad strength controls, AUX wake and receiver select fields, generic TX12 enables, AUX/DDC/HPD slew/spike/current/resistor/bias/compensation controls, GPIO receiver and pullup enables, AUX termination/swap/hysteresis controls, AUX voltage/output-drive tuning, DDC I2C mode and 1.2V pad controls, and `AUXI2C_PAD_ALL_PWR_OK` status bits.
- UNIPHY reserved blocks: `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` and the first six `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` registers, each exposing a full-width `UNIPHY_MACRO_CNTL_RESERVED` field.

The `RDPCSTX3` and `RDPCSTX4` layouts are intentionally repetitive. The fields name parallel DisplayPort transmitter instances, so nearby definitions should usually be identical except for the `RDPCSTX3`/`RDPCSTX4` prefix and address-block placement.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register, shift, and mask tables:

1. `dcn31_resource.c` includes `dpcs_4_2_0_offset.h` and this matching `dpcs_4_2_0_sh_mask.h`.
2. DCN 3.1 display-resource macros such as `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)` token-paste register and field names into resource tables.
3. Runtime AMD display code uses those tables through register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. Actual sequencing for PHY reset, power gating, clock gating, PLL programming, lane enablement, DisplayPort alternate-mode access arbitration, AUX/DDC pad setup, HPD sensing, and UNIPHY reset is implemented in DC/link/PHY/resource code and hardware state machines outside this generated header.

The macros only describe where bits live. They do not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, latched, reserved, or sequencing-sensitive.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in DPCS and DCIO registers:

- Transmitter and PHY control state: soft reset, SRAM reset, lane FIFO enable/start, TX FIFO errors, lane byte and bit order, CR register access, non-DPALT register block access, DPALT disable/status handshakes, and scratch/spare values.
- Clock and power state: TX/SRAM/OCLA gate disables/enables/status, external/alternate PHY reference clocks, PHY reset/test-powerdown, PHY power-gating mode, PCS/PMA/analog power enables and stable readbacks, SRAM initialization/load/bypass status, lane pstate, lane MPLL enable, DPALT four-lane and disable state, reference-clock request/enable, and memory power-state controls.
- Lane training and signal state: lane reset/disable/clock-ready/data-enable/request/ack, termination control, lane inversion, EQ bypass, high-protection enable, lane low-power/rate/width, receive-detect request/result, loopback enables, MPLLB fractional-N/SSC/divider/multiplier state, fuse-derived TX equalization and analog trim fields, voltage regulator bypass bits, and generic PHY in/out buses.
- Shared DCIO routing state: UNIPHY link inversion, channel crossbar sources, power-sequencer selection, test/reference clock output selection, genlock/swaplock routing and masking, PWM frame-start selection, pinstrap status, intercept-state status, and broad UNIPHY/DSYNC/PWRSEQ soft resets.
- Pad and sideband I/O state: generic GPIO, DDC, DDCVGA, genlock, swaplock, HPD, backlight, AUX, I2C, receiver, pullup, pull-down, drive-strength, slew, spike-filter, termination, polarity, voltage tuning, and pad-power-good fields.
- Reserved UNIPHY macro-control state: full-width reserved fields for UNIPHY1 and the start of UNIPHY2, whose hardware meaning is intentionally not described by the generated names.

Persistence is hardware-defined. Configuration fields generally remain until display link reprogramming, modeset, hotplug handling, suspend/resume, power gating, GPU reset, or ASIC reset rewrites them. Status and handshake bits may be sampled, latched, self-clearing, clear-on-write, or valid only while the relevant PHY, clock, pad, or power domain is active. This header does not record those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching register addresses for the fields described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` directly includes both DPCS 4.2.0 generated headers and initializes DCN 3.1 resource tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the `DPCS_DCN31_*` register and mask/shift list macros consumed by the resource initialization.
- Display link encoder, PHY, AUX/DDC, hotplug, panel power, clock, and hardware-sequencing code consume the initialized tables indirectly when bringing up links, programming lane and PLL state, servicing hotplug/AUX/DDC paths, and controlling display-side pads.

Behaviorally, this chunk sits below higher-level display paths. It provides field locations for low-level operations such as enabling a transmitter lane, requesting PHY clock/power state changes, observing ACK/status bits, programming DP/HDMI clocking, configuring AUX/DDC/HPD electrical pads, resetting UNIPHY/DSYNC blocks, and decoding DCIO status.

## Risks And Edge Cases

- These constants are untyped preprocessor values. An incorrect shift or mask can compile cleanly while causing the driver to update the wrong field or corrupt adjacent reserved bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register source, the companion offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. Line 2384 contains only the `RDPCSTX3_RDPCSTX_SPARE` mask; its shift is in the previous chunk. Line 4766 stops inside the `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` sequence; the remaining UNIPHY2 reserved registers are in the next chunk.
- `RDPCSTX3` and `RDPCSTX4` are copy-sensitive replicated transmitter blocks. A generator error in only one instance can break one physical link while other links appear healthy.
- PHY reset, lane request/ack, pstate/MPLL, clock gate, power gate, SRAM, receive-detect, and DPALT access-block fields are sequencing-sensitive. Bad masks can cause blank displays, failed link training, unstable clocks, missed ACKs, stuck DPALT access, high bit errors, or resume-only failures.
- Interrupt and clear fields in `RDPCSTX4_RDPCSTX_INTERRUPT_CONTROL` are side-effect-sensitive. Confusing status, clear, and mask bits can cause missed FIFO/DPALT events, repeated interrupts, or latent error status.
- GPIO/AUX/DDC/HPD pad fields affect physical sideband signaling. Incorrect masks can break hotplug detection, EDID/AUX transactions, DDC pullups, pad power validation, or board-specific polarity and drive-strength tuning.
- UNIPHY/DSYNC/PWRSEQ soft reset fields have broad blast radius. A bad field definition can reset or fail to reset a whole display PHY/sync/panel-power path.
- Reserved UNIPHY fields are full-width and poorly self-describing. Driver code should avoid depending on reserved semantics unless a platform-specific hardware sequence explicitly requires it.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support with DCN 3.1 enabled. Missing or renamed DPCS 4.2.0 macros should fail where `dcn31_resource.c` initializes register, shift, and mask tables.
- Mechanically verify that complete fields in this range have matching `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions at the starting `RDPCSTX3_RDPCSTX_SPARE` mask and ending UNIPHY2 reserved sequence.
- Cross-check every complete register group in this chunk against `dpcs_4_2_0_offset.h` and AMD's source register database.
- Diff the replicated `RDPCSTX3` and `RDPCSTX4` field layouts where hardware expects the transmitter instances to match.
- Exercise DisplayPort and HDMI link bring-up on ports mapped to the affected RDPCS/UNIPHY instances. Watch for stable link training, correct lane request/ack transitions, no stuck FIFO or DPALT events, and expected clock/power status.
- Run hotplug, EDID/DDC, DisplayPort AUX, suspend/resume, modeset, stream disable/enable, and GPU reset tests to catch pad, HPD, pstate, clock, and reset persistence mistakes.
- Validate panel/backlight and genlock/swaplock paths on systems that expose those pads, especially frame-start selection, power-sequencer GPIO routing, and GSL pad masks.
- Use register dumps during failing links to confirm that PHY power, MPLL, lane status, interrupt, GPIO, AUX/DDC, HPD, and pad-power-good fields decode correctly.

## Cross-Chunk Notes

The previous chunk owns the start of the `RDPCSTX3` register group and the shift for `RDPCSTX3_RDPCSTX_SPARE`. This chunk owns the rest of `RDPCSTX3`, all visible `RDPCSTX4`, the shared DCIO/GPIO/AUX pad section, and the start of UNIPHY reserved fields. The next chunk should continue the `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` sequence and should be reconciled before producing whole-file claims about all DPCS 4.2.0 UNIPHY reserved coverage.
