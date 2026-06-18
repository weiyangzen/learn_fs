# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 51065-53412

## Scope

This chunk covers generated DCN 3.5.0 ASIC register shift/mask macros from `dcn_3_5_0_sh_mask.h`, lines 51065-53412. It contains no C functions or runtime control flow; its role is to provide compile-time bitfield metadata for AMD display driver register access helpers.

The slice contains 2,217 `#define` entries: 1,109 `__SHIFT` constants and 1,108 `_MASK` constants. The one-entry imbalance is because this range starts in the middle of the `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` field group, so its shift definitions are in an earlier chunk.

## Purpose

The header maps named hardware fields to bit positions and bit masks for DCN 3.5.0 display blocks. Driver code does not normally manipulate these long macro names directly. Instead, block headers use `SF(...)`, `SRI(...)`, `SRI_ARR(...)`, and related macros to build register/field tables, and runtime code then uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_WRITE` against those tables.

Major hardware areas represented in this chunk:

- MPCC/MCM color memory and 1D LUT RAM region fields, including `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` through `REGION_32_33` and `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL`.
- OPP/OTG timing, CRC, DRR, long-vblank, and DLPC snapshot/stop-control fields for OTG instances 0-3.
- DP and DIG encoder fields for DP/DIG instances 0-4: DP MSA transmission enable, MST secondary allocation table encryption fields, ALPM scrambled-zero controls, stream/link symbol counters, DIG front-end/back-end clocks and resets, FIFO level, Dolby Vision and TMDS HDMI control fields.
- DIO, DPIA mux, I2C/DDC setup, stream mapper, UNIPHY channel crossbar, DC GPIO drive, PWRSEQ, DSCC, DSC top, and HDMI FRL/stream/TB encoder fields.
- DP 32-bit symbol encoder and DP DPHY symbol fields for DP link encryption and symbol counters.
- DLPC, DPIA MU, DPIA port clocks/resets/TPI status/interrupt/perf-counter fields.
- Azalia/AFMT ACP/audio-packet metadata fields and endpoint clock-gating controls.

## Important APIs, Types, And Macros

This chunk defines macro constants only. The meaningful API contract is the naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit index for `FIELD`.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask in the 32-bit register value.
- Repeated indexed blocks use a hardware-instance prefix, such as `OTG0_`, `DP3_`, `DIG4_`, `DSCC2_`, `DP_DPHY_SYM321_`, or `DPIA_PORT3`.
- Shared logical fields keep consistent suffix names across instances, which lets block headers refer to a common field name while selecting instance-specific registers.

Representative field groups:

- `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL__MPCC_MCM_*`: power force/disable/low-power/state fields for shaper, 3DLUT, and 1DLUT memories.
- `OTGx_OTG_V_COUNT_STOP_CONTROL*`, `OTGx_OTG_DLPC_CONTROL`, and `OTGx_OTG_CRC*_WINDOW*READBACK`: timing-generator stop counters, DLPC snapshots, long-vblank status, and CRC window readbacks.
- `DPx_DP_MSE_SAT*` and `DPx_DP_MSE_SAT*_STATUS`: MST encryption enable/type fields for virtual channels 0-5 and their status mirrors.
- `DPx_DP_STREAM_SYMBOL_COUNT_*` and `DPx_DP_LINK_SYMBOL_COUNT_*`: stream BS, link SR, and cycle counter enable/reset/status fields.
- `DIGx_DIG_FE_CLK_CNTL`, `DIGx_DIG_BE_CLK_CNTL`, `DIGx_DIG_FE_EN_CNTL`, and `DIGx_DIG_BE_EN_CNTL`: front-end/back-end mode, clock enable, reset, and gated-clock status fields.
- `DIO_CLK_CNTL`: display IO clock enables and clock-on status for DPIA, USB-C, DPREF, PHY reference, and RX/TMDS paths.
- `HDMI_FRL_ENC_*`, `HDMI_STREAM_ENC_*`, and `HDMI_TB_ENC_*`: HDMI FRL lane/training/jitter/memory controls, stream encoder clock/FIFO controls, and TMDS/FRL packet-generation controls.
- `DPIA_MU_*`: DPIA microcontroller clock gates, per-port reset completion, TPI credit status, interrupts, microsecond reference, port hidden status, glue IO enable, and performance counter controls.
- `AZALIA_*` and `AZF0ENDPOINT*`: ACP packet data/index metadata and endpoint fine-grain clock-gating repeat disable fields.

## Control Flow

There is no executable control flow in this chunk. Control flow appears in consumers that include this header:

- `display/dc/resource/dcn35/dcn35_resource.c` includes this header while defining DCN 3.5 resource register tables.
- `display/dc/irq/dcn35/irq_service_dcn35.c` includes it for interrupt source/status/ack bit definitions.
- `display/dmub/src/dmub_dcn35.c` includes it for DMUB-facing DCN 3.5 register programming.

Within display block code, these macros are consumed indirectly. For example, `dcn35_optc.h` maps `OTG0_OTG_V_COUNT_STOP_CONTROL` / `OTG_V_COUNT_STOP` through `SF(...)`, and `dcn35_optc.c` writes `OTG_V_COUNT_STOP_CONTROL` and `OTG_V_COUNT_STOP_CONTROL2` while programming vertical count stop behavior. The field widths here therefore bound the values that those runtime helpers can encode into MMIO writes.

## State And Persistence Behavior

This header stores no runtime state. It describes hardware-backed state that persists in registers until reset, power transition, driver reprogramming, or hardware self-clear semantics. Important state surfaces in this chunk include:

- MPCC MCM memory power state and force/disable controls.
- OTG stop-count, long-vblank, CRC readback, and DLPC snapshot/status fields.
- DP MST encryption enable/type status, ALPM status, and stream/link counter status.
- HDMI FRL jitter exceed and meter-buffer overflow status, HDMI stream FIFO calibration/status/error fields, and HDMI TB packet/error/CRC fields.
- DSCC end-of-frame interrupt status and enable fields.
- DPIA MU reset-done, timeout interrupt, TPI credit, port-hidden, and performance-counter state.
- Azalia/ACP endpoint packet configuration and endpoint clock-gating controls.

Persistence risk is indirect: incorrect mask/shift values make higher-level register helpers preserve, clear, or overwrite the wrong bits. That can produce long-lived hardware misconfiguration until the affected block is reset or reinitialized.

## Dependencies And Integration Points

Primary dependency direction is from generated register headers into DC display code:

- `dcn_3_5_0_sh_mask.h` is paired with DCN 3.5.0 register-address headers in `include/asic_reg/dcn/`.
- Display resource and block headers include both address and mask/shift metadata to instantiate per-generation register tables.
- Runtime display code relies on AMD's register helper macros to combine register addresses, masks, and shifts.
- Adjacent generation headers such as `dcn_3_5_1_sh_mask.h`, `dcn_3_6_0_sh_mask.h`, and `dcn_4_2_0_sh_mask.h` carry similarly named fields; cross-generation copy mistakes are plausible when fields move or widths change.

Notable integration points visible from repository search:

- `display/dc/mpc/dcn32/dcn32_mpc.c` uses logical `MPCC_MCM_MEM_PWR_CTRL` fields via register helpers for LUT memory power sequencing and waits on power-state fields.
- `display/dc/optc/dcn35/dcn35_optc.c` writes OTG count-stop controls that are represented by this chunk's `OTGx_OTG_V_COUNT_STOP_CONTROL*` fields.
- `display/dc/resource/dcn35/dcn35_resource.h` maps OTG register arrays with `SRI_ARR(...)`, tying the per-instance masks here to DCN 3.5 resource construction.

## Risks

- Generated macro drift: a wrong bit position or mask compiles cleanly but silently corrupts MMIO programming.
- Partial-field overlap: many fields are tightly packed into 32-bit registers; an incorrect mask can affect adjacent enable/status bits.
- Instance skew: repeated OTG/DP/DIG/DPIA families must remain consistent for all instances unless the hardware truly differs. A single bad instance macro can create port-specific failures.
- Status/control ambiguity: several registers contain both control and status or clear bits, such as reset-done, overflow, interrupt ack/status, and packet-error clear fields. Misusing masks can accidentally clear latched hardware state.
- Range-bound values: fields such as OTG vcount stop, HDMI packet line references, FIFO levels, DPIA counts, and jitter thresholds have fixed widths. Callers must clamp or validate values before using register helpers.
- Chunk boundary risk: this range starts mid-`MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` group and ends mid-`AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`; the merge lane must combine adjacent chunks before treating either group as complete.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display behavior based:

- Build coverage for DCN 3.5 display code that includes `dcn_3_5_0_sh_mask.h`, especially `dcn35_resource.c`, `irq_service_dcn35.c`, and `dmub_dcn35.c`.
- Macro table consistency checks comparing `_MASK`/`__SHIFT` pairs for same field names and verifying masks align with shifts and expected widths.
- Cross-generation diffs against `dcn_3_5_1_sh_mask.h` for fields that should remain identical between DCN 3.5 variants.
- Display bring-up tests covering DP/HDMI link enable, MST encryption, ALPM, Dolby Vision/TMDS mode programming, HDMI FRL training, DSC/DSCC paths, and DPIA USB-C paths.
- Runtime register readback tests where available: OTG vcount stop/readback, CRC windows, FIFO status/calibration, DP/HDMI symbol counters, DPIA interrupt/status/perf counters, and memory power-state waits.

## Chunk Notes For Merge Lane

This is a middle chunk of a large generated header. The final per-file research should describe the whole header as a generated DCN 3.5.0 register mask/shift contract, not as isolated hand-written logic. Adjacent chunks are needed to cover the opening include guards/license/generation context, earlier MPCC register families, and the trailing `AZF0ENDPOINT3` masks plus file footer.
