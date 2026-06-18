# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 7638-10215

## Purpose

This chunk is a generated AMD DCE 12.0 display-engine register-offset map. It contains only C preprocessor `#define` constants; there are no functions, structs, enums, local variables, branches, or executable statements. The constants name direct MMIO-style register offsets and each offset's `*_BASE_IDX` selector for SOC15 base-address calculation.

The covered range starts in the tail of the DCP5 graphics/color pipeline and then defines the remaining pipe-5 display blocks, virtual display blocks, hotplug/AUX blocks, and the beginning of the first digital encoder and DisplayPort block. Major register families in this chunk are:

- the tail of `DCP5`, covering DCP CRC, DVMM/PTE arbitration, flip-rate, GSL, line-buffer gap, stereo sync, hardware rotation, XDMA underflow/recovery, regamma piecewise-linear tables, alpha control, and surface counters;
- pipe-5 `LB5`, `DCFE5`, `DMIF_PG5`, `SCL5`, `BLND5`, `CRTC5`, and `FMT5` registers for line-buffer, frontend, display memory interface, scaler, blender, timing generator, and formatter programming;
- virtual pipe instances `UNP0/LBV0/SCLV0/COL_MAN0/DCFEV0/DMIFV_PG0/BLNDV0/CRTCV0` and `UNP1/LBV1/SCLV1/COL_MAN1/DCFEV1/DMIFV_PG1/BLNDV1/CRTCV1`;
- hotplug detect instances `HPD0` through `HPD5`;
- display performance monitor instances `DC_PERFMON8`, `DC_PERFMON11`, `DC_PERFMON12`, and `DC_PERFMON2`;
- AUX channel instances `DP_AUX0` through `DP_AUX5`;
- the first digital encoder block `DIG0`, including DIG front/back-end, HDMI, AFMT audio/infoframe, TMDS, CRC, FIFO, and lane-enable registers;
- the first entries of `DP0`, from DP link control through video M/N timing.

The practical purpose is to give DCE 12.0 AMDGPU/DC code stable symbolic names for hardware register offsets. Runtime code combines these constants with SOC15 segment bases, companion field masks, and per-instance offset tables to program display modes, scanout, interrupts, hotplug, AUX transactions, color processing, audio packets, and link state.

## Important APIs, Types, And Macros

There are no runtime APIs or C types in this chunk. The interface is the generated macro namespace:

- `mmBLOCK_REGISTER` macros hold register offsets, for example `mmCRTC5_CRTC_CONTROL`, `mmDP_AUX5_AUX_CONTROL`, `mmDIG0_HDMI_CONTROL`, and `mmUNP1_UNP_GRPH_ENABLE`.
- Every register macro in this range is paired with `mm..._BASE_IDX`, almost always `2`, which consumers pass through `DCE_BASE__INST0_SEG...` style SOC15 base selectors before adding the offset.
- Instance-specific names encode the hardware block and instance directly. For example `mmHPD3_DC_HPD_INT_CONTROL` belongs to HPD instance 3, while `mmDP_AUX4_AUX_SW_CONTROL` belongs to AUX instance 4.
- The chunk does not define bit fields. Callers must use the companion `dce_12_0_sh_mask.h` masks/shifts and generated field helpers.

Important macro families in the covered lines include:

- `mmDCP5_*`: register-gamma LUT/index/data, regamma control regions A/B, alpha, graphics flip/XDMA recovery/status/timeout/average-delay, DCP CRC and surface-counter registers.
- `mmLB5_*`, `mmLBV0_*`, and `mmLBV1_*`: line-buffer data format, memory control/size, desktop height, vline/vblank status, interrupt masks, sync reset selection, keyer colors, buffer urgency/status, no-outstanding-request status, and MVP flip controls.
- `mmDCFE5_*`, `mmDCFEV0_*`, and `mmDCFEV1_*`: display-controller frontend clocking, soft reset, memory power control/status, misc, flush, optional mode control, and request-counter controls.
- `mmDMIF_PG5_*`, `mmDMIFV_PG0_*`, and `mmDMIFV_PG1_*`: pipe arbitration, minimum/maximum requests, urgent/watermark controls, retry watermarks, DVMM status, and pre-processing checks.
- `mmSCL5_*`, `mmSCLV0_*`, and `mmSCLV1_*`: scaler coefficient RAM, tap controls, viewport start/size, overscan, ratios, filter initialization, autohorizontal ratio, rounding, bypass, and mode-change masks.
- `mmBLND5_*`, `mmBLNDV0_*`, and `mmBLNDV1_*`: blender control, feedthrough, alpha mode, viewport start/size, underflow interrupt, and register-update status.
- `mmCRTC5_*`, `mmCRTCV0_*`, and `mmCRTCV1_*`: timing-generator totals, blanking, sync A/B, trigger, control, blank, interlace, status, frame counter, vertical interrupt, update lock, master update, static-screen, CRC, test pattern, stereo, flow-control, snapshots, and DRR/GSL controls.
- `mmFMT5_*`: formatter clamp, dynamic expansion, bit-depth control, control, debug, temporal dither, memory power, CRC, force-output control, and 4:2:0 hblank controls.
- `mmUNP0_*` and `mmUNP1_*`: uniphy graphics enable/control, address/pitch/viewport, update, stereosync, surface-address in-use, DFQ, tiling, color-format, memory power, and rotation registers.
- `mmCOL_MAN0_*` and `mmCOL_MAN1_*`: color-management update, input CSC, prescale, gamut remap, output CSC, gamma correction LUT index/data/control, denorm, alpha, global alpha, color-keyer, cursor, degamma/regamma LUTs, and debug registers.
- `mmHPD0_*` through `mmHPD5_*`: hotplug interrupt status/control, RX interrupt timer, and toggle filter controls.
- `mmDP_AUX0_*` through `mmDP_AUX5_*`: AUX transaction control, arbitration, software data/control, status, DPHY timing/control, interrupt control, retry, GTC sync, and GTC sync status.
- `mmDIG0_*`: digital encoder control/status/test/CRC/FIFO, HDMI packet and ACR controls, AFMT audio/infoframe/generic/ISRC/60958/ramp registers, backend enable, TMDS controls, DIG version, lane enable, and AFMT control.
- `mmDP0_*`: start of DP link/video state, including link control, pixel format, MSA colorimetry/misc, DP config, video stream control, steer FIFO, timing, and M/N registers.

## Control Flow

This header chunk has no control flow. It influences runtime behavior by supplying addresses to code that performs register reads, writes, and read-modify-write operations.

The usual DCE 12.0 flow in consumers is:

1. include `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`;
2. select a SOC15 display base with `mm..._BASE_IDX`;
3. add the register offset from `mm...`;
4. optionally add or select a per-instance offset such as a CRTC pipe offset;
5. read/write the register with DC or AMDGPU helpers such as `dm_read_reg_soc15`, `generic_reg_update_soc15`, `generic_reg_set_soc15`, or resource-table register wrappers;
6. apply field masks/shifts from `dce_12_0_sh_mask.h`.

Concrete patterns in this tree include `display/dc/dce120/dce120_timing_generator.c`, which includes this offset header and reads CRTC status/frame-counter registers through `dm_read_reg_soc15`, and updates timing-generator fields through `generic_reg_update_soc15`. `display/dc/resource/dce120/dce120_resource.c` builds DCE120 instance offsets such as `mmCRTC5_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL` and expands register tables with macros that add `BASE(mm..._BASE_IDX)` to `mm...`. `display/dc/irq/dce120/irq_service_dce120.c` uses instance-specific DCP, CRTC, and HPD register macros to build IRQ enable/status/ack descriptors. GPIO and AUX/link resource code follows the same base-plus-offset convention.

Because this file is only an address map, sequencing rules live outside it. Callers are responsible for update locks, vblank-safe programming, AUX transaction ordering, hotplug interrupt acknowledgment, DP/HDMI link training and packet setup, memory-interface watermarks, and reset/power-gating coordination.

## State And Persistence Behavior

The header itself stores no runtime state and performs no I/O. Its constants are compiled into driver code.

The registers named here control or expose persistent hardware state in DCE 12.0 display blocks. That state can persist until later driver writes, display modesets, hotplug handling, AUX transactions, power-gating transitions, suspend/resume restore, GPU reset, or firmware/BIOS interaction. Relevant state categories include:

- display pipe state: CRTC timing, blanking, sync, frame count, vertical interrupts, update locks, static-screen, DRR, CRC, scaler viewport/filter/tap settings, line-buffer status, formatter clamp/dither/CRC, blender viewport/alpha/underflow status, and DCP regamma/color/alpha state;
- scanout and memory-interface state: UNP graphics surface addresses, pitch, tiling, viewport, DFQ, hardware rotation, memory power, DMIF/DMIFV arbitration, watermarks, request limits, DVMM, and outstanding-request state;
- virtual-pipe state: duplicated UNP/LBV/SCLV/COL_MAN/DCFEV/DMIFV/BLNDV/CRTCV programming for virtual display paths 0 and 1;
- link and connector state: HPD interrupt/timer/filter state, AUX software transaction registers, DP AUX DPHY timing and GTC sync state, DIG0 HDMI/AFMT/TMDS/lane-enable state, and the start of DP0 link/video programming;
- diagnostic state: performance counters, CRC registers, debug registers, underflow status, retry/watermark status, and surface-counter outputs.

The macros do not encode access attributes. Some target registers are read-only status, some are write-only or self-clearing controls, some are sticky interrupt/status bits, and some are double-buffered or latched on update boundaries. Consumers must preserve reserved fields and follow the hardware-specific programming sequence.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus the include guard from the full `dce_12_0_offset.h` file. Practical integration depends on the generated AMD DCE 12.0 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h` supplies masks and shifts for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c` includes this header for timing-generator status and programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c` includes this header to build DCE120 resource register tables and instance offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c` uses this header for HPD, page-flip, vblank, and vupdate IRQ register descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c` and `hw_factory_dce120.c` include this header for GPIO/HPD/DDC mapping.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c` include the companion DCE 12.0 masks and participate in generation-specific programming.
- SOC15 base headers such as `soc15_hw_ip.h` and `vega10_ip_offset.h` provide the segment-base macros used with `*_BASE_IDX`.

The path sits under a repository named `ceph-client`, but this file is AMDGPU display-driver register metadata. It does not implement Ceph filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These constants are untyped integers; using the wrong instance macro, wrong base index, wrong generation header, or wrong field-mask header can compile cleanly while touching the wrong display register.

This chunk has many repeated instance families with similar names. `HPD0` through `HPD5`, `DP_AUX0` through `DP_AUX5`, virtual pipe 0 versus 1, and pipe-5 versus base pipe macros differ by predictable but non-identical offsets. Copy/paste or generator errors can make an interrupt, AUX transaction, or pipe update affect the wrong connector or display path.

The chunk begins at line 7638 in the middle of the `DCP5` register family. Earlier DCP5 graphics, cursor, LUT, CSC, keying, degamma, gamut, and overlay registers are in the previous chunk. It ends at line 10215 after the first `DP0` video M/N entries, so the remainder of the DP0 block and later DP/DIG instances are in following chunks. File-level reconciliation should merge these boundaries before treating the DCP5 or DP0 feature coverage as complete.

Timing and latch hazards are not visible in this file. CRTC, scaler, line-buffer, formatter, color-management, and scanout-address registers may need update locks, vblank coordination, or pipe-disabled programming. AUX, HPD, DP, HDMI, AFMT, TMDS, and DIG registers have protocol-specific ordering and clear-on-write behavior. DMIF/UNP memory and watermarks can cause underflow, hangs, or corrupted scanout if programmed inconsistently with bandwidth and surface state.

Virtual-pipe registers are easy to confuse with physical pipe registers. `UNP*`, `LBV*`, `SCLV*`, `COL_MAN*`, `DCFEV*`, `DMIFV*`, `BLNDV*`, and `CRTCV*` have similar logical roles to physical DCP/LB/SCL/CRTC blocks but are not interchangeable addresses.

## Test Signals

Useful validation signals include:

- build coverage for all DCE120 translation units that include `dce_12_0_offset.h` or `dce_12_0_sh_mask.h`, especially timing-generator, resource, IRQ, GPIO, HW sequence, and GMC paths;
- generated-header checks that each `mm...` macro has the expected `mm..._BASE_IDX`, and that every register used with `REG_SET_FIELD`, `FD`, `generic_reg_update_soc15`, or IRQ table macros has a matching field definition in `dce_12_0_sh_mask.h`;
- static checks around instance arithmetic, especially pipe-5 offsets, `CRTCV0/1`, `HPD0-5`, `DP_AUX0-5`, `DIG0`, and `DP0`;
- modeset tests across all physical and virtual display paths covered by this chunk: enable/disable, vblank counter reads, update-lock behavior, DRR/static-screen, scaler/viewport changes, formatter/color-management changes, and suspend/resume;
- interrupt tests for HPD, HPD RX, page flip, vblank, vupdate, underflow, and AUX/connector events;
- DisplayPort and HDMI tests covering AUX transactions, hotplug debounce/filtering, DP link programming, HDMI/AFMT InfoFrame/audio packet programming, TMDS control, and lane-enable behavior;
- scanout stress tests covering surface address/pitch/tiling changes, XDMA underflow/recovery, UNP/DMIF watermarks, memory power transitions, and rotation;
- diagnostic tests for CRC, performance monitors, surface counters, DCP/CRTC/FMT debug paths, and DP AUX GTC sync status.

Regression symptoms from bad constants include wrong connector hotplug status, missed or stuck interrupts, AUX timeouts, blank displays, DP/HDMI link-training or audio failures, page-flip/vblank drift, underflow reports, incorrect color/gamma, corrupted scanout, or failures that only appear on pipe 5 or virtual display paths.

## Cross-Chunk Notes

This is a middle chunk of `dce_12_0_offset.h`. It starts after earlier DCE12 common, DCP, and pipe-instance definitions and continues the generated address map through DCP5, pipe 5, virtual pipes, HPD/AUX, DIG0, and the opening of DP0. The final per-file research should combine this with adjacent chunks so split logical blocks such as DCP5 and DP0 are described as complete register families.
