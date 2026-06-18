# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 5324-7968

Chunk: `subset-b-001577`
Covered source range: lines 5324-7968 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

## Purpose

This chunk is a generated AMD DCN 1.0 register offset header slice. It contains preprocessor constants for MMIO register addresses and matching base-index selectors; it is not executable driver logic. In this range every `#define` is an `mm*` address or `mm*_BASE_IDX` macro, for 2,398 macro definitions across 62 generated `addressBlock` sections.

The chunk starts at the tail of the DPP3 color-management block with `mmCM3_CM_CMOUT_CONTROL` through CM memory-power/debug registers, then covers DPP3 perfmon, MPC/MPCC composition, OPP/ABM/output formatting, OPTC/ODM/OTG timing generation, and the beginning of DIO connector-side blocks. It ends inside the DP AUX1 block at `mmDP_AUX1_AUX_LS_DATA_BASE_IDX`; DP AUX1 DPHY/GTC registers and AUX2+ are in the next chunk.

Major hardware surfaces in this range are:

- DPP3 color management and `DC_PERFMON15`.
- Four MPCC instances plus MPC global config, output muxes, update-lock sets, and `DC_PERFMON16`.
- Two ABM instances for backlight/PWM, histogram/local statistics, ACE curves, and master-lock state.
- Six OPP/FMT/OPPBUF/OPP pipe instances, OPP top clock control, and `DC_PERFMON17`.
- Six ODM input blocks and six OTG timing generators, followed by OPTC misc and `DC_PERFMON18`.
- DIO DAC, DOUT I2C, generic I2C, scratch/power/reset/interrupt registers, six HPD blocks, `DC_PERFMON19`, and the first two DP AUX register groups.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is the generated macro namespace:

- `mm<REGISTER>` gives the register offset value used by AMDGPU/DC register helpers.
- `mm<REGISTER>_BASE_IDX` selects the SOC15 base segment to add to that offset. All macros in this chunk use base index `2`.
- Repeated instance prefixes such as `MPCC0..3`, `FMT0..5`, `OPPBUF0..5`, `ODM0..5`, `OTG0..5`, `HPD0..5`, and `DP_AUX0..1` encode physical display block instances.
- Field shifts and masks are not defined here; they live in the companion `dcn_1_0_sh_mask.h`.

Important macro families include:

- `CM3_CM_*`: DPP3 color output control, dither/random seeds, memory power, and test-debug index/data.
- `DC_PERFMON15..19_*`: performance counter control, current-value compare, counter state, and high/low counter value registers for DPP3, MPC, OPP, OPTC, and DIO.
- `MPCC0..3_MPCC_*`: MPC compositor plane selection, OPP routing, blend/control state, stereo/multiplane controls, update-lock selection, offsets, background color, stall status, and busy/idle status.
- `MPC_*`, `MPC_OUT0..3_MUX`, `ADR_*_VUPDATE_LOCK_SET*`, and `CUR*_*_VUPDATE_LOCK_SET*`: global MPC clock/reset/CRC/perf/event/mux controls and vupdate lock routing for address and cursor updates.
- `ABM0..1_*`: backlight PWM levels, sample rates, histogram/statistics controls, ACE offset/slope/threshold programming, debug/capture controls, and ABM memory power/master lock.
- `FMT0..5_*`, `OPPBUF0..5_*`, and `OPP_PIPE0..5_*`: output pixel formatting, dither/clamp/dynamic expansion, 4:2:0 memory controls, output buffer sizing/segmentation, 3D parameters, pipe clock control, and OPP pipe CRC.
- `ODM0..5_OPTC_INPUT_*`: OPTC input global control, control, clock control, and spare registers for output data merge paths.
- `OTG0..5_OTG_*`: horizontal/vertical totals, blanking and sync, startup/update/ready windows, master/global update locks, double buffering, stereo/3D, dynamic refresh, trigger/manual flow controls, static-screen detection, frame/status counters, CRC windows/results, vertical interrupts, GSL, memory power, clock control, and spare registers.
- `DAC_*`, `DOUT_I2C_*`, `GENERIC_I2C_*`, `DIO_*`, `HPD0..5_*`, and `DP_AUX0..1_*`: display I/O configuration for analog DAC, I2C engines, DIO scratch/power/reset/interrupts, hot-plug detect status/control/filtering, and DP AUX software transaction/PHY/GTC registers.

## Control Flow

This header chunk has no internal control flow. The runtime flow is created by consumers that include `dcn_1_0_offset.h` with `dcn_1_0_sh_mask.h`:

1. Resource construction code builds generation-specific register tables from macro lists such as `MPC_COMMON_REG_LIST_DCN1_0`, `TG_COMMON_REG_LIST_DCN1_0`, `OPP_REG_LIST_DCN10`, `AUX_COMMON_REG_LIST`, and ABM register-list macros.
2. The register-table macros expand `mm*` and `mm*_BASE_IDX` names into SOC15 MMIO addresses, commonly through `SR`, `SRI`, `SRII`, or related helpers.
3. Hardware objects such as MPC, OPP, OPTC, AUX, HPD, GPIO, and ABM objects use those table entries with mask/shift metadata to read, write, update, or poll registers.
4. Sequencing, locking, interrupt acknowledgement, and polling behavior live in the DC display code, not in this generated offset header.

Concrete local integration examples include:

- `display/dc/resource/dcn10/dcn10_resource.c`, which builds `mpc_regs`, `tg_regs`, `opp_regs`, and `aux_engine_regs` from the DCN 1.0 offset namespace.
- `display/dc/mpc/dcn10/dcn10_mpc.h`, where `MPC_COMMON_REG_LIST_DCN1_0` maps `MPCC*` and `MPC_OUT*` names in this chunk into the MPC compositor object.
- `display/dc/optc/dcn10/dcn10_optc.h`, where `TG_COMMON_REG_LIST_DCN1_0` maps OTG timing, CRC, update-lock, GSL, and test-pattern registers.
- `display/dc/opp/dcn10/dcn10_opp.h`, where `OPP_REG_LIST_DCN10` maps FMT, OPPBUF, and OPP pipe registers.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and `display/dc/resource/dcn10/dcn10_resource.c`, which use DP AUX and HPD register-list macros for link encoder/AUX resources.
- `display/dc/irq/dcn10/irq_service_dcn10.c` and `display/dc/gpio/dcn10/hw_translate_dcn10.c`, which include this header for IRQ source handling and GPIO register-address translation.

## State And Persistence Behavior

The header itself is stateless. It allocates no memory, performs no I/O, takes no locks, and persists nothing outside the compiled constants.

The hardware registers addressed by these macros do represent persistent GPU display state until later programming, block reset, power-gating transition, suspend/resume restore, firmware intervention, or full GPU reset. State represented by this chunk includes:

- MPC/MPCC blending topology, output routing, background color, update-lock routing, compositor busy/idle status, and MPC CRC/perfmon state.
- ABM backlight/PWM state, histogram/local-statistics sampling, ACE curve programming, and ABM memory-power/master-lock state.
- OPP formatter state, output buffer segmentation, pipe clocks, pipe CRC capture, and OPP top clock state.
- ODM input routing and OTG timing-generator state, including mode timings, vstartup/vupdate/vready windows, update locks, DRR limits, stereo/3D controls, CRC windows/results, vertical interrupts, GSL synchronization, clock gating, and memory-power state.
- DIO state for DAC/I2C/AUX/HPD engines, hot-plug sense and interrupt latches, DIO scratch registers, soft resets, memory power, and generic interrupt messages.
- Perfmon counter configuration and values across multiple display blocks.

Access type is not encoded. Some addressed registers are control registers, some are status/readback registers, and some status or interrupt bits are acknowledged through companion fields in the mask header. Callers must rely on the block implementation and hardware spec for ordering, double-buffering, write-one-to-clear behavior, and safe polling.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor and AMD's generated ASIC register database. Practical dependencies include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h` for matching field shifts and masks.
- SOC15 base-address helpers and generation base tables such as `soc15_hw_ip.h` and `vega10_ip_offset.h`, which resolve `*_BASE_IDX` into an MMIO base.
- AMD DC register-helper macros and hardware-object register tables in the display core.

This chunk is integrated with DCN10 resource construction and hardware programming for:

- MPC/MPCC composition and output muxing.
- OPP/FMT output formatting, dither/clamp/4:2:0 handling, OPPBUF, and OPP pipe CRC.
- OPTC/OTG timing, vblank/vline/vupdate interrupts, CRC, dynamic refresh, update locks, stereo, and GSL.
- AUX/HPD/link-encoder and GPIO paths used for connector detection, DPCD/EDID access, and DP link training.
- ABM/backlight and adaptive brightness logic via shared DCE/DC ABM helpers.
- DC perfmon diagnostics for DPP, MPC, OPP, OPTC, and DIO blocks.

The file path is under a local `ceph-client` source mirror, but this chunk is AMDGPU display hardware metadata and has no Ceph filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These are untyped preprocessor constants; a wrong offset, base index, or instance prefix can compile cleanly while reads and writes target the wrong MMIO register.

Repeated instance blocks are a major review hazard. OTG0-5, FMT0-5, OPPBUF0-5, HPD0-5, and related blocks are nearly identical but have different offsets. A copy or generator error can affect only one display pipe or connector, so single-pipe testing may not catch it.

Chunk boundaries are incomplete. The first lines continue DPP3 CM definitions that began in the previous chunk, and this range ends in the middle of DP AUX1. The final per-file reconciliation should merge these with adjacent chunks before describing the full file.

Several addressed blocks are timing-sensitive or externally visible:

- OTG timing, double-buffer, DRR, GSL, and vertical interrupt registers can cause blank output, flicker, missed vblank, or bad multi-display synchronization when misprogrammed.
- MPCC and MPC mux registers define compositor topology; stale or wrong addresses can route planes to the wrong OPP or leave blend state busy.
- OPP formatter and output buffer registers affect color depth, dithering, 4:2:0 handling, segmentation, CRC, and final scanout formatting.
- HPD and AUX registers affect connector detection, interrupt storms/loss, DP AUX transactions, DPCD/EDID reads, MST sideband traffic, and link training.
- ABM/PWM registers can produce incorrect panel brightness or unstable adaptive-backlight transitions.
- Perfmon and CRC registers are often used for diagnostics; bad offsets may hide real hardware problems by reading plausible values from a different block.

All macros in this chunk use base index `2`. Later DCN generations have similar register names with different offsets and sometimes different base indexes, so cross-generation reuse must go through the intended generation-specific register-list macros rather than hard-coded addresses.

## Test Signals

Useful validation signals include:

- Build coverage for DCN10 users that include `dcn_1_0_offset.h`, especially `dcn10_resource.c`, `irq_service_dcn10.c`, `hw_translate_dcn10.c`, `hw_factory_dcn10.c`, MPC, OPTC, OPP, ABM, and link-encoder translation units.
- Generated-header consistency checks that every `mm<REGISTER>` has a matching `mm<REGISTER>_BASE_IDX`, and that consumed registers have corresponding field definitions in `dcn_1_0_sh_mask.h`.
- MMIO table validation that `SR`/`SRI`/`SRII` expansion resolves expected SOC15 base plus offset values for MPC, OPP, OTG, HPD, and AUX instances.
- Multi-pipe display tests across all available OTGs/OPPs/MPCCs, covering modeset, vblank/vline/vupdate IRQs, page flips, update locks, DRR, stereo/GSL where supported, CRC readback, and suspend/resume restore.
- Plane composition tests that exercise MPCC selection, OPP routing, background color, alpha/blend modes, and busy/idle polling.
- Output formatting tests for bit depth, dithering, clamp, dynamic expansion, 4:2:0 paths, OPPBUF segmentation, and OPP pipe CRC.
- Hot-plug and AUX tests across every connector: HPD connect/disconnect, delayed sense, RX IRQ, debounce/filter programming, EDID/DPCD reads, DP link training, AUX timeout/error handling, and MST sideband traffic.
- ABM/backlight tests for user level, target/current level readback, PWM update sample rate, histogram/ACE programming, master-lock handling, and panel suspend/resume.
- Perfmon tests that program event selection, start/stop counters, read high/low values, and verify interrupts or compare values without disturbing adjacent display block registers.

## Cross-Chunk Notes

Earlier chunks own the beginning of `dcn_1_0_offset.h`, including the full DPP0-3 and DPP3 CM context leading into the first lines here. Later chunks complete DP AUX1, AUX2+, DIG/link encoder, DP PHY, audio, clock-source, and remaining DCN 1.0 offset definitions. The merge lane should present the full source file as generated DCN 1.0 MMIO address metadata paired with `dcn_1_0_sh_mask.h`, not as algorithmic driver code.
