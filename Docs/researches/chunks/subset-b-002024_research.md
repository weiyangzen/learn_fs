# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 7652-10192

## Scope

This chunk is a middle slice of the generated AMD DCN 3.2.1 register offset header. It contains C preprocessor constants only: no functions, structs, enums, or executable control flow are defined in these lines. The constants map display controller hardware register names to MMIO register offsets and pair nearly every offset with a `_BASE_IDX` selector used to choose a base address from `ctx->dcn_reg_offsets[]`.

The chunk starts inside the `dce_dc_opp_fmt2_dispdec` block at `regFMT2_FMT_CLAMP_COMPONENT_G` and ends inside the `dce_dc_dio_dig4_dispdec` block at `regDIG4_HDMI_ACR_44_0`. Because both boundaries are partial, the merge lane must combine adjacent chunks to recover the complete `FMT2` and `DIG4` block inventories.

## Purpose

The purpose of these lines is to provide ASIC-specific register addresses for several display pipeline areas:

- OPP/FMT/OPPBUF/DPG/DSCRM registers for output processing, format control, output buffers, pipe CRC, display pattern generation, DSC forwarding, ABM, and OPP top clock control.
- OPTC/ODM/OTG registers for timing generation, output data merger input control, global sync lock, CRC windows/results, dynamic refresh-rate control, vertical interrupts, update locks, and timing status.
- DIO HPD, DP, and DIG registers for hot-plug detection, DisplayPort link/stream programming, HDMI/AFMT metadata/audio packet controls, TMDS controls, stream encoder startup, and test/CRC features.

Downstream AMD display code includes this header from `display/dc/resource/dcn321/dcn321_resource.c` together with `dcn_3_2_1_sh_mask.h`. The resource code uses macros such as `SR`, `SRI`, and `SRI_ARR` to combine these offset constants with `ctx->dcn_reg_offsets[reg..._BASE_IDX]` and populate per-block register tables. Runtime code then accesses those tables through `REG_READ`, `REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_WAIT`, and related register helper macros.

## Register Inventory In This Chunk

This slice contains 2,393 `#define reg...` lines: 1,197 register offset constants and 1,196 `_BASE_IDX` constants. The one-count mismatch is expected for this isolated chunk because the first complete register pair in view follows a missing prior line from the same `FMT2` block.

Visible block boundaries and representative contents:

- `dce_dc_opp_oppbuf2_dispdec`, base `0x2d0`: `regOPPBUF2_OPPBUF_CONTROL`, 3D parameter registers, and `OPPBUF_CONTROL1`.
- `dce_dc_opp_opp_pipe2_dispdec`, base `0x2d0`: `regOPP_PIPE2_OPP_PIPE_CONTROL`.
- `dce_dc_opp_opp_pipe_crc2_dispdec`, base `0x2d0`: pipe CRC control, mask, and result registers.
- `dce_dc_opp_dpg3_dispdec`, base `0x438`: DPG control, ramp, dimensions, RGB/YCbCr color, offset segment, and status registers.
- `dce_dc_opp_fmt3_dispdec`, base `0x438`: FMT clamp, dynamic expansion, format control, bit-depth control, dither seed, stereo, 4:2:0 memory, and 4:2:2 control registers.
- `dce_dc_opp_oppbuf3_dispdec`, `opp_pipe3`, and `opp_pipe_crc3`, base `0x438`: OPPBUF, pipe control, and CRC registers for pipe 3.
- `dce_dc_opp_dscrm0` through `dscrm3`: one `DSCRM_DSC_FORWARD_CONFIG` register per instance.
- `dce_dc_opp_opp_top_dispdec`: `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`.
- `dce_dc_optc_odm0` through `odm3`: per-ODM input global control, source select, data format, bytes-per-pixel, width, input clock, memory config, and spare registers.
- `dce_dc_optc_otg0` through `otg3`: large repeated timing generator blocks containing horizontal/vertical timing, trigger, force-count, flow, stereo, interlace, status, snapshot, interrupt, update-lock, master-enable, CRC, static-screen, 3D, GSL, DRR, DTO, request, DSC start, pipe update, and spare registers.
- `dce_dc_optc_optc_misc_dispdec`: GSL source select, OPTC clock control, ODM memory power control/status, and misc spare register.
- `dce_dc_dio_hpd0` through `hpd4`: HPD interrupt status/control, HPD control, fast training, and toggle filter control registers.
- `dce_dc_dio_dp0` through `dp4`: repeated DisplayPort link blocks covering link control, pixel format, MSA fields, stream control, DPHY training/test/CRC, secondary-data packets, audio N/M, MST/MSE slot allocation, MSO/DSC, DB, metadata, ALPM, GSP, and AUX-less ALPM registers.
- `dce_dc_dio_dig0` through `dig3`: repeated stream encoder blocks covering DIG front-end control, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packets, AFMT, backend enable, TMDS, version, and forced disable.
- `dce_dc_dio_dig4`: begins in this chunk at base `0x1000`, but only runs through `regDIG4_HDMI_ACR_44_0`; later DIG4 HDMI ACR, AFMT, backend, and TMDS symbols are outside this chunk.

## Important APIs, Types, And Macros

The chunk itself exports register-name macros. Important naming forms are:

- `reg<block><instance>_<REGISTER>`: the register offset within the ASIC register map, for example `regOTG0_OTG_H_TOTAL`, `regDP0_DP_LINK_CNTL`, `regDIG0_DIG_FE_CNTL`, and `regHPD0_DC_HPD_INT_STATUS`.
- `reg<block><instance>_<REGISTER>_BASE_IDX`: index into `ctx->dcn_reg_offsets[]`; all constants in this chunk use base index `2`.
- Address block comments: generated metadata documenting the hardware address block and its local base address. These comments are not consumed by C code but are useful for validating instance spacing and generated output.

The consumer-side APIs are not defined here, but this chunk is designed for these integration macros in `dcn321_resource.c`:

- `BASE(reg..._BASE_IDX)` resolves the ASIC segment base using `ctx->dcn_reg_offsets`.
- `SRI(reg_name, block, id)` constructs one register address from a block instance, for example `SRI(OTG_H_TOTAL, OTG, inst)` expands toward `regOTG<inst>_OTG_H_TOTAL`.
- `SRI_ARR(reg_name, block, id)` stores per-instance addresses into register arrays.
- `REG(reg_name)` handles non-instanced addresses by adding `ctx->dcn_reg_offsets[...]` and `reg...`.

Those populated register tables are used by hardware object headers and implementations such as:

- OPP paths: `dc/opp/dcn10/dcn10_opp.h` maps `FMT_CONTROL` and `OPPBUF_CONTROL`; `dcn10_opp.c` updates format, dithering, clamping, pixel encoding, and output-buffer width fields.
- OPTC paths: `dc/optc/dcn10/dcn10_optc.h` and `dcn32_optc.h` map OTG registers; `dcn10_optc.c` writes and reads timing registers such as `OTG_H_TOTAL`.
- DIO link paths: `dc/dio/dcn30/dcn30_dio_link_encoder.h` maps `DP_LINK_CNTL`; DCE/DCN link encoder implementations update `DP_LINK_TRAINING_COMPLETE`.
- DIO stream encoder paths: `dc/dio/dcn30/dcn30_dio_stream_encoder.h` maps `DIG_FE_CNTL`; stream encoder code starts/stops DIG, selects sources, configures TMDS/HDMI encoding, and waits on symbol-clock state.
- HPD/GPIO/IRQ paths: HPD register macros feed IRQ services and GPIO HPD register tables through `DC_HPD_INT_STATUS` and related control/status registers.

## Control Flow

There is no runtime control flow in this header chunk. The effective flow is compile-time and initialization-time:

1. `dcn321_resource.c` includes this offset header and the matching shift/mask header.
2. Register-list macros in DCN resource and hardware object headers token-paste symbolic names into concrete constants from this file.
3. DCN321 resource construction populates register address structures for OPP, OPTC, DIO link encoders, stream encoders, HPD, IRQ, HW sequencer, and related blocks.
4. Runtime display paths call register helper macros against those tables. The helpers read/write MMIO registers, update bitfields defined by the shift/mask header, and may poll hardware status.

For example, an `SRI_ARR(DP_LINK_CNTL, DP, id)` use resolves to `BASE(regDP<id>_DP_LINK_CNTL_BASE_IDX) + regDP<id>_DP_LINK_CNTL`, and stream/link encoder code later manipulates the resolved address through register helper APIs.

## State And Persistence Behavior

The constants in this chunk have no in-memory mutable state and perform no persistence. Their only state-like behavior is their contribution to immutable register-address tables initialized during driver setup.

Hardware state lives outside the header in the GPU registers addressed by these constants. Writes through downstream `REG_UPDATE` or `REG_SET` calls persist in hardware until overwritten, reset, power-gated, or reinitialized. Status and result registers in this chunk, such as OTG CRC results, HPD status, DP DPHY CRC/status, DIG output CRC, and OPP pipe CRC results, expose current hardware state to the driver.

Because all visible `_BASE_IDX` values are `2`, this chunk depends on DCN321 platform setup assigning the correct MMIO segment base to `ctx->dcn_reg_offsets[2]`. A bad base-index table causes every register derived from these constants to target the wrong MMIO region even if the offsets are individually correct.

## Dependencies

Direct dependencies are preprocessor-level:

- The include guard and offset macro names from the same generated header.
- `dcn_3_2_1_sh_mask.h`, which must define matching bit shifts and masks for fields within the registers named here.
- `dcn321_resource.c` macro definitions that use `reg...` and `reg..._BASE_IDX` names.
- Resource and hardware object headers that refer to these names through `SRI`, `SRI_ARR`, `SF`, `SE_SF`, `LE_SF`, `OPP_SF`, and related macros.
- `reg_helper.h` and DC register helper infrastructure for actual MMIO access after resource construction.

External dependencies are hardware/ASIC contracts:

- The DCN 3.2.1 register map must match these offsets exactly.
- The block instance spacing implied by repeated bases must match the silicon layout: OTG instances step through offset groups from `0x1b2a` to `0x1d21`, DP instances from `0x2108` to `0x2567`, DIG instances from `0x208b` onward, and HPD instances from `0x1f14` through `0x1f38`.
- DisplayPort, HDMI, DSC, MST/MSE, ALPM, GSL, DRR, CRC, and HPD behavior depends on register semantics defined outside this header.

## Integration Points

Key integration points visible from this chunk:

- `display/dc/resource/dcn321/dcn321_resource.c`: includes this header and converts constants into typed register tables.
- `display/dc/resource/dcn32/dcn32_resource.h`: defines many of the register list macros that reference names in this chunk, including DIO, HPD, DP, OPP, and OTG lists.
- `display/dc/opp/*`: consumes FMT and OPPBUF addresses to program clamping, dither, pixel encoding, stereo, 4:2:0/4:2:2 handling, and output-buffer parameters.
- `display/dc/optc/*`: consumes OTG/ODM/GSL/DRR/CRC addresses to program timing, update locks, vertical interrupts, global sync, dynamic refresh, CRC readback, and timing status.
- `display/dc/dio/*`: consumes DP and DIG addresses for link training, stream enable/disable, TMDS/HDMI packet programming, DP secondary data, DSC/MSO/MST, audio timing, and low-power features.
- `display/dc/irq/*` and `display/dc/gpio/*`: consume HPD addresses to detect cable state and service HPD interrupts.

## Risks And Edge Cases

- **Generated-header drift:** If this offset header and the matching shift/mask header are regenerated from different hardware descriptions, code may compile but manipulate wrong fields or addresses.
- **Wrong base index:** The visible `_BASE_IDX` constants are all `2`; if `ctx->dcn_reg_offsets[2]` changes meaning or is initialized incorrectly, the entire OPP/OPTC/DIO region addressed here is wrong.
- **Partial chunk boundaries:** This report cannot claim complete coverage of the `FMT2` or `DIG4` blocks. The final merged per-file research must reconcile previous and following chunks.
- **Instance-copy errors:** Repeated OTG, DP, DIG, and HPD blocks are mechanically similar. A single offset typo in one instance can affect only that pipe/connector and may appear as a monitor-specific or pipe-specific failure.
- **Cross-generation similarity:** Nearby headers such as DCN 3.2.0, 3.1.x, 3.5.x, 3.6.0, 4.1.0, and 4.2.0 contain similar symbols with some offset differences. Copying values across generations is risky even when names match.
- **Status/result side effects:** Some downstream reads/writes to interrupt, CRC, training, snapshot, or lock registers may have clear-on-read, latch, or timing-sensitive behavior defined by hardware, not by this header.
- **Power-gating interactions:** Registers under OPP, OPTC, DIO, and ODM may be inaccessible or stale when their blocks are power-gated; callers must rely on resource/hwseq sequencing rather than the constants alone.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Compile-time success of DCN321 resource code, especially token-pasted register list macros such as `SRI_ARR(OTG_H_TOTAL, OTG, inst)`, `SRI_ARR(DP_LINK_CNTL, DP, id)`, `SRI_ARR(DIG_FE_CNTL, DIG, id)`, and `SRI_ARR(DC_HPD_INT_STATUS, HPD, id)`.
- Static comparison against generated register-map sources or adjacent known-good DCN headers to ensure instance offsets and `_BASE_IDX` values are expected for DCN 3.2.1.
- Display bring-up tests across all exposed pipes/connectors: HPD detection, mode set, blank/unblank, DP link training, HDMI output, audio packet programming, DSC/MSO/MST paths, and stream encoder start/stop.
- Timing validation through OTG status/readback and vertical interrupt behavior, including DRR, GSL, update-lock, and CRC windows where supported.
- CRC/debug paths: OPP pipe CRC, OTG CRC, DIG output CRC, and DP DPHY CRC should produce stable expected values under controlled test patterns.
- Suspend/resume and power-gating tests to catch address mistakes in memory power control, clock control, and block reinitialization paths.
- Multi-instance coverage: tests should exercise OTG0-OTG3, DP0-DP4, DIG0-DIG4, and HPD0-HPD4 rather than validating only instance 0.
