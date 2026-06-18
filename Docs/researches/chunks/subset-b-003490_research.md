# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h lines 1-8445

## Scope And Purpose

This chunk is the first 8,445 lines of AMD's generated Navi10 hardware enum header. It defines compile-time `typedef enum` constants that encode numeric values for GPU, display, memory-surface, timing-generator, link-encoder, AUX, I2C/DDC, and DCIO register fields. It does not define functions, structs with storage, variables, locks, allocations, sysfs/debugfs surfaces, or direct MMIO access.

The path is under a `ceph-client` source mirror, but the file is AMDGPU register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU display, memory-controller, hub, and graphics code that includes this header and writes these enum values through generated register accessor macros and ASIC-specific register-offset/mask headers.

This chunk contains 779 complete enum definitions. It also includes the file license, include guard, and a non-driver-build compatibility block that maps OpenGL-style blend names such as `GL__ZERO` to generated `BLEND_*` values. The chunk ends at the comment for `DCIO_DIO_OTG_EXT_VSYNC_MUX`; the actual `typedef enum DCIO_DIO_OTG_EXT_VSYNC_MUX` begins on line 8,446 and is outside this chunk.

## Important APIs, Types, And Constants

The exported API is the enum namespace itself. Consumers use these names as raw field values when packing hardware register fields with macros such as `REG_SET_FIELD`, `REG_UPDATE`, `REG_SET`, and generated DC register tables. Important families in this chunk include:

- GDS and general chip enums: `GDS_PERFCOUNT_SELECT` selects global data share performance events across shader engines/shader arrays plus GWS events. `GATCL1RequestType`, `UTCL1RequestType`, `UTCL1FaultType`, `UTCL0RequestType`, `UTCL0FaultType`, `VMEMCMD_RETURN_ORDER`, GL/TCC/GL2 cache policies, memory types, RMI client IDs, read/write cache policies, generic perfmon modes, surface array/tiling forms, DSM error-injection choices, and HDP endian modes define non-display hardware field values.
- Converter and cursor front-end enums: `CNVC_ENABLE`, `CNVC_BYPASS`, `DENORM_TRUNCATE`, `PIX_EXPAND_MODE`, `SURFACE_PIXEL_FORMAT`, `XNORM`, `COLOR_KEYER_MODE`, `CUR_ENABLE`, `CUR_MODE`, and related cursor ROM/expansion/pending enums describe pixel expansion, color keying, cursor formats, and conversion state.
- Display scaler and color management enums: DSCL entries such as `SCL_COEF_FILTER_TYPE_SEL`, `DSCL_MODE_SEL`, `SCL_AUTOCAL_MODE`, coefficient RAM selectors, boundary modes, line-buffer/OBUF controls, plus CM/CMC entries for bypass/enables, LUT config/mode/RAM selection, number of segments, internal CSC, gamut remap, coefficient format, and 3D LUT size/bit-depth.
- DPP and DC perfmon enums: DPP test-clock and CRC source/input selectors are followed by `PERFCOUNTER_*` and `PERFMON_*` values for counter value slice selection, increment mode, run/count-off controls, interrupt enable/type, counted value type, hardware stop selectors, counter state machines 0-7, and global/local state selection.
- HUBP/HUBPREQ/HUBPRET memory-display enums: rotation/mirror, pipe/bank/shader-engine geometry, swizzle modes, pipe interleave, render-backend counts, dimension type, metadata linear/alignment, array/tile/pipe config, micro-tile mode, tile split, bank width/height, macro tile aspect, swath height, PTE/DPTE/MPTE group sizes, blank/disable/no-outstanding status, VTG selection, TMZ/DCC flags, flip modes, surface update locks, interrupt controls, detile crossbar routing, DET/PIXCDC memory sleep, cursor memory/address modes, dynamic metadata status, and XFC pixel/frame/chunk choices.
- Composition, output, and pattern-generator enums: MPC config and OCSC enums cover CRC modes, vupdate lock bits, rate-control disable, denorm modes, output CSC coefficient formats, and CSC modes. MPCC enums cover blend/pass-through modes, per-pixel/global alpha modes, premultiplied-alpha flags, stereo/subsampling modes, stall interrupt ack/mask, background color bit depth, OGAM LUT RAM selection, and OGAM mode. DPG and FMT enums cover display pattern generation, dynamic range, bit depth, field polarity, pixel encoding/subsampling, bit reduction, truncation, spatial/temporal dithering/FRC, clamp formats, memory power, frame/random control, and PTI polarity.
- OPP and OTG timing enums: OPP pipe clock/bypass and CRC controls are followed by a large OTG block for start/disable points, field-number polarity, read-request disable, SOF pull, dynamic refresh rate min/max selection, trigger A/B source and pipe selections, flow-control sources and polarity, stereo, blanking, interlace, forced vsync, snapshots, update locks, double buffering, DRR average frames, vertical interrupts, CRC source/data modes, external timing sync, static-screen signaling, 3D structure, sync polarity, repetition counts, master/DRR update lock selection, GSL/master mode, PTI, and pipe abort.
- DMCUB/RBBMIF/IHC/DMU/DCCG/HPD enums: DMCUB timer/interrupt type, invalid-register-access type, DMU GPU timer read/start selection, interrupt line status, DMU clock gating and SMU interrupt controls, DCCG enable/clear/reference-source/clock-source selections, deep-color, refclock and DP refclock sources, pipe pixel-rate and PHY PLL sources, DTO/audio DTO selections, DISPCLK ramp and FIFO error detection, global memory power request disable, DCCG performance selects, soft resets, DVO skew/phase controls, vsync counter controls, and HPD interrupt acknowledge/polarity/RX acknowledge.
- DP/DIG/link and sideband enums: DisplayPort entries cover MSO link count, sync polarity, combine pixel count, link training completion, embedded-panel mode, pixel encoding, component depth, lane count, stream disable/defer/ack/mask, M/N generator settings, enhanced frame mode, DPHY lane pattern/test controls, 8b/10b reset/current disparity, PRBS/FEC/CRC, fast training, secondary packet/audio/MST scheduling, MSA override, DSC mode, and link training switch mode. DIG/HDMI/TMDS entries cover HDMI keepout, clock-channel rate, null/audio/ACR/GC/ISRC/MPEG/generic packet send/continuous controls, deep color, audio layout/CRC/ramp controls, TMDS color/pixel/control data selection, DIG FE/BE source and HPD selects, FIFO/test pattern controls, AFMT interrupt and audio source controls, Dolby Vision/metadata routing, and HDMI metadata packet timing.
- DP AUX, DOUT I2C, DIO_MISC, and DCIO enums: AUX entries define HPD selection, test mode, software go, link-service read trigger, arbitration priority/register ownership, ack fields, PHY TX/RX timing windows, thresholds, GTC sync controls, error acks, reset/done, and PHY wake priority. DOUT I2C entries define software transaction start/reset, DDC select, transaction count, arbitration, ack, DDC speed/drive/EDID detect controls, stop-on-NACK, data index writes, and read-request interrupt type. DIO/DCIO entries cover display I/O memory power, clock gating, soft resets, DAC/TMDS muxing, generic stereosync, HDMI RX status timer type, DX protection, generic clock output selection, UNIPHY clock/link/channel controls, LVTMA panel power sequencing, backlight PWM, group/frame update locking, GSL/genlock/swaplock masks, GPU timer start position, and DCIO clock test/gate selection.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime use is indirect:

1. Navi10-era AMDGPU components include `navi10_enum.h` alongside register offset and mask headers.
2. Driver code chooses a symbolic enum value based on DRM plane, stream, link, tiling, cursor, timing, power, interrupt, or debug state.
3. Generated register helpers pack the enum's integer into the correct bitfield and write or read the actual hardware register.
4. Hardware blocks such as HUBP, MPC, MPCC, OPP, OTG, DCCG, HPD, DP, DIG, AUX, I2C, DCIO, GFX, GMC, GFXHUB, MMHUB, and ATHUB interpret the numeric value.

The header therefore forms a compile-time ABI between software policy code and Navi10 register specifications. It does not sequence hardware by itself; sequencing lives in display core, DCN register programming paths, amdgpu memory/hub setup, link training, modeset, page-flip, cursor, hotplug, AUX/DDC, and debug/performance-counter code.

## State And Persistence Behavior

The enums store no software state and persist nothing. The values describe stateful hardware fields whose contents can persist in registers until overwritten, reset, power-gated, or restored after suspend/resume.

State represented by this chunk includes cache policy and fault/request types, GDS performance event selection, surface format and tiling metadata, cursor and plane format/address mode, DCC/TMZ flags, flip/update lock and interrupt behavior, color conversion/LUT selection, scaler setup, CRC/perfmon state machines, display pipe timing and synchronization, MPCC blending and composition, dithering/truncation/FRC behavior, clock-source selection, hotplug and interrupt acknowledge bits, DP link and PHY training state, HDMI/audio packet generation, AUX/DDC/I2C ownership and transaction status, panel power/backlight controls, and genlock/swaplock grouping.

Several enum names encode write-one-to-clear or acknowledge semantics, for example `*_ACK`, `*_CLEAR`, and interrupt status controls. The header does not mark access type, side effects, reset values, or whether fields are read-only, write-only, latched, self-clearing, double-buffered, or timing-sensitive. Consumers must follow the relevant register programming model.

## Dependencies And Integration Points

Direct includes in this tree include Navi10/GFX10-era and later AMDGPU blocks such as `amdgpu/gfx_v10_0.c`, `amdgpu/gmc_v10_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/mmhub_v2_0.c`, and newer hub/GFX variants that reuse the generated enum namespace. The header is also parallel to `soc21_enum.h` and `soc24_enum.h`, which carry many equivalent enum names for later ASIC generations.

Display integration is mostly through AMD DC/DCN register programming. Plane and cursor paths map DRM formats, tiling, cursor attributes, and update locks into DC-facing types, then lower layers program registers using generated enum values and masks. Link and connector paths use DP, DIG, HDMI, AUX, I2C/DDC, HPD, DCCG, and DCIO values during modeset, link training, MST/audio metadata programming, EDID/AUX transactions, hotplug handling, panel power sequencing, and backlight control.

The enum values must remain synchronized with Navi10 register field definitions and companion generated headers that provide register addresses, field masks, and field shifts. Renaming a value usually causes a build failure; changing the underlying integer can compile cleanly but program the wrong hardware mode.

## Risks And Edge Cases

- Numeric drift is the primary risk. A wrong enum value for `SURFACE_PIXEL_FORMAT`, swizzle/tile geometry, `DP_PIXEL_ENCODING`, `DP_COMPONENT_DEPTH`, `CURSOR_MODE`, `MPCC_CONTROL_MPCC_MODE`, `OTG_*`, `DCCG_*`, `DP_AUX_*`, or `DOUT_I2C_*` can compile but produce corruption, blank displays, failed link training, bad colors, broken EDID reads, incorrect cursor rendering, or hard-to-reproduce interrupt behavior.
- This chunk crosses many hardware domains. Some enum names are generic (`ENABLE`, `INT_MASK`, `CLOCK_GATING_EN`, `SOFT_RESET`) and can collide conceptually with other headers even when C enum constants live in the same global namespace. Consumers need the correct ASIC header and matching register field.
- Reserved values are explicitly present in many enums. Accidentally using reserved values in normal paths can rely on undefined hardware behavior.
- Some names reflect generated-source typos or legacy spellings, such as `ONE_SHADER_ENGIN`, `SURFACE_INUSE_RAED_NO_LATCH`, `HDMI_DEFAULT_PAHSE`, and `DPHY_8B10B_RESETET`. Cleanup-style renames would break consumers unless all users and generated headers are updated together.
- Interrupt ack/clear enums may have inverted-looking semantics relative to ordinary booleans. Treating `*_ACK`, `*_CLEAR`, and mask fields as plain enable bits can miss or spuriously clear interrupts.
- Display timing, update-lock, double-buffer, DRR, external sync, genlock, and swaplock values are sequencing-sensitive. Correct constants still need to be written at the right vblank/update point.
- The chunk boundary leaves only the comment for `DCIO_DIO_OTG_EXT_VSYNC_MUX`; the enum body starts in the next chunk. Final reconciliation should not claim this chunk contains that definition.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU with Navi10/GFX10/DCN display support enabled so all enum names referenced by GFX, GMC, GFXHUB, MMHUB, ATHUB, and display code compile.
- Mechanically compare enum names and integer values against the authoritative Navi10 register database and generated address/mask headers.
- Diff common enum families against `soc21_enum.h`, `soc24_enum.h`, and older DCE enum headers where hardware compatibility is expected, while allowing known ASIC-generation differences.
- Exercise modesets across RGB/YCbCr formats, 6/8/10/12 bpc, HDMI and DP, MST/SST, DSC/FEC-capable links, hotplug, EDID over DDC and AUX, backlight/panel power sequencing, page flips, cursor formats, rotation/mirroring, DCC/TMZ surfaces, variable refresh/DRR, suspend/resume, and display CRC/debug paths.
- Watch for kernel warnings, DC link-training failures, AUX/I2C timeouts, HPD storms, underflow or FIFO errors, incorrect CRCs, color/format mismatches, blank displays, broken audio infoframes, cursor artifacts, and regressions that appear only with multi-plane blending or multi-display timing synchronization.

## Cross-Chunk Notes

This is the opening chunk of `navi10_enum.h`, so it includes the license and file guard but not the final guard close. Later chunks continue the DCIO enum namespace beginning with `DCIO_DIO_OTG_EXT_VSYNC_MUX` and then cover the remaining ASIC enum families. The final per-file report should merge all chunks before making whole-file claims about the generated Navi10 enum set.
