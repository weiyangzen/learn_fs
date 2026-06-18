# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 5236-7883

## Scope And Purpose

This chunk is generated AMD DCN 2.1 register-offset metadata. It contains no executable C logic; its interface is a large set of preprocessor constants that map display hardware register names to numeric MMIO offsets and to a segment/base selector via the paired `_BASE_IDX` macros.

The path is under the local `ceph-client` source mirror, but this file belongs to the Linux AMDGPU display stack. In this line range it describes display engine blocks for Renoir/DCN 2.1: the tail of DPP color-management instance 3, the DPP perf monitor for instance 3, MPC/MPCC blending and output color blocks, OPP instances 0-5, DSC remap controls, OPP performance counters, and the beginning of OPTC/ODM input controls. It is not Ceph filesystem code.

The chunk boundaries are not semantic. It starts inside the `CM3` DPP color-management register sequence, at `mmCM3_CM_DGAM_RAMA_END_CNTL2_B`, and ends inside the `ODM3` block at `mmODM3_OPTC_WIDTH_CONTROL`; surrounding chunks are needed for the complete source-file register map.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables in this chunk. The public API is the generated macro naming contract:

- `mm<block/register>` gives the DCN 2.1 register offset.
- `mm<block/register>_BASE_IDX` gives the segment index used by register-table constructors to add the correct ASIC base address.
- Repeated instance prefixes such as `CM3`, `MPCC0` through `MPCC7`, `FMT0` through `FMT5`, `DPG0` through `DPG5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, `DSCRM0` through `DSCRM5`, and `ODM0` through `ODM3` distinguish hardware instances that share a common layout.

Important macro families in this range:

- `mmCM3_CM_*`: DPP instance 3 color-management and LUT programming offsets. The visible portion covers degamma RAM A/B tail registers, blend-gamma control/LUT/RAM A/B registers, HDR multiplier, memory power control/status, dealpha, coefficient format, shaper control/LUT/RAM A/B registers, 3D LUT mode/index/data/read-write controls, 3D LUT normalization and output offsets, and test/debug index/data.
- `mmDC_PERFMON15_*`: DPP3 display performance monitor offsets for perf counter control, state, control registers, current value, high/low counter words, and interrupt/misc value.
- `mmMPCC0_MPCC_*` through `mmMPCC7_MPCC_*`: multi-plane composition controller instance offsets for top/bottom source selection, OPP assignment, blend/control state, update-lock selection, top/bottom gains, background color, memory power control, stall status, and busy/idle status.
- `mmMPC_*`, `mmMPC_OUT*_*`, and `mmMPC_OCSC_*`: global MPC controls and output-side color processing. This includes soft reset, update-lock controls, pending/ack/status registers, stall controls, output muxes, denorm and clamp controls, output CSC coefficient sets for outputs 0-3, out CSC coefficient format, OC SC mode/coefficients for outputs 0-5, LUT/PWL RAM controls, and MPC perf monitor event selection.
- `mmMPCC_OGAM*_*`: output gamma programming for MPCC instances 0-7, including per-channel LUT index/data/write masks, RAM A/B start/slope/end/region programming, memory power state, and debug controls.
- `mmABM0_*` plus `mmBL1_PWM_*`: adaptive backlight management and PWM/backlight control offsets, including ABM control, hysteresis, luminance/current/target levels, pixel-count filters, test/debug controls, PWM period/current counter, backlight gain/level, and ramp/ramp-rate controls.
- `mmFMT0_FMT_*` through `mmFMT5_FMT_*`: output formatter offsets for component clamps, dynamic expansion, format control, bit-depth/dither seeds, clamp control, side-by-side stereo, 4:2:0 map memory control, and 4:2:2 control.
- `mmDPG0_DPG_*` through `mmDPG5_DPG_*`: display pattern generator offsets for pattern/ramp control, dimensions, RGB/YCbCr color values, offset segment, and status.
- `mmOPPBUF0_OPPBUF_*` through `mmOPPBUF5_OPPBUF_*`: output pixel processor buffer offsets for active width, pixel repetition, MSO/display segmentation, 3D parameters, and secondary control.
- `mmOPP_PIPE0_OPP_PIPE_CONTROL` through `mmOPP_PIPE5_OPP_PIPE_CONTROL`: OPP pipe controls.
- `mmOPP_PIPE_CRC0_*` through `mmOPP_PIPE_CRC5_*`: OPP pipe CRC control, mask, and result registers.
- `mmOPP_TOP_CLK_CONTROL`: shared OPP top-level clock control.
- `mmDSCRM0_DSCRM_DSC_FORWARD_CONFIG` through `mmDSCRM5_DSCRM_DSC_FORWARD_CONFIG`: DSC remapper/forwarding configuration for OPP/DSC routing.
- `mmDC_PERFMON16_*`: OPP-side display performance monitor offsets.
- `mmODM0_OPTC_*` through the visible start of `mmODM3_OPTC_*`: OPTC/ODM input controls for global control, data source selection, data format, bytes per pixel, segment width, input clock, memory configuration, and spare registers.

## Control Flow

This header has no runtime control flow. It is declarative hardware metadata. Runtime behavior appears when DCN 2.1 display code builds register tables from these macros and later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, and related helpers.

Representative integration flows in this tree:

- `display/dc/resource/dcn21/dcn21_resource.c` includes `dcn_2_1_0_offset.h`, defines `BASE(mm..._BASE_IDX) + mm...` expansion helpers such as `SR`, `SRI`, `SRII`, and `SRIR`, and instantiates arrays for DPP, OPP, MPC, OPTC, audio, hub, clock, and other DCN 2.1 blocks. This chunk feeds those table initializers for DPP color-management instance 3, OPP instances 0-5, MPCC/MPC, and ODM/OPTC offsets.
- `display/dmub/src/dmub_dcn21.c` includes this offset header for the DMUB service register table; the DMUB-facing file uses generated offset and mask headers to produce common register descriptors.
- `display/dc/dpp/dcn20/dcn20_dpp.h` defines `TF_REG_LIST_DCN20*` macros that reference `CM_BLNDGAM_*`, `CM_SHAPER_*`, and `CM_3DLUT_*` through `SRI(..., CM, id)`. For `id == 3`, the `CM3` macros in this chunk resolve those DPP color-management register addresses.
- `display/dc/mpc/dcn10/dcn10_mpc.h` and the DCN20 MPC implementation consume the `MPCC*` and `MPC*` register families through indexed register arrays. Runtime MPC code reads and writes `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, status, and blend-related fields to build and tear down plane-composition trees.
- `display/dc/opp/dcn20/dcn20_opp.h` extends the DCN10 OPP register list with DPG registers. `dcn21_resource.c` instantiates `OPP_REG_LIST_DCN20(id)` for OPP instances 0-5, which maps to the `FMT`, `DPG`, `OPPBUF`, `OPP_PIPE`, and `OPP_PIPE_CRC` offsets in this chunk.
- OPTC headers such as `display/dc/optc/dcn10/dcn10_optc.h` use `SRI(OPTC_INPUT_GLOBAL_CONTROL, ODM, inst)` and related ODM macros. Runtime OPTC code reads underflow state, clears underflow, configures ODM data source selection, and manages segment/memory programming using these offsets.

Because the file only provides constants, sequencing rules are enforced by the consumers and by hardware. This header does not know when it is safe to program a LUT bank, change MPCC topology, clear underflow, read CRC results, or power-gate memories.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The represented state is MMIO-backed DCN display hardware state. Values programmed through these offsets persist in the hardware block until a later register write, modeset/reprogramming sequence, power transition, reset, or firmware/hardware action changes them.

The state represented in this chunk includes:

- DPP/CM state for instance 3: degamma, blend-gamma, shaper, and 3D LUT selection/data/RAM segments; color coefficients; HDR multiplier; memory power controls; and debug/test selectors.
- MPC/MPCC state: composition topology, selected top/bottom inputs, OPP assignment, per-plane blending/gain/background colors, update-lock affiliation, stall/status bits, output muxes, output CSC/OCSC coefficients, PWL/OGAM LUT contents, and MPC memory/perf controls.
- ABM/backlight state: ABM algorithm thresholds and levels, PWM period and current count, backlight level/gain, ramping, and test/debug state.
- OPP/output state: formatter clamps, bit depth, dither seeds, 4:2:0/4:2:2 formatting, test pattern generator dimensions/colors/status, OPP buffer segmentation and 3D timing parameters, OPP pipe controls, pipe CRC configuration/results, DSC forwarding, and OPP perf counters.
- ODM/OPTC input state: source selection for output data, input data format, bytes per pixel, ODM segment width, input clock gating/control, memory selection/configuration, spare register contents, and underflow-related global-control fields defined by the paired shift/mask header.

Some registers are configuration state, some are data windows for LUT RAMs, and some are status or side-effect controls. Names such as `*_LUT_INDEX`, `*_LUT_DATA`, `*_READ_WRITE_CONTROL`, `*_MEM_PWR_CTRL`, `*_MEM_PWR_STATUS`, `*_STATUS`, `*_STALL_STATUS`, `*_CRC_RESULT*`, `*_PERFCOUNTER_STATE`, and `OPTC_INPUT_GLOBAL_CONTROL` signal different access semantics that must be respected by callers.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- The paired `dcn_2_1_0_sh_mask.h` header supplies field masks and shifts for these register offsets.
- `renoir_ip_offset.h` supplies the IP base/segment arrays used by `BASE(mm..._BASE_IDX)`.
- DC register helpers in `reg_helper.h` and `dm_services.h` consume the final addresses through `REG_*` macros and low-level MMIO accessors.
- Resource constructors in `display/dc/resource/dcn21/dcn21_resource.c` map the generated offsets into typed register structs for DPP, OPP, MPC, OPTC, ABM, audio, DCCG, and other hardware objects.
- Runtime block implementations in `display/dc/dpp`, `display/dc/mpc`, `display/dc/opp`, and `display/dc/optc` use those register structs to implement color programming, plane composition, output formatting, CRC capture, ODM combine/bypass, underflow handling, and debug/performance flows.
- DMUB service setup in `display/dmub/src/dmub_dcn21.c` also includes the offset/mask pair for DCN 2.1 register descriptors.

The numeric offsets are a hardware ABI for DCN 2.1. They must remain synchronized with AMD's generated register database, the matching shift/mask file, and the block register-list macros that assume specific register names exist.

## Risks And Edge Cases

- Incorrect offsets or `_BASE_IDX` values compile cleanly but can send MMIO reads/writes to the wrong register, wrong instance, or wrong segment. Failures can appear as color corruption, broken gamma/LUT programming, bad plane composition, missing output, CRC mismatch, underflow, hangs during modeset, or power-management regressions.
- The chunk starts and ends inside larger repeated blocks. A review of only this chunk cannot prove full `CM3` or `ODM3` coverage; adjacent chunk results must be reconciled before final per-file conclusions.
- Repeated instance families are vulnerable to copy/paste drift. `MPCC0` through `MPCC7`, `OGAM0` through `OGAM7`, and OPP instance 0-5 blocks should keep consistent per-instance spacing and naming; a single bad instance may only fail on high pipe counts, multi-plane compositions, or specific outputs.
- LUT and RAM window registers have ordering and bank-selection requirements outside this header. Programming `*_LUT_INDEX`, `*_LUT_DATA`, write-enable masks, RAM A/B regions, or 3D LUT controls in the wrong order can corrupt visible color state even if the offsets are correct.
- Status and side-effect registers require careful access. `*_STATUS`, `*_STALL_STATUS`, `*_CRC_RESULT*`, performance counter state/value registers, underflow clear/status bits, and memory power status/control registers may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive according to hardware semantics not encoded here.
- MPC/MPCC topology registers affect live plane blending. Changing `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, update-lock selection, or output mux registers outside the intended hardware sequence can produce transient blanking, underflow, or composition glitches.
- ODM/OPTC controls are tied to stream splitting and high-bandwidth modes. Incorrect ODM data source, width, bytes-per-pixel, clock, or memory configuration may only surface on high-resolution, high-refresh, DSC, or ODM-combined modes.
- OPP formatter, OPPBUF, DPG, and pipe CRC registers have standards-visible output effects. Mistakes can affect bit depth, dithering, chroma format, stereo layout, MSO segmentation, blank/test patterns, and debug CRC validation.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and DCN 2.1 hardware behavior:

- Build AMDGPU with DC/DCN 2.1 support enabled. Missing or renamed macros should fail in `dcn21_resource.c`, DCN20 DPP/OPP/MPC/OPTC headers, DMUB DCN21 setup, or block implementation files.
- Diff this chunk against a regenerated DCN 2.1 offset header and against neighboring ASIC families to catch unintended offset/base-index drift, especially in repeated MPCC, OGAM, OPP, and ODM families.
- Boot and modeset on Renoir/DCN 2.1 hardware with one and multiple displays. Watch for blank screens, underflow logs, color corruption, failed hotplug, and suspend/resume regressions.
- Exercise DPP color paths: degamma, blend gamma, shaper LUT, 3D LUT, HDR multiplier, color transforms, and memory power transitions where supported by the driver and test stack.
- Exercise MPC/MPCC composition: single plane, multi-plane overlay, alpha blending, plane add/remove, pipe split, high pipe-count use, and transitions that rebuild MPCC trees.
- Exercise OPP/output paths: output bit-depth changes, dithering, RGB/YCbCr and 4:2:0/4:2:2 formats, test pattern generation, OPP pipe CRC capture, DSC forwarding, and MSO/segmentation where available.
- Exercise ODM/OPTC modes: high pixel-clock modes that require ODM combine/bypass transitions, DSC-enabled modes, and underflow clear/status handling.
- Check debugfs or driver diagnostics for pipe CRC stability, perf counter sanity, no unexpected underflow/stall status, correct LUT programming, and no MMIO access faults.
