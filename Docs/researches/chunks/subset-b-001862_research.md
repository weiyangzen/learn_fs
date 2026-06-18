# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 7648-10228

## Purpose

This chunk is generated AMD DCN 3.1.5 register-address metadata. It contains no executable C logic; it publishes `#define` constants for register offsets and their associated base-index selectors. The companion `dcn_3_1_5_sh_mask.h` header provides field masks and shifts, while this offset header gives the address half used by display-driver register helper macros.

Although this file lives under a local `ceph-client` source mirror, the content is AMDGPU display-engine hardware metadata and has no Ceph or distributed-filesystem behavior.

The requested range starts in the middle of the ABM0 ambient-backlight histogram-result block and ends in the middle of the DIG2 HDMI/audio packet block. Within those boundaries, it covers:

- The tail of `ABM0` histogram readback and backlight master lock offsets.
- Full `ABM1`, `ABM2`, and `ABM3` ambient-backlight/PWM blocks.
- OPP blocks for pipes 0 through 3: display pipe generator (`DPG`), formatter (`FMT`), OPP buffer, OPP pipe control, and OPP pipe CRC registers.
- DSC remap/forwarding (`DSCRM0` through `DSCRM2`), OPP top-level controls, and `DC_PERFMON16`.
- ODM input controls 0 through 3 and OTG timing generator blocks 0 through 3.
- OPTC miscellaneous controls and `DC_PERFMON17`.
- Hotplug-detect blocks `HPD0` through `HPD4`.
- DisplayPort link/PHY/secondary-data/MST/DSC/ALPM/GSP offsets for `DP0`, `DP1`, and `DP2`.
- Digital front-end/HDMI/audio formatter offsets for `DIG0` and `DIG1`, plus the beginning of `DIG2`.

This slice has 2,385 `#define reg...` lines: 1,193 register-offset constants and 1,192 `_BASE_IDX` constants. The one-count mismatch is intentional for the chunk boundary: line 10228 includes `regDIG2_HDMI_DB_CONTROL`, while its `_BASE_IDX` appears after this range.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocations, locks, or direct persistence APIs in this chunk. Its public interface is the generated macro naming convention:

- `reg<REGISTER_OR_INSTANCE>`: register offset within a DCN base segment.
- `reg<REGISTER_OR_INSTANCE>_BASE_IDX`: selector for the base segment used by `BASE(reg..._BASE_IDX)` in DCN315 consumers.

Important register families in this range:

- ABM/PWM: `regABM*_BL1_PWM_*`, `regABM*_DC_ABM1_*`, ACE slopes/thresholds, luma statistics, histogram sample/bin/result registers, and backlight master locks. These are the address constants for adaptive backlight management and panel backlight PWM state.
- OPP/display formatter: `regDPG*_*`, `regFMT*_*`, `regOPPBUF*_*`, `regOPP_PIPE*_*`, and `regOPP_PIPE_CRC*_*`. These support output-pixel formatting, clipping/clamping, 4:2:2 conversion, dithering, pipe blank/control, buffer controls, and CRC diagnostics.
- DSC/OPP top/perfmon: `regDSCRM*_*`, `regOPP_TOP_*`, `regOPP_ABM_CONTROL`, and `regDC_PERFMON16_*`. These support DSC forwarding/remap, shared OPP controls, ABM selection, and OPP-side performance counters.
- OPTC/ODM/OTG: `regODM*_*`, `regOTG*_*`, `regOPTC_*`, `regDWB_SOURCE_SELECT`, and `regDC_PERFMON17_*`. These are timing-compositor addresses for ODM input selection, OTG totals/blanking/sync, vertical interrupts, trigger controls, CRC, lock/unlock, global swap lock, generated test signals, stereo, static-screen, double-buffer controls, and timing perf counters.
- HPD: `regHPD*_DC_HPD_*` for interrupt status/control, control, fast-training status, interrupt filter, RX interrupt timer, and toggle filter control.
- DP link encoders: `regDP*_DP_LINK_CNTL`, training controls, MSA/MSE timing and allocation registers, DPHY symbols/scrambling/CRC/fast-training, secondary-data packet controls, audio N/M timestamp registers, DSC, DB, ALPM, and GSP packet controls/status.
- DIG/HDMI front ends: `regDIG*_DIG_*`, `regDIG*_HDMI_*`, `regDIG*_AFMT_*`, `regDIG*_TMDS_*`, `regDIG*_DIG_BE_*`, and `regDIG*_FORCE_DIG_DISABLE` for digital encoder setup, output CRC/test patterns, HDMI metadata/audio/infoframes/generic packets, ACR values, audio formatter, backend enable, TMDS, and forced disable. `DIG2` is incomplete in this slice and stops at `regDIG2_HDMI_DB_CONTROL`.

The `_BASE_IDX` values map most OPP/OPTC/HPD/DP/DIG instance registers to segment 2 or 3. DCN315 users define constants such as `DCN_BASE__INST0_SEG2` and `DCN_BASE__INST0_SEG3`, then compute absolute MMIO addresses with expressions like `BASE(regX_BASE_IDX) + regX`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes this generated offset header and the matching shift/mask header.

Typical flow:

1. DCN315 DMUB, IRQ, GPIO, and resource code include `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Those source files define DCN base segment constants such as `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`.
3. Token-paste helper macros such as `REG_OFFSET_EXP`, `REG`, `SRI`, `SRI_DMUB`, `REGI`, and block-specific register-list macros combine `reg..._BASE_IDX` and `reg...` values into absolute MMIO offsets.
4. Higher-level display objects use the resulting register tables to program hardware during resource construction, modesets, interrupt acknowledgment, HPD/DDC/GPIO handling, DMUB setup, link training, timing generation, stream encoding, audio packet generation, panel backlight adjustment, diagnostics, and suspend/resume restore.

The offsets alone do not encode ordering or access side effects. Consumers must still follow hardware programming sequences for pipe disable/enable, OTG locking, vertical blank updates, double-buffer commits, HPD interrupt acknowledgment, DP link training, audio packet setup, ABM updates, CRC/perfmon readback, and power/clock gating.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes addresses for MMIO-backed GPU display state. State represented by these definitions includes:

- ABM and backlight state: ambient-light level, user/target/current/final PWM duty, minimum duty cycle, update sample rate, ABM control, register locks, ACE coefficients, luma statistics, histogram configuration, histogram bins/results, and master locks.
- OPP pipe state: DPG control/status, formatter clamp/dynamic-expansion/dither/bit-depth/420 memory controls, OPP buffer controls, pipe enable/control, and per-pipe CRC controls/results.
- Shared OPP and perfmon state: DSC forwarding, OPP clock/debug/spare/ABM controls, and performance counter selection, run state, repeat count, interrupt status/ack, and counter high/low values.
- OPTC/OTG state: ODM input sources, H/V totals, blanking, sync timing, control flags, vertical interrupt positions, dynamic timing controls, global swap lock, CRC windows/results, generated test pattern state, static-screen controls, double-buffer controls, trigger controls, and timing generator spare registers.
- HPD state: hotplug status, interrupt enable/ack/filter, RX interrupt timer, control bits, fast-training status, and debounce/toggle filtering.
- DP/DIG state: DP link control, main-stream attributes, training patterns, DPHY symbols/scrambler/CRC/fast-training, secondary-data packet framing, audio N/M/timestamp, MST allocation, DSC/MSO/ALPM/GSP controls, digital front-end controls, HDMI infoframes/generic packets/metadata/audio, ACR values, audio formatter, TMDS, backend enable, and forced-disable state.

Persistence is hardware-defined. Some registers hold configuration until a modeset, link retrain, panel power transition, suspend/resume, clock/power-gating event, or ASIC reset. Others are read-only status, sticky interrupt, write-one-to-clear, double-buffered, self-clearing, or diagnostic readback registers. This generated offset header does not distinguish those access classes; consumer code and hardware documentation provide that context.

## Dependencies And Integration Points

This chunk must match AMD's generated DCN 3.1.5 register database and its companion field header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`

Key integration points:

- `dmub_dcn315.c` builds `dmub_srv_dcn315_regs` by expanding register and field lists through DCN315 base/offset macros. Although the DMUB list is mostly outside this specific OPP/OPTC/DIO slice, it depends on the same generated offset/field scheme and base-index mapping.
- `dmub_srv.c` selects `dmub_srv_dcn315_regs` for `DMUB_ASIC_DCN315`, allowing common DMUB service code to issue register reads/writes through the populated DCN31 register table.
- `irq_service_dcn315.c` maps hardware interrupt source IDs to DAL IRQ sources and uses `SRI`/`SRI_DMUB` expansions for enable and ack registers. The HPD and OTG families in this chunk are directly relevant to hotplug, HPDRX, vblank, vline, and vupdate interrupt plumbing.
- `hw_factory_dcn315.c` and `hw_translate_dcn315.c` use generated offsets/masks to build HPD/DDC/generic GPIO register tables and to translate GPIO IDs to MMIO offsets. The HPD blocks in this chunk are the register-address side for that hotplug handling.
- `dcn315_resource.c` constructs the DCN315 resource pool, IRQ service, DIO, and stream encoders. Its display objects ultimately rely on these generated offsets for timing generators, OPPs, link encoders, digital encoders, audio/HDMI packet registers, and panel/backlight control paths, even when the register tables are assembled through inherited DCN3.x macros.
- Clock-manager, DML, and HWSS code do not necessarily include this header directly, but their modeset and bandwidth decisions are realized through the OPP/OPTC/DIO/ABM register programming described by these offsets.

## Risks And Edge Cases

- Generated macro drift is the main risk. A wrong offset or base index compiles cleanly but can program the wrong MMIO address, causing display corruption, missed interrupts, bad link training, audio failure, or hangs.
- The chunk boundaries are artificial. The previous chunk owns the start of the ABM0 block, and the next chunk owns the `_BASE_IDX` for `DIG2_HDMI_DB_CONTROL` plus the rest of DIG2. File-level reconciliation must merge adjacent chunks before making complete claims about ABM0 or DIG2.
- Base-index mistakes are as dangerous as offset mistakes. The same small register offset added to the wrong `DCN_BASE__INST0_SEG*` segment targets a different hardware island.
- ABM/PWM offsets are panel-facing. Bad address constants can produce incorrect brightness transitions, broken adaptive backlight behavior, stale histogram reads, or register-lock misuse.
- OPP/FMT/CRC offsets affect pixel output. Wrong formatter or OPP pipe addresses can break color expansion, dithering, 4:2:0/4:2:2 behavior, pipe enablement, blanking, or CRC diagnostics.
- OTG/OPTC offsets are timing-critical. Misaddressed totals, blanking, sync, trigger, lock, vline, or vupdate registers can create unstable modesets, missed flips, stuck interrupts, or visible timing glitches.
- HPD offsets are interrupt-sensitive. Incorrect status, control, filter, or ack addresses can cause lost hotplug events, repeated HPD storms, failed HPDRX/AUX handling, or slow connect/disconnect detection.
- DP/DIG offsets are link- and audio-critical. Mistakes in training, MSA/MSE, secondary-data, DSC/MSO, ALPM, GSP, HDMI infoframe, ACR, AFMT, or TMDS addresses can prevent displays from lighting, break MST/DSC, corrupt metadata, or lose HDMI/DP audio.
- Perfmon and CRC blocks are diagnostic but side-effectful. Bad run, select, status, or ack offsets can make validation data misleading or leave performance/CRC interrupt state uncleared.

## Test Signals

Useful validation combines generated-header consistency checks, build checks, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail at compile time in DCN315 DMUB, IRQ, GPIO, and resource code.
- Mechanically verify that every complete register macro in this chunk has a paired `_BASE_IDX`, allowing the known boundary exception for `regDIG2_HDMI_DB_CONTROL`.
- Compare this chunk against AMD's authoritative DCN 3.1.5 register database and adjacent DCN 3.1.x/DCN 3.6 offset headers where the hardware blocks are expected to stay layout-compatible.
- Exercise panel brightness and ABM paths: PWM duty programming, ambient/user/target/current/final level reads, histogram/luma readback, ABM lock behavior, and suspend/resume restore.
- Exercise OPP and formatter paths: modesets across color depths and pixel encodings, dithering, dynamic expansion, 420/422 conversion, CRC generation/readback, pipe blank/unblank, and multi-pipe operation.
- Exercise OTG/OPTC timing: vblank/vline/vupdate interrupts, global swap lock, vertical interrupt controls, double-buffer update timing, test-pattern generation, CRC windows, and static-screen controls across four timing generators.
- Exercise HPD handling on ports 0 through 4: connect/disconnect debounce, HPD IRQ acknowledgement, HPDRX interrupt routing, fast-training status reads, and repeated plug/unplug stress.
- Exercise DP link training and stream setup for DP0 through DP2: link control, training pattern transitions, MSA timing, MST allocation, DSC/MSO, secondary-data packets, ALPM, GSP packet controls, and link CRC diagnostics.
- Exercise DIG/HDMI paths: HDMI metadata, audio packet controls, infoframes, generic packets, ACR values, AFMT controls, TMDS setup, backend enable/disable, and forced digital disable. For DIG2, include the next chunk before validating the complete HDMI/audio register set.
- Exercise suspend/resume and display hotplug while active streams are running to catch stale base-index mappings, lost restore state, and interrupt ack mistakes.

## Cross-Chunk Notes

The previous chunk owns the beginning of `dce_dc_opp_abm0_dispdec`, including ABM0 PWM controls, ACE/luma setup, histogram bin controls, and `HG_RESULT_1` through `HG_RESULT_5`. This chunk starts at `regABM0_DC_ABM1_HG_RESULT_6`.

The next chunk owns `regDIG2_HDMI_DB_CONTROL_BASE_IDX` and the rest of the DIG2 HDMI/audio formatter/TMDS/backend register block. The final per-file research document should merge these boundaries before summarizing the complete ABM0 or DIG2 register inventories.
