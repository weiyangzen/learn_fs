# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio_regs.h

## Purpose
`intel_audio_regs.h` defines the MMIO addresses and bit fields used by i915 display audio programming across G4X, IBX/CPT/VLV, HSW+, DP 2.0, LPE, CDCLK timestamp, and display audio workaround registers.

## Important APIs, Types, and Functions
The file is macro-only. Important groups include G4X ELD control/data registers; IBX/CPT/VLV per-pipe ELD and audio config registers; `AUD_CONFIG_*` N/CTS and HDMI pixel-clock fields; HSW transcoder audio config and M/CTS registers; `HSW_AUD_PIN_ELD_CP_VLD` output/ELD/CP bits; `AUD_DP_2DOT0_CTRL` SDP split enable; `AUD_FREQ_CNTRL`, `AUD_PIN_BUF_CTL`, `AUD_TS_CDCLK_M/N`; DSC/audio hblank workaround fields in `AUD_CONFIG_BE`; and LPE audio base and VLV mute/debug bits.

## Control Flow
The macros are consumed by `intel_audio.c` in codec enable/disable, ELD readout, HDMI/DP audio config, component power restore, wake override, CDCLK post programming, and DP/DSC workaround paths. They do not execute control flow themselves.

## State and Persistence
They describe hardware state encoded in MMIO registers. Persistent software state is kept elsewhere, but incorrect masks or shifts here directly corrupt register programming.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_MMIO_TRANS`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. It is tightly integrated with i915 display/audio register access helpers and platform register layouts.

## Risks
Register definitions are platform-sensitive. Reusing G4X/PCH/VLV/HSW fields on the wrong generation can touch reserved or unrelated bits. Some macros use non-`REG_*` literal shifts for historical fields, so review must verify signedness and mask width when changing them. HDMI N/CTS fields split upper/lower N values and must remain consistent with hardware documentation.

## Test Signals
Primary signals are successful compile, register read/write traces under KMS debug, HDMI/DP audio functional tests, DP 2.0 SDP split tests, CDCLK transition tests on display version 13+, and workaround-specific validation on DSC/high-resolution modes.
