# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_regs.h

## Purpose
Defines i915 MMIO register addresses and bit fields for DisplayPort AUX channel control and data registers across legacy ports, PCH AUX, VLV, Xe_LPD/Xe2_LPD USB-C AUX channels, and PICA power-well control.

## Important APIs, types, and functions
- Register address macros include `DP_AUX_CH_CTL()`, `VLV_DP_AUX_CH_CTL()`, `PCH_DP_AUX_CH_CTL()`, `XELPDP_DP_AUX_CH_CTL()`, and corresponding `*_DATA()` macros.
- Bit definitions cover AUX send/done/interrupt/error state, timeout selection, message size, precharge/sync fields, hardware test bits, AKSV select, and Xe_LPD AUX power request/status.
- `__xe2lpd_aux_ch_idx()` remaps non-USB-C AUX channels into the display version 20 register layout.
- `XE2LPD_PICA_PW_CTL` and its request/status bits describe PICA power-well control.

## Control flow
The file is declarative. Macro expansion selects the right MMIO address family based on AUX channel and, for Xe_LPD, display version. Callers use the generated register offsets in AUX transaction code and power management paths.

## State and persistence
No C state is stored. The macros address hardware registers whose contents are controlled by AUX transaction programming and power-well management elsewhere.

## Dependencies and integration points
Depends on `intel_display_reg_defs.h` for `_MMIO`, `_PORT`, `_PICK_EVEN_2RANGES`, `REG_BIT`, `REG_GENMASK`, and field helpers. It is an integration point for low-level AUX transfer code, HDCP AKSV AUX transactions, PSR/FEC/GTC AUX-related bits, and platform-specific power sequencing.

## Risks
Register selection is platform-sensitive. The Xe2 remapping helper can silently route to the wrong register if an invalid `aux_ch` is passed. Several bits have different meanings before and after Skylake or Icelake, so callers must only set fields valid for the target platform. Message size and timeout fields are critical for AUX transaction reliability.

## Test signals
Compile-time macro use catches syntax errors only. Runtime signals are AUX transfer success, timeout/error bits in `DP_AUX_CH_CTL`, platform bring-up logs, HDCP AUX behavior, eDP panel probing, and Type-C/USB-C AUX operation on display version 20 and newer hardware.
