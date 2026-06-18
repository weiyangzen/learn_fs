# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 221995-222948

## Purpose

This chunk is generated AMD DCN 3.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to access individual fields inside C20 PHY receiver/adaptation and PIPE4 lane message-bus registers. Consumers combine these `__SHIFT` and `_MASK` definitions with the matching register offsets from `dcn_3_2_0_offset.h` and the DC register helper macros to read, write, or update hardware fields safely.

The range begins in the `C20_PHY_CR4_RAWLANEAONX_DIG_RX_*` block, covering RX equalizer/adaptation status, tap-offset validity, CDR detector controls, RX input/output override fields, and signal-detect filtering. It then switches to `addressBlock: c20_phy_lane0_pipe4_rdpcspipemsgbusind`, defining PIPE4 lane0 LPC PHY fields for RX margining, RX/TX control, VDR indirect access, custom DP/FRL/HDMI rate signaling, TX equalization overrides, recalibration, and deskew. The final part repeats the same PIPE4 LPC PHY field layout for lane1 and ends at the file footer.

Although this repository path is under a Ceph client mirror, the source is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, memory allocations, or locks in this slice. The API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit position of a field within the register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field after shifting into register position.

Major macro groups in this chunk:

- `C20_PHY_CR4_RAWLANEAONX_DIG_RX_DFE_*_TAP1_OFST_BANK_0/1`: six-bit DFE tap1 offset fields for DEH/DEL/DOH/DOL/EEH/EEL/EOH/EOL phases, plus one-bit `DFE_TAP1_OFST_VLD` validity flags. The requested range starts at the tail of bank0 EOH and then includes EOL bank0 and a full bank1 set.
- `C20_PHY_CR4_RAWLANEAONX_DIG_RX_ADPT_*_BANK_0/1`: RX adaptation outputs for attenuator, VGA, CTLE boost/pole, DFE taps 1 through 5, IQ value/valid, reference error even/odd bytes, and `RX_ADAPT_DONE`.
- `C20_PHY_CR4_RAWLANEAONX_DIG_RX_TX_*`: control fields used by RX-side adaptation logic to derive or invert TX equalization direction and compare adapted ATT/VGA/post-boost/post-tap values against thresholds.
- `C20_PHY_CR4_RAWLANEAONX_DIG_RX_ADPT_CTL_0` through `_28`: twenty-nine full-width 16-bit adaptation control registers exposed as generic `VAL` fields.
- `C20_PHY_CR4_RAWLANEAONX_DIG_RX_CDR_*`: CDR detector enable, PPM monitor mode, disable-during-adaptation bit, and a 12-bit recovery-time value.
- `C20_PHY_CR4_RAWLANEAONX_DIG_RX_OVRD_IN_0`, `RX_IN_0`, `RX_OVRD_OUT_0`, `RX_OUT_0`, and `RX_PMA_OVRD_OUT_0`: override-enable/value pairs and current input/output status for RX disable, termination, AC/DC termination, LF/HF signal detect, HF filter disable, VREF generator control, and PMA termination/VREF outputs.
- `C20_PHY_LANE0_PIPE4_UPCSLANE_PIPE_LPC_PHY_*` and `C20_PHY_LANE1_PIPE4_UPCSLANE_PIPE_LPC_PHY_*`: 8-bit PIPE4 message-bus register fields for RX margining, elastic buffer control, RX equalization/recalibration, RX status, TX deemphasis, FS/LF, local preset coefficient request, TX margin/swing, encode/decode bypass, VDR indirect read/write address/data windows, custom SERDES/HDMI/width/LFPS controls, TX EQ overrides for G1/G2/HDP paths, recalibration bank selection, force/skip enables, deskew enables, and global recal/deskew override enables.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes `dcn_3_2_0_sh_mask.h` together with `dcn_3_2_0_offset.h`.

The usual flow is:

1. DCN 3.2 resource, IRQ, GPIO, clock, GMC, and DMUB code include the generated offset and shift/mask headers.
2. Register helper macros build symbolic register descriptors from the matching `mm...` offset and `...__FIELD_MASK` / `...__FIELD__SHIFT` constants.
3. Driver code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, polling helpers, or DMUB register access wrappers to program the C20 PHY lane registers.
4. Hardware performs RX adaptation, margining, EQ training, signal detection, VDR indirect accesses, recalibration, and deskew according to the programmed fields.

The macros do not encode ordering. Consumers must still sequence link power, lane enablement, PHY reset/recalibration, adaptation-control writes, status polling, VDR address/data transactions, and interrupt/status clearing according to the PHY specification.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state.

The represented state includes:

- RX adaptation results and status: ATT, VGA, CTLE, DFE taps, IQ, reference error, and adaptation-done bits for two calibration banks.
- RX control and observability: CDR detector configuration, recovery timing, margin range, RX disable/termination/VREF/signal-detect input controls, output status, and PMA override values.
- PIPE4 per-lane state: destructive margining start/reset/mode/direction/offset, elastic-buffer depth and reset controls, RX polarity and equalization training, invalid-request status, TX deemphasis and preset coefficient data, FS/LF values, TX margin and swing, and encode/decode bypass.
- VDR and calibration state: indirect VDR read/write address/data bytes, DP custom SERDES rate, HDMI rate, custom width, LFPS electrical-idle timer, TX EQ override enables and G1/G2/HDP override coefficients, MPLL/RX calibration bank overrides, recal force/skip controls, TX/RX deskew enables, and top-level recal/deskew override enables.

Persistence is hardware-defined. Some fields are configuration bits that may remain until reset, link reconfiguration, power gating, suspend/resume, or modeset. Others are status, latch, request, reset, self-clearing, or read-only fields. This generated mask header does not distinguish those behaviors; the consuming code and hardware documentation must apply the correct access pattern.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2 register database and must match the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`

Direct include sites for this mask header in the local tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`

Within this chunk, several macro names only appear in this generated header in the local tree. That is expected for low-level register databases: higher-level code often reaches them through token-pasting register lists, generated tables, firmware interfaces, or shared helper macros instead of spelling every final macro name directly.

## Risks And Edge Cases

- Mask/shift drift is the primary risk. These are untyped constants, so an incorrect bit position or mask can compile cleanly while corrupting adjacent hardware fields.
- Reserved masks are documented but not enforced. Writes must preserve reserved bits where required; clobbering them can trigger undefined PHY behavior.
- The chunk starts mid-register-family. The first two lines are the mask tail for `C20_PHY_CR4_RAWLANEAONX_DIG_RX_DFE_EOH_TAP1_OFST_BANK_0`; adjacent chunk context is needed for that register's shifts and complete bank0 coverage.
- Banked adaptation fields are easy to mix up. Bank0 and bank1 have matching layouts but may represent different calibration contexts; using the wrong bank can create link-training or resume-only failures.
- Override-enable/value pairs must be programmed coherently. Setting an override value without its enable bit, or leaving an override enabled after test/debug paths, can force RX termination, VREF, signal detect, PMA output, TX EQ, recalibration, or deskew behavior unexpectedly.
- VDR indirect accesses are sequencing-sensitive. Address high/low and data high/low fields must be written/read in the correct order; this header only provides field geometry.
- Lane0 and lane1 PIPE4 blocks are duplicated. Copy/paste or token-paste mistakes can silently program the wrong lane, causing failures that appear only with multi-lane links, particular lane mappings, FRL, or DisplayPort rates.
- Several fields control destructive margining, recalibration, and deskew. Misprogramming them can disturb active links, produce transient display blanking, or cause hard-to-reproduce signal integrity failures.

## Test Signals

Useful validation signals for changes affecting this area include:

- Build coverage for DCN 3.2 AMDGPU display code, especially files that include `dcn_3_2_0_sh_mask.h`, to catch renamed or malformed macros.
- Static consistency checks that each register field has the expected `__SHIFT` and `_MASK` pair and that reserved fields do not overlap named fields.
- Display bring-up on DCN 3.2 hardware across DisplayPort, HDMI, and FRL modes, with multi-lane configurations exercising both lane0 and lane1 PIPE4 blocks.
- Link-training and equalization logs showing RX adaptation completion, stable CDR behavior, valid DFE/IQ data, and no unexpected invalid-request status.
- Margining or PHY diagnostic tests that exercise `RX_MARGIN_CONTROL*`, error/sample resets, margin offset/direction, and destructive margining enablement.
- Suspend/resume, hotplug, modeset, and link-rate-switch testing to detect stale overrides, failed recalibration, deskew issues, or lost PHY state.
- Register readback tests around override and VDR paths to verify value/enabled pairs, address/data ordering, and preservation of reserved bits.
