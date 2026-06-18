# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h lines 3030-6042

## Purpose

This chunk is a generated AMD DCE 11.2 register-address map. It contains 3,013 preprocessor `#define` constants that name MMIO register offsets for several display-engine blocks: the tail of UNIPHY reserved macro-control space, DCRX and DPHY macro reserved ranges, six DCP display-pipe register instances, nine DIG/HDMI/AFMT/TMDS encoder instances, DMCU microcontroller registers, and the start of nine DisplayPort link/stream register instances.

The chunk does not implement behavior directly. Its purpose is to give DCE 11.2-specific symbolic names to hardware addresses so AMDGPU, power-management, and display code can issue register reads and writes without hard-coding numeric offsets. The file-level naming pattern is important: unqualified aliases such as `mmGRPH_ENABLE`, `mmDIG_CONTROL`, and `mmDP_LINK_CNTL` point at the first instance, while qualified names such as `mmDCP5_GRPH_ENABLE`, `mmDIG8_DIG_CONTROL`, and `mmDP8_DP_LINK_CNTL` point at explicit hardware instances.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this range. The exported interface is a set of macros consumed by register-access helpers such as `RREG32()` and `WREG32()` in other AMDGPU code.

Major macro groups in this chunk are:

- `mmUNIPHY_MACRO_CNTL_RESERVED157` through `mmUNIPHY_MACRO_CNTL_RESERVED159`, plus `mmDCIO_UNIPHY0_...` through `mmDCIO_UNIPHY7_...` aliases, finishing the UNIPHY reserved macro-control space started before this chunk.
- `mmDCRX_PHY_MACRO_CNTL_RESERVED0` through `mmDCRX_PHY_MACRO_CNTL_RESERVED379`, a contiguous reserved receiver PHY macro range from `0x5a84` through `0x5bff`.
- `mmDPHY_MACRO_CNTL_RESERVED0` through `mmDPHY_MACRO_CNTL_RESERVED63`, a contiguous transmitter/display PHY macro range from `0x5d98` through `0x5dd7`.
- DCP pipe registers for instances 0-5, with default aliases at the DCP0 offsets. These cover graphics enable/control, primary and secondary surface addresses, pitch, surface offsets, flip/update control, DFQ status, interrupts, compression surface metadata, prescale values, input/output CSC matrices, color transform matrices, denorm/round/clamp controls, keyer registers, degamma and gamut-remap registers, DCP debug registers, hardware rotation, XDMA underflow detection, regamma LUT programming, alpha control, and related per-pipe state.
- DIG encoder registers for instances 0-8, including `DIG_*`, `HDMI_*`, `AFMT_*`, and `TMDS_*` register families. These names cover encoder control, HDMI audio/video packet controls, AFMT audio packet/status/generic packet registers, infoframe/checksum registers, TMDS control, and DIG debug access.
- DMCU registers from `mmDMCU_CTRL` through DMCU interrupt/performance/DPRX interrupt controls, plus master/slave communication mailbox registers.
- DP link and secondary-stream registers for instances 0-8, beginning at `mmDP_LINK_CNTL` and continuing through `mmDP3_DP_MSE_SAT0` at the chunk boundary. This includes link control, pixel format, MSA colorimetry/misc/timing overrides, video timing and M/N values, link framing, HBR2 and DPHY training/test/CRC controls, secondary-data packet controls, audio M/N readback, timestamps, and MSE rate-control registers.

The companion `dce_11_2_sh_mask.h` header supplies field masks and shifts for many of these registers. This `_d.h` header supplies only addresses.

## Control Flow

This chunk has no runtime control flow. Its operational flow is compile-time macro expansion:

1. A DCE 11.2 consumer includes `dce/dce_11_2_d.h`, often with `dce/dce_11_2_sh_mask.h`.
2. The consumer selects either a concrete instance macro, such as `mmDP4_DP_SEC_CNTL`, or a base alias plus a runtime offset, such as `mmGRPH_ENABLE + amdgpu_crtc->crtc_offset`.
3. The resulting integer offset is passed to AMDGPU register helpers for MMIO access.
4. Hardware state changes only in the external code that reads or writes the selected register.

The repeated instance layout is the key control convention. DCP instances use offsets `0x1a00`, `0x1c00`, `0x1e00`, `0x4000`, `0x4200`, and `0x4400` for corresponding pipe registers. DIG/DP instances use mostly regular per-link blocks at `0x4a00`, `0x4b00`, `0x4c00`, `0x4d00`, `0x4e00`, `0x4f00`, `0x5400`, `0x5600`, and `0x5700` regions. Code that relies on adding per-instance offsets depends on those generated constants staying aligned with the hardware register map.

## State And Persistence Behavior

The header stores no software state and has no persistence by itself. It is a declarative map from names to numeric hardware offsets.

When external code writes these registers, the affected state lives in the display hardware. Examples include scanout surface address state in DCP registers, color conversion and gamma LUT state in DCP color registers, HDMI/AFMT packet state in DIG registers, DMCU firmware/control/mailbox state, and DisplayPort link-training, stream, audio, CRC, and MST/MSE state in DP registers. That hardware state persists until reprogrammed, reset by the relevant display block, or cleared by GPU reset/suspend/resume paths.

The reserved PHY macro ranges are also stateful if touched by diagnostics or bring-up code, but their semantics are intentionally not represented in this header. They should be treated as ASIC-register database entries rather than self-documenting software contracts.

## Dependencies

This chunk depends on the surrounding generated DCE 11.2 register-header ecosystem:

- The include guard and license/header context from the top of `dce_11_2_d.h`.
- Matching field definitions in `dce_11_2_sh_mask.h`.
- AMDGPU register access helpers and display/power-management code that consume `mm*` offsets.
- ASIC-specific display hardware for DCE 11.2, including DCP, DIG, DMCU, DCIO/UNIPHY, DCRX/DPHY, and DP blocks.

One direct in-tree inclusion is `drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`, which includes both `dce_11_2_d.h` and `dce_11_2_sh_mask.h`. Similar DCE generation patterns are used by display paths such as older `dce_v*_0.c` files, where calls like `WREG32(mmGRPH_ENABLE + amdgpu_crtc->crtc_offset, ...)` and `RREG32(mmDP_SEC_CNTL + dig->afmt->offset)` show the intended base-plus-instance-offset style.

## Integration Points

The DCP section integrates with scanout plane programming, page flips, cursor/display pipe state, color management, and per-pipe debug/status paths. Register families such as `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_UPDATE`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `REGAMMA_*`, and `ALPHA_CONTROL` are the low-level address layer beneath DRM/KMS plane and color-management logic.

The DIG/HDMI/AFMT/TMDS section integrates with digital encoder setup, HDMI packet generation, audio infoframes, generic infoframe packet transmission, and debug access for encoder front ends. Each register has a default alias plus `DIG0` through `DIG8` instance forms, allowing either table-driven instance selection or explicit register use.

The DMCU section integrates with display microcontroller firmware loading/control, DMCU interrupt routing, scratch registers, and host-to-microcontroller mailboxes (`MASTER_COMM_*` and `SLAVE_COMM_*`). Power-management code including the VegaM SMU manager includes this DCE 11.2 map, so address drift can affect display-related power and firmware coordination.

The DP section integrates with DisplayPort link bring-up, main-stream attribute programming, video timing, DPHY training/test controls, CRC diagnostics, secondary-data packet and audio clock programming, and MST/MSE bandwidth allocation. The chunk ends in the middle of the MSE saturation register family at `mmDP3_DP_MSE_SAT0`; the later chunk must be reconciled for the complete per-file DP/MSE view.

## Risks And Edge Cases

- These constants are raw hardware offsets. A wrong address compiles cleanly but can read or write the wrong display register, causing blank displays, bad color, failed link training, audio packet loss, or difficult suspend/resume failures.
- The chunk starts in the middle of the UNIPHY reserved sequence and ends in the middle of the DP MSE saturation sequence. A final per-file report must merge adjacent chunks before drawing conclusions about those register families.
- Default aliases such as `mmGRPH_ENABLE`, `mmDIG_CONTROL`, and `mmDP_SEC_CNTL` map to instance 0. Code using a default alias must add the correct runtime instance offset when targeting other pipes or links.
- The generated instance layout is not perfectly inferred from simple arithmetic. For example, the visible `DP_DPHY_SCRAM_CNTL` instance list has `mmDP8_DP_DPHY_SCRAM_CNTL` at `0x56b6` and no `mmDP7_DP_DPHY_SCRAM_CNTL` line in this chunk, while nearby DP DPHY registers define both DP7 at `0x56xx` and DP8 at `0x57xx`. Consumers should trust the generated header for this ASIC but static validation should flag such irregularities for review against the source register database.
- Reserved DCRX/DPHY/UNIPHY macro-control names provide no bit-level semantics. Hand-written code should avoid programming them unless backed by ASIC documentation or known firmware/display bring-up requirements.
- DCP surface-address and compression-address registers encode memory addresses; programming the wrong pipe or stale address can point scanout at invalid or unintended framebuffer memory.
- DMCU mailbox and firmware-control registers are coordination points between host driver and display microcontroller. Incorrect ordering or offsets in consumer code can deadlock firmware handshakes or misroute interrupts even though this header itself has no ordering rules.
- DP secondary-data and audio M/N registers are timing-sensitive. Using the wrong per-link offset can produce valid MMIO transactions that affect a different active connector.

## Test Signals

Useful validation for this chunk is mostly build-time, static, and hardware-integration oriented:

- Kernel/driver builds that include `dce_11_2_d.h` and `dce_11_2_sh_mask.h` should compile without missing macro or duplicate-definition diagnostics.
- Static checks should compare repeated DCP0-5, DIG0-8, and DP0-8 groups for expected address progression and known exceptions.
- Register-table generation tests should confirm that default aliases map to the intended first instance and that explicit instance macros match the ASIC register database.
- Display smoke tests should exercise plane enable/disable, flips, color-management updates, hardware cursor/alpha paths, and compressed-surface scanout on DCE 11.2 hardware.
- HDMI/DP hotplug and modeset tests should verify encoder setup, infoframe/audio packet programming, DP link training, CRC diagnostic paths, and MST/MSE bandwidth allocation.
- Suspend/resume and GPU reset tests should verify that DCP, DIG, DMCU, and DP state programmed via these offsets is restored to working hardware state.
- Low-level debug reads of representative registers, such as `mmDCP0_GRPH_ENABLE`, `mmDIG0_DIG_CONTROL`, `mmDMCU_STATUS`, and `mmDP0_DP_LINK_CNTL`, should return plausible values on matching DCE 11.2 hardware and should not access unrelated blocks.
