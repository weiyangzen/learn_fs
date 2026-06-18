# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 7776-10411

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register-offset metadata. It contains no executable C logic. Its purpose is to publish compile-time MMIO register addresses and register base-index selectors for display-core code that programs DCN 2.0 hardware blocks.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The range covers a large display-pipeline section:

- Tail of `MPCC_OGAM6` and full `MPCC_OGAM7` output-gamma LUT/register windows.
- MPC output color-space-conversion register banks for six outputs plus OCSC debug and MPC perfmon 12.
- OPP/formatter/display-pattern/OPP-buffer/OPP-pipe/OPP-pipe-CRC register instances 0 through 5, plus OPP top, DSCRM 0 through 5, and OPP perfmon 18.
- ODM input register instances 0 through 5.
- OTG timing-generator register instances 0 through 5.
- OPTC miscellaneous, ODM memory power, and OPTC perfmon 19 registers.
- DIO global I2C/DDC engine registers, DIO scratch/power/clock/interrupt registers, and the beginning of HPD0 interrupt registers.

Every hardware register macro appears with a companion `_BASE_IDX` macro. In this chunk almost every `_BASE_IDX` is `2`, which selects the register aperture/base used by the generated AMD register access tables.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated preprocessor naming contract:

- `mm<block>_<register>` gives the register offset used by AMDGPU/DC register access helpers.
- `mm<block>_<register>_BASE_IDX` gives the register base-table index used with that offset.
- Matching bit masks, shifts, and field-value definitions live in the corresponding `dcn_2_0_0_sh_mask.h` and enum headers.

Important macro families in this chunk:

- `mmMPCC_OGAM6_*` and `mmMPCC_OGAM7_*`: output-gamma programming windows for MPCC instances. They define LUT index/data/control registers, mode registers, and RAM A/RAM B per-channel start/slope/end/region registers for blue, green, and red channels. The range begins inside the `MPCC_OGAM6` RAMA/RAMB region list and then covers full `MPCC_OGAM7`.
- `mmMPC_OUT*_CSC_*`: output CSC mode and coefficient registers for MPC outputs 0 through 5. Each output has A and B coefficient banks with packed coefficient pairs such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`, plus global `MPC_OUT_CSC_COEF_FORMAT` and OCSC test-debug index/data registers.
- `mmDC_PERFMON12_*`, `mmDC_PERFMON18_*`, and `mmDC_PERFMON19_*`: display performance counter control, state, current-value interrupt/misc, high, and low counter registers for MPC, OPP, and OPTC-related monitor blocks.
- `mmBL1_PWM_*`: backlight/PWM control, period/counter, current/target duty cycle, group registers, user-level/ABM registers, and gamma/lookup-table index/data registers.
- `mmFMT[0-5]_*`: per-OPP formatter clamp, dynamic expansion, format control, bit-depth, dither random seeds, stereo, 4:2:0 memory control, and 4:2:2 control registers.
- `mmDPG[0-5]_*`: display pattern generator control, ramp, dimensions, RGB/YUV color, offset segment, and status registers.
- `mmOPPBUF[0-5]_*`: OPP buffer control and 3D parameter registers.
- `mmOPP_PIPE[0-5]_*` and `mmOPP_PIPE_CRC[0-5]_*`: per-pipe control and CRC control/mask/result registers used for output validation and diagnostics.
- `mmDSCRM[0-5]_*`: per-output descrambler control registers.
- `mmODM[0-5]_*`: OPTC input controls for data source selection, format, bytes per pixel, width, clock control, memory configuration, and spare registers.
- `mmOTG[0-5]_*`: large per-timing-generator banks covering horizontal/vertical totals, blanking and sync windows, variable refresh totals, triggers, flow control, interlace, readback, status counters, update locks, master enable, blank/black colors, vertical interrupts, CRC windows/results/masks, global sync lock/update controls, GSL windows, DRR, DSC start position, pipe update status, and spare registers.
- `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, `mmODM_MEM_PWR_*`, and `mmOPTC_MISC_SPARE_REGISTER`: OPTC-wide source, clock, memory-power, status, and spare controls.
- `mmDC_I2C_*`: global DC I2C/DDC control, arbitration, interrupt, status, six DDC channel status/speed/setup pairs, transaction descriptors, data, VGA DDC setup, EDID-detect, and read-request interrupt registers.
- `mmDIO_*`, `mmDCE_VCE_CONTROL`, and `mmDIG_SOFT_RESET`: DIO scratch registers, DIO memory power/clock controls, power-management control, DIG reset, HDMI RX status timer, PSP/generic interrupt status/clear/message registers.
- `mmHPD0_DC_HPD_INT_STATUS` and `mmHPD0_DC_HPD_INT_CONTROL`: first hotplug-detect block interrupt status/control entries. The remainder of HPD0 continues after this chunk.

## Control Flow

This chunk has no runtime control flow. It is declarative register-address metadata consumed by C code through generated register tables and helper macros such as `SR`, `SRI`, `SRI_ARR`, `SRII`, `REG_READ`, `REG_SET`, `REG_UPDATE`, and `REG_GET`.

Representative runtime flows in local consumers:

- `display/dc/resource/dcn20/dcn20_resource.c` includes `dcn_2_0_0_offset.h` and uses these offsets to populate DCN20 resource register tables for MPC, OPP, OPTC, I2C, GPIO, clock, and DMUB-related blocks.
- `display/dc/mpc/dcn20/dcn20_mpc.h` maps `MPCC_OGAM_MODE` as an indexed `MPCC_OGAM` register, and `display/dc/mpc/dcn20/dcn20_mpc.c` writes `MPCC_OGAM_MODE[mpcc_id]` while enabling, disabling, or selecting output gamma modes.
- `display/dc/optc/dcn10/dcn10_optc.h` and related DCN OPTC code map `OTG_H_TOTAL` and `OPTC_INPUT_GLOBAL_CONTROL`; `dcn10_optc.c` writes timing values, reads timing-generator state, checks underflow status, and clears underflow using fields in the matching mask header.
- `display/dc/opp/dcn20/dcn20_opp.c` reads `OPP_PIPE_CRC_CONTROL` into debug/state snapshots, while generic DCE/OPP code programs formatter clamps, dithering, bit depth, and CRC capture through the per-OPP registers defined here.
- `display/dc/dce/dce_i2c_hw.c` drives hardware DDC transactions through `DC_I2C_CONTROL`, transaction descriptors, `DC_I2C_DATA`, status, speed/setup, reset, and arbitration registers.
- `display/dmub/src/dmub_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include this offset header for DCN20 device-service, IRQ, GPIO, and clock/resource integration.

Because this header only supplies constants, it does not enforce sequencing. Consumers must order operations around OTG update locks and double-buffering, MPC/MPCC gamma RAM access, OPP CRC windows, I2C arbitration and soft reset, ODM memory power control, DIO power/clock controls, and HPD interrupt status/ACK behavior.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe hardware MMIO state.

The represented hardware state spans:

- Gamma/color state in MPCC output gamma LUTs and MPC output CSC coefficient banks.
- Output formatting state in FMT clamp, expansion, bit-depth, dither, 4:2:0, 4:2:2, stereo, and OPP buffer controls.
- Test/diagnostic state in DPG generators, OPP pipe CRC windows/results, MPC/OPP/OPTC perfmon counters, and OTG CRC/readback/status registers.
- Timing-generator state in OTG horizontal and vertical totals, blanking, sync, trigger, interlace, VRR/DRR, global sync lock, update-lock, vertical interrupt, DSC, and pipe-update registers.
- Routing and output-combiner state in ODM input source/format/width/clock/memory registers and OPTC source-selection controls.
- Connector sideband state in DC I2C/DDC engine arbitration, status, transactions, speed/setup, EDID detect, and read-request interrupt registers.
- DIO global state in scratch registers, memory power state, clock controls, DIG soft reset, PSP/generic interrupt registers, and HPD0 interrupt status/control.

Persistence is hardware-specific and not encoded in this file. Some registers are durable programming knobs that remain until modeset, reset, suspend/resume, power-gating transition, or an explicit rewrite. Other registers are read-only status, counters, sticky interrupt status, write-one-to-clear controls, self-clearing requests, or double-buffered values latched at vertical update boundaries. The names hint at behavior (`*_STATUS`, `*_CLEAR`, `*_INT_STATUS`, `*_UPDATE_LOCK`, `*_COUNT_RESET`, `*_SOFT_RESET`, `*_MEM_PWR_STATUS`), but access type, reset value, and side effects require the matching hardware register specification and mask headers.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract for DCN 2.0. It is meaningful together with:

- `dcn_2_0_0_sh_mask.h` for field masks and shifts.
- DCN 2.0 enum/value headers for symbolic register field values.
- AMD display register-access helper macros and per-block register-table structures in `drivers/gpu/drm/amd/display/dc`.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration points are DCN20 resource construction, modeset timing programming, ODM/OPTC routing, multi-display synchronization, output gamma and output CSC programming, DRM color-management application, formatter/dither/bit-depth setup, OPP/OTG CRC validation, underflow detection/clear, display perfmon sampling, EDID/DDC transactions, HPD interrupt handling, DIO power/clock/reset management, and debug state collection.

## Risks And Edge Cases

- Numeric offsets are hardware ABI. A wrong offset or base index can compile cleanly while writing the wrong register block, corrupting unrelated display state, or hanging display hardware.
- The chunk boundary is not semantic. It starts inside the `MPCC_OGAM6` RAM region list and ends immediately after HPD0 interrupt status/control, so readers must merge adjacent chunks for complete MPCC6 and HPD0 coverage.
- Instance-indexed families are highly repetitive. Manual edits to `FMT[0-5]`, `DPG[0-5]`, `OPPBUF[0-5]`, `ODM[0-5]`, `OTG[0-5]`, or `MPC_OUT[0-5]` can introduce off-by-one instance drift that affects only some pipes.
- MPCC OGAM and MPC output CSC registers are color-critical. Bad addresses or mismatched masks can cause wrong gamma, color-space conversion errors, visible banding, or incorrect HDR/SDR output transforms.
- OTG registers are timing-critical. Incorrect `OTG_H_TOTAL`, blanking, sync, update-lock, global-sync, DRR, or DSC start-position offsets can produce black screens, flicker, lost vblank, invalid frame pacing, or multi-display synchronization failures.
- ODM/OPTC state is routing-critical. Wrong source, format, width, clock, memory-power, or underflow-clear registers can break multi-pipe combine/split paths or hide real underflow diagnostics.
- I2C/DDC registers interact with external displays. Arbitration, reset, transaction-count, DDC select, data, and speed/setup mistakes can cause EDID read failures, hotplug instability, or stalled sideband transactions.
- Status, clear, reset, and interrupt registers have side effects not visible in this offset header. Consumers must rely on the matching mask headers and hardware docs to avoid clearing sticky state or triggering resets accidentally.
- This generated header is shared by many display modules. Renaming or moving macros without updating register-table users produces build failures; changing values without regeneration can produce runtime-only regressions that tests may miss unless run on DCN20 hardware.

## Test Signals

Useful validation is compile-time plus hardware/display behavior:

- Build AMDGPU/DC with DCN20 support enabled; missing or renamed macros should fail in DCN20 resource, MPC, OPP, OPTC, I2C, GPIO, IRQ, DMUB, and clock-manager paths.
- Diff generated offsets against adjacent DCN families such as `dcn_2_0_1_offset.h`, `dcn_2_1_0_offset.h`, and `dcn_3_0_0_offset.h` to catch unintended instance or base-index drift where hardware is expected to remain compatible.
- Exercise modesets on DCN20 hardware across all available pipes: single display, multi-display, ODM/split scenarios, blank/unblank, suspend/resume, and hotplug cycles.
- Validate timing behavior: vblank/vline delivery, frame counters, update-lock behavior, global sync lock, DRR/VRR changes, DSC start positioning where supported, and absence of underflow after mode changes.
- Validate color/output programming: output gamma LUT changes, output CSC changes, formatter clamp/bit-depth/dither settings, 4:2:0/4:2:2 output modes, and visible color correctness across SDR/HDR-style configurations.
- Validate diagnostics: OPP pipe CRC results, OTG CRC windows/results, MPC/OPP/OPTC perfmon reads, pattern generator output, and debug register snapshots.
- Validate connector sideband behavior: EDID reads through DDC1-DDC6, I2C soft reset/retry paths, read-request interrupts, HPD0 connect/disconnect interrupt status and control, and DIO power/clock transitions.
- Watch negative signals in kernel logs and display behavior: black screens, stuck modesets, missed vblank/page-flip completion, underflow messages, HPD flapping, EDID failures, color shifts, CRC mismatches, display clock/power transition failures, or resume failures.
