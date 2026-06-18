# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 7884-10415

## Scope And Purpose

This chunk is generated AMD DCN 2.1 display register-offset metadata. It contains no executable C logic; its public surface is a sequence of `#define` constants that name MMIO registers and their corresponding base-index segments for the Renoir/DCN21 display engine.

The file lives under a `ceph-client` source mirror, but this range is entirely AMDGPU Display Core hardware metadata. The macros are consumed by DCN21 resource, GPIO, interrupt, link/stream encoder, AUX/DDC, and DMUB register-table code through generated register-list macros and register helper APIs.

The range starts at the tail of `dce_dc_optc_odm3_dispdec`, covers complete `ODM4` and `ODM5` input blocks, all six `OTG0` through `OTG5` timing-generator blocks, OPTC misc/performance-monitor blocks, DIO I2C/misc/HPD/AUX blocks, complete `DIG0`/`DP0` and `DIG1`/`DP1` blocks, and ends part-way through the `DIG2` block at `mmDIG2_AFMT_GENERIC_6`. The next chunk is needed for complete `DIG2` coverage.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or persistent software objects in this chunk. The interface is the generated AMD register-offset naming contract:

- `mm<register_name>` gives the register offset used by register-list initialization.
- `mm<register_name>_BASE_IDX` gives the segment selector used by `BASE(...)`, `REG_OFFSET(...)`, `SRI(...)`, `SRII(...)`, `REGI(...)`, and similar register-table macros.
- All visible `_BASE_IDX` values in this chunk are `2`, meaning these offsets resolve through the DCN/DC display base segment selected by the including code.

The chunk contains 1,210 register offset symbols and 1,210 matching `_BASE_IDX` symbols. Major macro families are:

- ODM/OPTC input macros: the tail of `mmODM3_OPTC_*`, complete `mmODM4_OPTC_*`, and complete `mmODM5_OPTC_*` input controls for data source selection, format, bytes-per-pixel, width, input clock, memory config, and spare registers.
- OTG macros: complete `mmOTG0_` through `mmOTG5_` timing generator register sets. Each instance has 105 registers covering horizontal/vertical totals, blanking, sync, trigger controls, status/readback, counters, stereo/interlace, snapshots, interrupts, update locks, blank/black colors, CRC windows/data, static-screen detection, 3D structure, global sync lock, vstartup/vupdate/vready, DRR, request control, DSC start position, pipe update status, and spare registers.
- OPTC misc macros: `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, `mmODM_MEM_PWR_CTRL*`, `mmODM_MEM_PWR_STATUS`, and `mmOPTC_MISC_SPARE_REGISTER`.
- Display performance monitor macros: `mmDC_PERFMON17_*` for OPTC and `mmDC_PERFMON18_*` for DIO, including counter control/state, perfmon control, interrupt/misc value, and high/low counter readback registers.
- DIO I2C/DDC macros: `mmDC_I2C_*` controls for arbitration, interrupts, software status, DDC1-DDC5 hardware status, per-DDC speed/setup, transaction slots, data, EDID-detect control, and read-request interrupt.
- DIO misc macros: `mmDIO_SCRATCH*`, `mmDCE_VCE_CONTROL`, DIO memory power status/control, DIO clock control, DIO power management, `mmDIG_SOFT_RESET`, HDMI RX status timer, PSP interrupt status/clear, and generic interrupt message/clear registers.
- HPD macros: `mmHPD0_` through `mmHPD4_` hotplug-detect status/control, interrupt control, fast-train control, and toggle-filter control.
- AUX macros: `mmDP_AUX0_` through `mmDP_AUX4_` AUX channel control, software control/status/data, arbitration, interrupt control, LS status/data, AUX DPHY TX/RX control/status, GTC sync control/status, error control, controller status, and PHY wake control.
- DIG stream-encoder macros: complete `mmDIG0_` and `mmDIG1_` register families, plus the first 43 `mmDIG2_` entries. These cover DIG front-end controls, output CRC, test/random patterns, FIFO status, HDMI metadata/generic packets, HDMI control/status, audio/ACR/VBI/infoframe packets, AFMT audio metadata and status, IEC 60958, audio CRC/ramp controls, DIG back-end controls, TMDS control/pattern registers, version/lane enable, AFMT control, and forced DIG disable. `DIG2` is incomplete in this chunk.
- DP link macros: complete `mmDP0_` and `mmDP1_` DisplayPort link families. They cover link control, pixel format, MSA colorimetry/timing parameters, video stream controls, link frame and secondary data control, DPHY control/status/test/training/scrambling/CRC, audio M/N and timestamp, Multi-Stream Transport MSE rate/SAT/link-timing/status controls, DSC control, metadata transmission, DSC bytes-per-pixel, and ALPM control.

Address-block inventory in this chunk:

- Partial previous block: tail of `dce_dc_optc_odm3_dispdec`, 3 visible registers.
- `dce_dc_optc_odm4_dispdec`, base `0x100`, 8 registers.
- `dce_dc_optc_odm5_dispdec`, base `0x140`, 8 registers.
- `dce_dc_optc_otg0_dispdec` through `dce_dc_optc_otg5_dispdec`, bases `0x0`, `0x200`, `0x400`, `0x600`, `0x800`, and `0xa00`, 105 registers each.
- `dce_dc_optc_optc_misc_dispdec`, base `0x0`, 8 registers.
- `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec`, base `0x79a8`, 9 registers.
- `dce_dc_dio_dout_i2c_dispdec`, base `0x0`, 26 registers.
- `dce_dc_dio_dio_misc_dispdec`, base `0x0`, 24 registers.
- `dce_dc_dio_hpd0_dispdec` through `dce_dc_dio_hpd4_dispdec`, bases `0x0`, `0x20`, `0x40`, `0x60`, and `0x80`, 5 registers each.
- `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec`, base `0x7d10`, 9 registers.
- `dce_dc_dio_dp_aux0_dispdec` through `dce_dc_dio_dp_aux4_dispdec`, bases `0x0`, `0x70`, `0xe0`, `0x150`, and `0x1c0`, 19 registers each.
- `dce_dc_dio_dig0_dispdec`, base `0x0`, 88 registers.
- `dce_dc_dio_dp0_dispdec`, base `0x0`, 73 registers.
- `dce_dc_dio_dig1_dispdec`, base `0x400`, 88 registers.
- `dce_dc_dio_dp1_dispdec`, base `0x400`, 73 registers.
- `dce_dc_dio_dig2_dispdec`, base `0x800`, 43 visible registers in this chunk, continuing later.

## Control Flow

This header has no runtime control flow. It is declarative hardware metadata. Control flow appears in consumers that include this offset header together with `dcn_2_1_0_sh_mask.h` and then build register tables or issue MMIO accesses.

Representative flow:

- DCN21 code includes `dcn/dcn_2_1_0_offset.h`, `dcn/dcn_2_1_0_sh_mask.h`, and `renoir_ip_offset.h`.
- Register-list macros such as `SR`, `SRI`, `SRII`, `REG`, and `REGI` concatenate block and register names into `mm...` and `mm..._BASE_IDX` symbols from this header.
- The `BASE(mm..._BASE_IDX) + mm...` expression produces the final register address stored in per-block register tables.
- Runtime display objects then use helper APIs such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, `REG_SET`, and field-specific variants with the generated address tables and masks.

Important control-flow users:

- `display/dc/resource/dcn21/dcn21_resource.c` uses this header to construct DCN21 resource register tables. The macros in this chunk feed timing-generator, OPTC, DIO, AUX/DDC, DIG, DP, and other display object register addresses used during resource creation and modeset programming.
- `display/dc/irq/dcn21/irq_service_dcn21.c` includes this header for DCN21 interrupt service setup. The OTG vertical interrupt and HPD-related register families in this chunk are part of the hardware surface used by vblank, vline, vupdate, page-flip, HPD, and HPDRX interrupt handling.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` includes this header and builds HPD and DDC GPIO register tables. The `mmHPD*_DC_HPD_*` and `mmDC_I2C_*` families are the relevant chunk content.
- `display/dc/gpio/dcn21/hw_translate_dcn21.c` uses the same generation-specific register definitions to map logical GPIO/DDC/HPD objects to hardware instances.
- `display/dmub/src/dmub_dcn21.c` includes this header for DMUB service register construction. Although this chunk is mostly display pipe/DIO metadata, it shares the same generated base-address contract used by DMUB register helpers.

The generated header does not encode sequencing rules. Consumers must still program hardware in the order required by Display Core: pipe setup, timing lock/update, link encoder setup, AUX/DDC transactions, HPD interrupt enablement, DP link training, HDMI/DP packet programming, audio infoframe programming, CRC/test setup, and power-management transitions.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The macros point at hardware registers whose values live in the DCN21 display engine and may be reset, retained, latched, or self-cleared according to hardware semantics outside this file.

The represented state includes:

- ODM/OPTC input state: data source selection, pixel format, bytes per pixel, input width, clock control, and memory configuration for output data merger paths.
- OTG timing state: horizontal and vertical totals, blanking windows, sync positions, DRR total limits, vstartup/vupdate/vready timing, global sync lock state, master/update locks, and request/update state for each of six timing generators.
- OTG status and diagnostics: frame/HV/VF counters, snapshot position/frame, interlace/stereo status, CRC windows and readback data, range timing interrupt status, global sync status, pipe update status, and pixel readback.
- DIO physical/logical state: DIO scratch registers, clock and memory power control/status, soft reset, power management, PSP/generic interrupt state, and HDMI RX status timer configuration.
- Connector detection state: HPD interrupt status/control and toggle filtering for five HPD instances.
- AUX/DDC transaction state: DDC arbitration/status/speed/setup/transaction/data registers and AUX request/status/data/interrupt/DPHY/GTC/PHY-wake registers for five AUX channels.
- DIG/HDMI/AFMT state: stream source selection, HDMI packet controls, audio packet/ACR/infoframe metadata, generic packets, AFMT status, IEC 60958 channel status, audio CRC/ramp controls, TMDS controls, lane enablement, and forced-disable state.
- DP link state: link control, video stream control, MSA timing/colorimetry, DPHY training/test/scrambling/CRC/FEC-related state, secondary packet/audio timing, MST MSE rate and slot allocation state, DSC control, metadata transmission, and ALPM control.
- Performance monitoring state: DC perfmon counters and interrupt/misc value registers for OPTC and DIO performance counter blocks.

Register persistence must be interpreted by the owning hardware block. Configuration registers generally persist until modeset, stream disable, power-gate/reset, suspend/resume, or driver reprogramming. Status, interrupt, clear, force, snapshot, test, CRC, and counter registers can have side effects on read or write. Names such as `*_INT_STATUS`, `*_INTERRUPT_CONTROL`, `*_CLEAR`, `*_MANUAL_TRIG`, `*_COUNT_RESET`, `*_SNAPSHOT_CONTROL`, `*_CRC_*`, `*_TEST_PATTERN`, `*_FAST_TRAINING`, `*_PHY_WAKE_CNTL`, and `*_FORCE_DIG_DISABLE` are signals that consumer code must observe register-specific semantics from the hardware documentation and existing driver patterns.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header convention:

- `dcn_2_1_0_offset.h` supplies the offsets and base-index symbols documented here.
- `dcn_2_1_0_sh_mask.h` supplies the matching field shift/mask symbols for packed register fields.
- `renoir_ip_offset.h` supplies the generation-specific base segment macros used by `BASE(...)` in DCN21 consumers.
- `reg_helper.h` and DC register helper macros provide the compile-time concatenation and runtime MMIO helpers that consume these symbols.

Primary integration points in the local source tree:

- DCN21 resource construction in `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`.
- DCN21 interrupt mapping/service logic in `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`.
- DCN21 GPIO/HPD/DDC factories and translation in `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`.
- DMUB DCN21 register service setup in `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`.
- Shared display object implementations under `display/dc/dio`, `display/dc/dce`, `display/dc/optc`, `display/dc/gpio`, and `display/dc/resource` that consume generation-specific register tables initialized from these macros.
- Higher-level DRM/DC flows for modeset, vblank/vline/vupdate interrupts, page flips, hotplug, EDID/AUX transactions, DP link training, HDMI/DP infoframes, audio packet programming, MST slot allocation, DSC, ALPM, CRC capture, and suspend/resume.

The offset values in this chunk closely mirror other DCN generations for some blocks, but they are still generation-specific ABI. For example, `mmOTG0_OTG_H_TOTAL`, `mmDIG0_DIG_FE_CNTL`, and `mmDP0_DP_DPHY_CNTL` appear across several DCN/DCE headers with compatible names but not always identical offsets. DCN21 consumers should remain bounded to `dcn_2_1_0_*` headers unless intentionally porting or comparing ASIC generations.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or base index can compile cleanly while directing register access to the wrong MMIO address, causing display modeset failures, blank screens, bad timings, broken hotplug, AUX/DDC failures, bad link training, HDMI/DP packet errors, lost audio, or hard-to-debug interrupt behavior.
- The chunk has non-semantic boundaries. It starts in the middle of `ODM3` and ends mid-`DIG2`; whole-file conclusions about those two blocks require adjacent chunk reconciliation.
- Repeated block instances are easy to drift manually. OTG0-5 each have the same 105-register shape with different offsets; HPD0-4, AUX0-4, DIG0-2, and DP0-1 follow similar repeated patterns. A one-instance typo can produce failures only on specific pipes or connectors.
- Base-index correctness matters as much as the numeric offset. The register-list macros add `BASE(mm..._BASE_IDX)` to `mm...`; an incorrect `_BASE_IDX` can target a wrong register segment even when the offset number looks plausible.
- Timing-generator registers are sensitive to programming order. Incorrect use of `OTG_UPDATE_LOCK`, `OTG_MASTER_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, vstartup/vupdate/vready registers, DRR limits, or global sync controls can cause tearing, hangs waiting for vblank/update, bad variable refresh behavior, or multi-display sync failures.
- Interrupt/status/clear registers may be sticky, write-one-to-clear, or latch-on-read depending on the register. HPD, OTG vertical/range timing, DIO PSP/generic, AUX, I2C, AFMT, and perfmon interrupt families need the surrounding driver helper behavior to avoid lost or storming interrupts.
- AUX and DDC offsets affect EDID, link training, DSC capability discovery, HDCP/DPCD transactions, and sink management. Subtle register drift can look like monitor-specific failures rather than a compile-time error.
- DIG and DP blocks mix HDMI, DP, audio, TMDS, MST, DSC, ALPM, CRC, and test controls. Misaddressed packet or link registers can regress only one transport mode, audio format, MST topology, DSC mode, or power-saving state.
- Power and reset registers in `DIO_*`, `ODM_MEM_PWR_*`, `DIG_SOFT_RESET`, and `FORCE_DIG_DISABLE` can disrupt active display paths if written at the wrong time or with the wrong instance.
- Performance counter registers are diagnostic but can still perturb measurement or interrupt behavior if counter control/state registers are misprogrammed.

## Test Signals

Useful validation is a mix of compile-time generation checks and hardware behavior:

- Build AMDGPU/DC with DCN21/Renoir support enabled. Missing or renamed macros should fail in DCN21 resource, GPIO, IRQ, DMUB, and shared display object register table initialization.
- Diff this generated chunk against the expected upstream/generated `dcn_2_1_0_offset.h` and against nearby DCN generation headers to catch unintended offset or `_BASE_IDX` drift, especially in repeated OTG, AUX, HPD, DIG, and DP instances.
- Exercise modesets on DCN21 hardware across all available pipes/connectors: single display, multi-display, clone/extend, rotation/scaling, interlace if supported, suspend/resume, runtime power transitions, and repeated enable/disable cycles.
- Validate vblank, vline, vupdate, page-flip, and range-timing interrupt behavior. Watch for missed interrupts, interrupt storms, stuck flips, delayed page flips, or timeouts waiting for vblank/update locks.
- Validate HPD and HPDRX behavior by hotplugging all physical connectors, including rapid plug/unplug and DP short/long pulse cases. Check that connector status changes, IRQ logs, and userspace DRM events remain correct.
- Validate DDC/AUX paths with EDID reads, DPCD reads/writes, DP link training at multiple link rates/lane counts, MST topology discovery, DSC capability discovery, and AUX wake behavior.
- Validate HDMI and DP stream-encoder behavior: link comes up, correct pixel format/colorimetry/timing, infoframes are correct, audio packets/ACR are stable, CRC capture works when enabled, and test-pattern paths do not affect normal mode.
- Validate MST, DSC, ALPM, FEC/training-related paths where supported by the ASIC and sink, because the `DP0`/`DP1` macro families include MSE, DSC, secondary-data, and ALPM offsets.
- Use debugfs or driver diagnostics to compare OTG counters, CRC readbacks, AUX transaction status, HPD status, and perfmon values with expected behavior during modeset, hotplug, and link-training scenarios.
- For the incomplete `DIG2` range, ensure merge-lane review includes the continuation chunk before judging full third-DIG support.
