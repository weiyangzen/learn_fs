# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 7665-10255

## Purpose

This chunk is generated AMD DCN 3.6 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric register offsets and companion base-index selectors. Consumers combine each `reg...` offset with its matching `reg..._BASE_IDX` through resource, IRQ, and DMUB register-list macros to compute the actual MMIO address for DCN 3.6 display hardware.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The requested range is a large mid-file slice. It starts at the tail of the `ABM1` block with only `regABM1_DC_ABM1_BL_MASTER_LOCK_BASE_IDX`, covers complete `ABM2` and `ABM3` adaptive-backlight blocks, covers OPP/formatter/output-buffer/DPG/DSCRM register families for four OPP pipes, covers ODM and OTG/OPTC timing-generator register families for four timing generators, covers OTG CRC32 readout blocks, covers HPD instances 0 through 4, covers DP/DIG link and stream-encoder register families for instances 0 and 1, and ends inside the `DP2` block at `regDP2_DP_DPHY_FAST_TRAINING_BASE_IDX`. The range contains 2,383 `#define` lines: 1,191 register-offset macros and 1,192 `_BASE_IDX` macros because the chunk begins with a lone base-index line from the previous block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locks in this range. The exported interface is the generated macro namespace:

- `reg<block><instance>_<register>` or `reg<global_register>` constants provide DCN 3.6 register offsets.
- `reg..._BASE_IDX` constants select the base-address segment used by `BASE(reg..._BASE_IDX) + reg...`.
- Address-block comments document the generated register database grouping and per-instance base offset, for example `dce_dc_opp_abm2_dispdec` at base `0x208`, `dce_dc_optc_otg3_dispdec` at base `0x600`, and `dce_dc_dio_dp2_dispdec` at base `0x920`.

Major register families in this chunk:

- `ABM2` and `ABM3`: backlight/PWM level registers, ambient/user/target/current ABM levels, final/minimum duty cycle, ABM control, sample rates, register locks, ACE slopes/thresholds, luma statistics, histogram bins/results, and master lock. The first line is the unmatched `_BASE_IDX` for the previous `ABM1` master-lock offset.
- `DPG0` through `DPG3`, `FMT0` through `FMT3`, `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and OPP pipe CRC registers: output-pixel processing control, dynamic pixel generation/test-pattern support, formatter clamping, 4:2:2 control, OPP buffer control, and pipe CRC controls/results.
- `DSCRM0` through `DSCRM3`: DSC forward configuration for each OPP-side slice/router path.
- Global OPP/top/perfmon symbols: OPP clock/top/ABM controls, GSL source select, OPTC/DLPC/ODM memory power controls/status, spare registers, and DC perfmon counter/control/high/low registers.
- `ODM0` through `ODM3`: OPTC input global/clock/data-source controls, data format, bytes per pixel, width, memory config, RSMU underflow, and underflow thresholds.
- `OTG0` through `OTG3`: timing-generator totals, blanks, syncs, controls, status, vertical interrupts, CRC windows/readbacks, dynamic refresh rate controls, global sync/lock, manual triggers, DSC start position, keepout, and spare registers.
- `OTG_CRC320` through `OTG_CRC323`: 32-bit CRC readout data for OTG CRC channels 0 through 3.
- `HPD0` through `HPD4`: hotplug status/control/toggle-filter registers.
- `DP0`, `DP1`, and partial `DP2`: DisplayPort link, pixel format, MSA, stream timing, video `M/N`, DPHY training/scrambling/CRC/status, MST/secondary packet controls, ALPM, symbol-count status/control, and link-training/test registers.
- `DIG0` and `DIG1`: digital stream encoder front-end/back-end controls, output CRC, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, HDMI status, AFMT bridge control, TMDS controls, sync patterns, DC balancer, and version.

The key consuming types are register-table structs allocated by the DC resource layer, such as `struct dce_abm_registers`, `struct dcn10_timing_generator`, `struct dcn10_link_enc_registers`, `struct dcn10_link_enc_hpd_registers`, `struct dcn10_stream_enc_registers`, and `struct dce110_opp_registers`. These structs receive computed addresses through token-pasting macros rather than by directly naming the generated macros in ordinary C expressions.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code that includes this offset header with the matching `dcn_3_6_0_sh_mask.h` field header.

The main flow is:

1. DCN 3.6 resource construction includes this header and defines helper macros such as `SR`, `SRI`, `SRI_ARR`, `SRI2_ARR`, and `SR_ARR`.
2. Resource register-list macros paste block names and instance IDs into generated symbols. Examples include `SRI_ARR(DC_ABM1_HG_SAMPLE_RATE, ABM, id)`, `SRI_ARR(OPTC_INPUT_GLOBAL_CONTROL, ODM, inst)`, `SRI_ARR(OTG_H_TOTAL, OTG, inst)`, `SRI_ARR(DC_HPD_INT_STATUS, HPD, id)`, and `SRI_ARR(DP_LINK_CNTL, DP, id)`.
3. Each expansion computes `BASE(reg..._BASE_IDX) + reg...`, where `BASE()` indexes `ctx->dcn_reg_offsets[]`.
4. The computed addresses are stored in per-object register tables for ABM, OPP, timing generators, link encoders, stream encoders, HPD, and DMUB support.
5. Later hardware code uses the populated tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, polling, IRQ ack, and DMUB register-helper paths.

Observed direct include sites in this tree are `display/dmub/src/dmub_dcn36.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dc/resource/dcn36/dcn36_resource.c`. `dmub_dcn36.c` initializes DMUB register offsets through `REG_OFFSET_EXP(reg_name)`. `irq_service_dcn36.c` builds IRQ enable/ack/status addresses for HPD and OTG interrupts through `SRI(...)`. `dcn36_resource.c` builds the broader DC resource register tables during `dcn36_resource_construct()`.

## State And Persistence Behavior

The macros themselves are compile-time constants and store no software state. The state they describe is MMIO-backed display hardware state:

- ABM state includes programmed backlight levels, PWM duty-cycle limits, ambient-light/user inputs, adaptive brightness controls, luma statistics, histogram results, and register-lock/master-lock state.
- OPP/DPG/FMT/OPPBUF/CRC state includes formatter clamp and 4:2:2 configuration, output buffer state, pattern/DPG controls, and output-pipe CRC capture/results.
- ODM/OTG state includes active timing totals, sync and blank windows, vertical interrupt positions, master-update locks, global sync, CRC windowing, dynamic refresh control, DSC start positioning, underflow thresholds, and timing-generator status.
- HPD state includes hotplug sense/status, interrupt controls, and debounce/toggle filtering.
- DP/DIG state includes link training, stream timing and MSA values, scrambling/CRC/status, MST secondary packet controls, HDMI and DP packet generation, audio clock regeneration, TMDS controls, and stream encoder CRC/test-pattern state.
- Perfmon symbols describe DC performance counter state for OPP/OPTC blocks.

Persistence is hardware-defined. Configuration registers generally retain values until rewritten by modeset, link reconfiguration, power gating, suspend/resume restore, or ASIC reset. Status, interrupt, clear/ack, CRC, perfmon, lock, and counter registers may be sticky, read-only, self-clearing, write-one-to-clear, or sampling-sensitive. This offset header does not encode those access semantics; the companion shift/mask header and consuming display code provide field-level meaning and access ordering.

## Dependencies And Integration Points

This chunk depends on consistency across the generated DCN 3.6 register database:

- `dcn_3_6_0_sh_mask.h` must define matching field masks/shifts for the registers named here.
- `ctx->dcn_reg_offsets[]` must provide correct base addresses for the `_BASE_IDX` segment values. This chunk uses base index `3` for OPP/ABM/OPTC-side blocks and base index `2` for DIO/DP/DIG/HPD-side blocks.
- `display/dc/resource/dcn36/dcn36_resource.c` defines the resource-layer macros that turn these symbols into concrete register tables. Relevant initializers include `abm_regs_init()`, `opp_regs_init()`, `optc_regs_init()`, `hpd_regs_init()`, `link_regs_init()`, and `stream_enc_regs_init()`.
- `display/dc/irq/dcn36/irq_service_dcn36.c` consumes HPD and OTG offsets when constructing IRQ source information for HPD, HPD RX, vblank, vupdate, and vline interrupts.
- `display/dmub/src/dmub_dcn36.c` uses the same offset/base-index contract to initialize DMUB-side register definitions for firmware-assisted operations.
- Common hardware modules under `display/dc/dce`, `display/dc/dcn35`, `display/dc/dio`, `display/dc/optc`, and `display/dc/opp` consume the resulting register tables rather than this generated chunk directly.

The chunk also depends on structural instance alignment. DCN 3.6 resource capabilities in `dcn36_resource.c` expose four timing generators/OPPs and five DIG/link encoders. This range covers complete OPP/OTG instances 0-3, HPD instances 0-4, complete DP/DIG instances 0-1, and the beginning of DP instance 2; adjacent chunks are required for the remaining DIO/link register namespace.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These are untyped preprocessor constants, so a wrong `reg...` value or `_BASE_IDX` can compile while directing reads/writes to the wrong MMIO segment or register.
- The range has artificial boundaries. It begins with the lone `ABM1` master-lock `_BASE_IDX` and ends at `DP2_DP_DPHY_FAST_TRAINING_BASE_IDX`; a file-level report must merge neighboring chunks before making complete claims about ABM1 or DP2.
- Repeated-instance families are copy-sensitive. OPP, ODM, OTG, HPD, DP, and DIG blocks are structurally similar, but one bad offset can affect only a specific pipe, connector, timing generator, or link encoder and escape broad testing.
- ABM and backlight registers affect visible brightness and panel power behavior. Bad offsets can cause wrong brightness levels, ineffective adaptive brightness, flicker, or lock/update sequencing failures.
- OTG/ODM mistakes can cause severe display symptoms: bad timings, failed vblank/vupdate interrupts, underflows, broken dynamic refresh, incorrect DSC start position, CRC readback failures, or update-lock deadlocks.
- HPD and DIO mistakes can break connector detection, short-pulse handling, EDID/DPCD flows through the link stack, link training, MST payloads, HDMI packet generation, audio, or suspend/resume hotplug recovery.
- Status, clear, lock, CRC, and perfmon registers are side-effect-sensitive. Accessing the wrong address may clear an event, sample stale state, or leave interrupts asserted.
- The header gives no read/write permissions. Consumers must know from hardware specs and field masks which registers are read-only, write-only, write-one-to-clear, double-buffered, or power/clock-gated.

## Test Signals

Useful validation signals include:

- Build AMDGPU/DC with DCN 3.6 enabled; missing or renamed symbols should fail in `dcn36_resource.c`, `irq_service_dcn36.c`, or `dmub_dcn36.c`.
- Mechanically verify that each non-`_BASE_IDX` `reg...` macro in this range has a matching `_BASE_IDX`, accounting for the known initial `ABM1` tail line, and compare offsets/base indices against AMD's authoritative DCN 3.6 register database.
- Exercise four-pipe display configurations to cover OPP/ODM/OTG instances 0 through 3, including modesets, vblank/vupdate interrupts, update locks, dynamic refresh changes, CRC capture, and DSC-enabled modes.
- Validate ABM/backlight behavior on panels that support it: user brightness changes, adaptive brightness transitions, PWM duty-cycle limits, suspend/resume restore, and register-lock behavior.
- Test connector paths for HPD0 through HPD4, including plug/unplug, short-pulse handling, debounce/toggle filtering, resume, and IRQ ack behavior.
- Exercise DP and HDMI links on DIG/DP instances covered by this chunk: link training, lane/rate changes, MST, MSA programming, secondary packets, HDMI generic/infoframe/audio/ACR packets, TMDS output, stream CRC, and ALPM where supported.
- Watch kernel logs and display diagnostics for hotplug storms, stuck IRQs, AUX/link-training timeouts, blank displays, underflow, CRC mismatch, audio dropouts, incorrect brightness, and resume regressions.

## Cross-Chunk Notes

Earlier chunks own the start of the ABM register sequence, including most of `ABM1`. Later chunks continue `DP2` and the remaining DIO/link/output register namespace. The final per-file research document should reconcile this chunk with adjacent chunks before summarizing the complete `dcn_3_6_0_offset.h` hardware map.
