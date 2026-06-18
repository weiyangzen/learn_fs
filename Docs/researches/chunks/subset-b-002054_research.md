# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 10410-13005

## Purpose

This chunk is a generated AMD DCN 3.5.0 register-offset header slice. It has no executable C logic; it exports preprocessor constants that name MMIO register offsets and the base-index selector used to resolve those offsets through `ctx->dcn_reg_offsets[]` in AMDGPU display code. The companion `dcn_3_5_0_sh_mask.h` supplies field shifts and masks for the same symbolic register names.

The requested range contains 2,376 `#define` lines, mostly one offset macro plus one `_BASE_IDX` macro per register. The slice begins at an artificial chunk boundary with the final `_BASE_IDX` for a prior DCIO UNIPHY register, then covers display panel power sequencing, DSC/DSCC instances, writeback, DCHVM, HPO DisplayPort stream/link encoder blocks, MPCC pipe-composition registers, MPCC output-gamma/remap registers, and the first MPC config registers. Of the `_BASE_IDX` values in this range, 773 point at base index `2` and 415 point at base index `3`, reflecting two DCN address spaces used by the generated register helpers.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or runtime APIs in this chunk. The exported interface is the generated register namespace:

- `reg<REGISTER_OR_BLOCKED_REGISTER>`: numeric register offset.
- `reg<REGISTER_OR_BLOCKED_REGISTER>_BASE_IDX`: index into the per-ASIC DCN base-address array.
- `ix...`: no `ix` indexed-register constants are introduced by this chunk; this range is all `reg...` macros after the carry-over DCIO line.

The major register families are:

- Boundary carry-over: `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57_BASE_IDX` is the last macro from the preceding DCIO/UNIPHY block and should be reconciled with the previous chunk before making whole-block conclusions.
- Panel power sequencing: `PWRSEQ0` and `PWRSEQ1` expose GPIO enables/control/masks, panel power-sequence control/state/delay/reference-divider registers, backlight PWM control/period/lock registers, and spare registers.
- DSC/DSCC compression: four DSC instances (`DSC_TOP0-3`, `DSCCIF0-3`, `DSCC0-3`) expose top-level control/debug, CIF config, DSCC config/status/interrupt status, PPS config registers `0-22`, memory power control, squared-error counters, max absolute error counters, rate-buffer fullness counters, rate-control fullness counters, and test/debug-bus rotation registers.
- DSC perfmon: `DC_PERFMON19-22` provide counter control, state, monitor control, current-value, high, and low registers for DSC-related performance monitoring.
- Writeback: `DWB` top registers cover clock enable, memory power, soft reset, overflow status/counter, CRC control/masks/values, output control, and host-read controls. `DWBCP` covers HDR multiplier, gamut remap A/B coefficient groups, MMHUBBUB backpressure controls, output gamma LUT access/control, two OGAM RAM banks, per-channel start/end/slope/base/offset programming, and RAM region descriptors.
- DCHVM: `DCHVM_CTRL0`, clock/memory controls, RIOMMU control, and RIOMMU status describe the display client HVM/RIOMMU register surface in this slice.
- HPO DisplayPort stream encoder instances `0-3`: each instance has stream encoder clock/control/status/spare registers, APG control/status/memory/payload/video/MPEG info registers, DME control/status/memory registers, VPG generic packet access/config/status/video/audio/MPEG info registers, and DP SYM32 encoder control/status/link-training/test/debug/CRC/spare registers.
- HPO DP link/DPHY: link encoder `0-1` clock/control/spare macros and DPHY SYM32 control/status/test/debug/CRC/count macros are present for PHY-side high-performance DP paths. Instances `2-3` in this chunk include stream/APG/DME/VPG/SYM32 macros but no matching link-encoder/DPHY blocks before the chunk moves into MPC.
- MPC/MPCC: `MPCC0-3` expose top/bottom mux selection, control/control2, status/idle/status-size, ALPHA/GLOBAL/GLOBAL_ALPHA values, and debug-index/data registers.
- MPCC OGAM and gamut remap: `MPCC_OGAM0-3` expose output gamma control, LUT index/data/control, two OGAM RAM banks (`RAMA`, `RAMB`) with B/G/R start, slope, base, end, offset, and region descriptors, plus gamut-remap coefficient format/mode and A/B coefficient matrix registers.
- MPC config start: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, and `MPC_CRC_CTRL` start the global MPC config block; the rest of this address block continues in later chunks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated metadata:

1. DCN35 initialization code includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros token-paste names such as `regDSCC0_DSCC_CONFIG0`, `regDP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL`, or `regMPCC0_MPCC_CONTROL` into offset-table initializers.
3. Helper macros add the selected base address: for example, DCN35 resource code uses `SR`, `SRI`, `SRI_ARR`, and related macros shaped as `BASE(reg..._BASE_IDX) + reg...`.
4. Hardware block constructors store the computed addresses in typed register tables for DSC, HPO DP stream encoders, HPO DP link encoders, writeback, MMHUBBUB/MCIF writeback, MPC/MPCC, DCCG, power control, and related DCN35 components.
5. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, IRQ helpers, and block-specific programming functions. Those helpers use the computed offsets from this header and the field definitions from the shift/mask header.

The macros do not encode sequencing. Consumers still have to order panel power-up/down, backlight PWM changes, DSC setup/PPS programming, writeback enable/disable, HPO DP training and packet programming, MPCC mux/blend updates, OGAM LUT updates, gamut-remap updates, CRC collection, soft resets, and clock/power transitions correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes hardware state in DCN 3.5.0 registers:

- Panel and backlight state in PWRSEQ instances: GPIO routing, panel sequencing delays, state observation, reference dividers, PWM period/control, and register lock behavior.
- DSC compression state: top/control flags, CIF config, DSCC config/status, PPS programming, memory power, rate-buffer counters, error counters, and test/debug state for four DSC engines.
- Performance counter state for DSC and writeback perfmon blocks.
- Writeback state: DWB enable/clock/reset state, overflow counters, CRC collection, output control, host-read state, color/HDR/gamut-remap coefficients, OGAM LUT RAM contents, and MMHUBBUB backpressure controls.
- DCHVM/RIOMMU state: clock/memory controls and RIOMMU control/status bits relevant to display memory virtualization.
- HPO DP state: stream/link clocking, stream encoder status, APG/VPG packet state, DME memory/control state, SYM32 link-training/test/debug/CRC state, and DPHY control/status.
- MPC/MPCC state: pipe mux topology, composition controls, alpha/global-alpha values, idle/status signals, per-MPCC OGAM LUTs, and gamut-remap matrices.
- Global MPC state beginning with clock control, soft reset, and CRC control.

Persistence is hardware-defined. Configuration values generally remain until a modeset, plane update, link retrain, writeback reconfiguration, power-gate cycle, suspend/resume, driver reset, or ASIC reset. Status, perf counter, CRC, overflow, interrupt/status, and debug registers may be read-only, sticky, self-clearing, write-one-to-clear, or only valid while their block clocks and power domains are enabled. This offset header does not describe those access semantics.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DCN 3.5.0 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`, which defines the field shifts and masks for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes both DCN35 generated headers and builds register tables with token-pasted offset macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, where `REG_OFFSET_EXP(reg_name)` resolves generated offsets through `BASE(reg..._BASE_IDX) + reg...` for DMUB-facing register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which uses the same generated offset/shift/mask model for DCN35 IRQ register tables, even though this particular chunk is mostly display block programming rather than the main HPD/vblank IRQ register set.
- Hardware object headers included by `dcn35_resource.c`: DSC register-list macros, `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST_RI`, `DCN3_1_HPO_DP_LINK_ENC_REG_LIST_RI`, `DWBC_COMMON_REG_LIST_DCN30_RI`, `MCIF_WB_COMMON_REG_LIST_DCN3_5_RI`, `MPC_REG_LIST_DCN3_2_RI`, and their shift/mask list counterparts.

The direct code integration visible in `dcn35_resource.c` maps this chunk into:

- `dsc_regs[4]`, `dsc_shift`, and `dsc_mask` for DSC engines.
- `hpo_dp_stream_enc_regs[4]`, `hpo_dp_se_shift`, and `hpo_dp_se_mask` for HPO DP stream encoders.
- `hpo_dp_link_enc_regs[2]`, `hpo_dp_le_shift`, and `hpo_dp_le_mask` for HPO DP link encoders.
- `dwbc35_regs[1]`, `dwbc35_shift`, and `dwbc35_mask` for display writeback.
- `mcif_wb35_regs[1]`, `mcif_wb35_shift`, and `mcif_wb35_mask` for MCIF/MMHUBBUB writeback integration.
- `mpc_regs`, `mpc_shift`, and `mpc_mask` for MPCC/MPC composition, mux, CRC, OGAM, and gamut-remap programming.

One notable local integration detail is that `dcn35_resource.c` defines `DSCC0_DSCC_CONFIG0__ICH_RESET_AT_END_OF_LINE__SHIFT` and `_MASK` immediately after including the generated DCN35 headers. That suggests the generated shift/mask header or shared DSC macro list needed a local compatibility patch for this DSC field, while the offset macro `regDSCC0_DSCC_CONFIG0` still comes from this offset header.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong offset or `_BASE_IDX` can compile cleanly and route a register access to the wrong block, wrong instance, or wrong address space.
- This is generated metadata. Manual edits can diverge from AMD's authoritative register database, firmware assumptions, and the matching shift/mask header.
- The chunk boundary is artificial. It starts with a dangling DCIO/UNIPHY `_BASE_IDX` from the previous block and ends after only the first three MPC config registers. Whole-block conclusions require adjacent chunks.
- Repeated instances are copy-sensitive. DSC0-3, HPO stream encoders 0-3, APG/VPG/DME instance IDs, SYM32 encoder IDs, MPCC0-3, and MPCC_OGAM0-3 use similar names but different offsets and base addresses.
- HPO DP instance coverage is asymmetric in this range: link encoder and DPHY SYM32 macros are present for the first two HPO DP link paths, while stream/SYM32 encoder macros continue for instances 2-3. Consumers must use the resource table's actual instance counts rather than infer all link-side blocks from stream-side blocks.
- DSC programming is field- and sequence-sensitive. Bad offsets can corrupt PPS programming, memory-power control, rate-buffer telemetry, or error-counter reads, causing DSC link failures, corruption, blanking, or misleading diagnostics.
- Writeback and DWBCP registers include CRC, overflow, backpressure, color, HDR, gamut, and OGAM programming. Misaddressing can produce bad captured frames, stalls, silent color conversion errors, or hard-to-debug overflow behavior.
- MPCC and MPC registers control display pipe composition. Wrong mux, alpha, OGAM, or gamut-remap offsets can swap pipes, break blending, produce color errors, or disturb atomic updates.
- Panel power/backlight PWRSEQ registers are user-visible and potentially timing-sensitive. Incorrect offsets may leave eDP panels dark, flicker during enable/disable, or mishandle backlight PWM register locking.
- Status/debug/perf registers may have side effects or validity constraints not represented here. Test/debug, CRC, perfmon, overflow, and status reads should be treated according to the programming guide and block power state.

## Test Signals

Useful validation combines generated-header consistency with DCN35 hardware behavior:

- Build AMDGPU with DCN35 display support enabled. Missing or renamed macros should fail in `dcn35_resource.c`, `dmub_dcn35.c`, IRQ service compilation, or hardware object register-list expansion.
- Mechanically compare this range against the matching `dcn_3_5_0_sh_mask.h` and AMD's generated register database, checking that every consumed offset macro has a matching base-index macro and that consumers do not request registers absent from this slice or adjacent chunks.
- Diff equivalent blocks against nearby generated variants such as `dcn_3_5_1_offset.h`, `dcn_3_6_0_offset.h`, and `dcn_4_2_0_offset.h` to catch accidental instance swaps or unexpected base-index changes.
- Exercise eDP panel power and backlight transitions on DCN35 hardware: cold boot, modeset, DPMS off/on, suspend/resume, brightness changes, and panel power sequencing.
- Validate DSC on supported links with multiple bpc/format/refresh modes, MST where applicable, hotplug/retrain cycles, suspend/resume, and error-counter/perfmon reads.
- Exercise HPO DP stream/link paths: high-bandwidth DP modes, link training, test-pattern generation, APG/VPG info packets, MPEG/audio/video packet updates, CRC/debug status reads, and link retraining after hotplug.
- Exercise writeback paths: enable/disable DWB, capture frames, stress MMHUBBUB backpressure, monitor overflow counters, validate CRC values, and verify HDR/gamut/OGAM effects in captured output.
- Exercise MPCC/MPC composition paths: multi-plane blending, alpha and global-alpha changes, plane reordering, pipe split/merge, color-management changes, OGAM LUT programming, gamut remap, and MPC CRC reads.
- Watch kernel logs and display diagnostics for register timeout messages, blank displays, missed page flips, link training failures, writeback overflows, DSC corruption, color mismatches, stuck soft resets, and resume-only failures.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_0_offset.h`. Earlier chunks contain the file prologue and many preceding DCN35 blocks; the first line here belongs to a preceding DCIO/UNIPHY block. Later chunks continue the MPC config block and the rest of the generated DCN35 register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN35 register offsets, all HPO DP link paths, or the full MPC/MPC config register surface.
