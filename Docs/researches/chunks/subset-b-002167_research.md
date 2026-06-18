# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 39889-42395

## Scope And Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask header slice. It does not implement executable logic; it defines the bitfield contract used by the AMD display driver to program and inspect DCIO, GPIO, UNIPHY, panel power sequencing, and the beginning of DSCC0 Display Stream Compression compressor registers.

The chunk starts at the tail of `UNIPHYA_CHANNEL_XBAR_CNTL`, then covers repeated `UNIPHYB` through `UNIPHYG` link/channel crossbar fields, DCIO strap/debug/reset fields, a large `dcn_dcec_dcio_dcio_chip_dispdec` GPIO/AUX/DDC/HPD block, four `dcn_dcec_dcio_dcio_uniphy*_dispdec` reserved UNIPHY macro-control banks, the `dcn_dcec_pwrseq0_dispdec_pwrseq_dispdec` panel power/backlight PWM block, and the first part of `dcn_dcec_dsc0_dispdec_dscc_dispdec`.

These macros are consumed by DCN401 display code that includes `dcn/dcn_4_1_0_sh_mask.h`, notably `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/gpio/dcn401/hw_translate_dcn401.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and `display/dmub/src/dmub_dcn401.c`. The companion offset header supplies register addresses; this file supplies the per-field shift and mask constants used by register read/modify/write helpers.

## Important APIs, Types, And Functions

There are no C APIs, types, functions, or inline routines in this range. The public surface is preprocessor constants following the generated AMD naming scheme:

- `REGISTER__FIELD__SHIFT` gives the low-bit position for a field.
- `REGISTER__FIELD_MASK` gives the bit mask for the same field.
- Comment markers such as `//DC_GPIO_HPD_MASK` and `// addressBlock: ...` group fields by register and hardware address block.

The UNIPHY groups define lane/link wiring controls. `UNIPHYB_LINK_CNTL` through `UNIPHYG_LINK_CNTL` expose `UNIPHY_CHANNEL[0-3]_INVERT` bits. Matching `UNIPHY*_CHANNEL_XBAR_CNTL` registers expose `UNIPHY_CHANNEL[0-3]_XBAR_SOURCE` selectors and `DOUT_PHY_CHANNEL[0-3]_EN` enables. These are the hardware-level source selection and lane-enable controls behind display link routing.

The DCIO strap/control block includes `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `CC_DC_MISC_STRAPS`, `INTERCEPT_STATE`, pattern generator bits, global sync/swaplock pad controls, debug output selection, and `DCIO_SOFT_RESET`. Security and platform policy bits include `HDCP_DIS`, `HDCP_KEYS_INVALID`, and `HDMI_DISABLE`; reset bits cover PHY/link PLLs, DVO, DAC, DIG, AUX, DDC, audio, and DMCU domains.

The main GPIO block is broad:

- `DC_GPIO_GENERIC_*` covers generic pads A-G, including mask, input/output value, enable, pull-down, receive state, and strength fields.
- `DC_GPIO_DDC[1-6]_*` covers DDC clock/data pads and AUX overlay mode/polarity/power-down permissions for six connectors.
- `DC_GPIO_DDCVGA_*` is the VGA DDC variant with input polarity and data strength fields.
- `DC_GPIO_SYNCA_*`, `DC_GPIO_GENLK_*`, and `DC_GPIO_HPD_*` cover sync, genlock, swaplock, and hot-plug detect pads.
- `DC_GPIO_DRIVE_STRENGTH_S0`, `DC_GPIO_DRIVE_STRENGTH_S1`, `DC_GPIO_DRIVE_TXIMPSEL`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, and `DC_GPIO_TX12_EN` expose pad electrical configuration.
- `PHY_AUX_CNTL` and `DC_GPIO_AUX_CTRL_[0,1,3,4,5]` define AUX/DDC analog controls such as wake, pad RX selection, comparator selection, termination, DP/DN swap, hysteresis, VOD tune, I2C mode, 1.2 V enable, and pad I2C control.
- `AUXI2C_PAD_ALL_PWR_OK` reports all-power-good bits for AUX/I2C PHYs 1-6.

The I2S/SPDIF subset defines audio-pad control through `DC_GPIO_I2S_SPDIF_MASK`, `_A`, `_EN`, `_Y`, and `_STRENGTH`, including data, MCLK, BCLK, LRCK, SPDIF, pull-up/RX selection, RX enable, and drive strength fields.

The four UNIPHY macro-control banks, `DCIO_UNIPHY[0-3]_UNIPHY_MACRO_CNTL_RESERVED[0-57]`, are uniform full-register reserved fields. Each register exposes only `UNIPHY_MACRO_CNTL_RESERVED` at shift 0 with mask `0xFFFFFFFFL`. They are still part of the hardware register map and can matter for firmware bring-up, diagnostics, generated address coverage, or vendor-specific programming flows outside ordinary field-level driver logic.

The panel power sequence block defines `DC_GPIO_PWRSEQ_*` pad controls for `VARY_BL`, `DIGON`, and `BLON`, then `PANEL_PWRSEQ_CNTL`, `PANEL_PWRSEQ_STATE`, `PANEL_PWRSEQ_DELAY1`, `PANEL_PWRSEQ_DELAY2`, `PANEL_PWRSEQ_REF_DIV1`, `PANEL_PWRSEQ_REF_DIV2`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, `BL_PWM_GRP1_REG_LOCK`, `PWRSEQ_DBG_SEL`, and `PWRSEQ_SPARE`. These fields control panel target state, sync/digital/backlight outputs, timing delays, reference dividers, PWM duty/period, frame-start update recognition, and double-buffer locking.

The DSCC0 block begins the Display Stream Compression compressor register surface. It defines compressor topology and status fields in `DSCC0_DSCC_CONFIG[0-2]` and `DSCC0_DSCC_STATUS`, interrupt enable/status/clear fields for rate-control-buffer model overflow, output-buffer overflow/underflow, and end-of-frame-not-reached conditions, then `DSCC0_DSCC_PPS_CONFIG[0-22]` fields that map the DSC Picture Parameter Set into hardware registers. The PPS fields include DSC version, PPS identifier, line buffer depth, bits per component/pixel, chunk size, picture/slice dimensions, initial transmit/decode delays, scale intervals, BPG offsets, rate-control model size, edge/quantization/tgt offset fields, RC buffer thresholds, and range min/max QP plus range BPG offsets for ranges 0-14.

The tail of the chunk defines DSCC memory power controls, error metrics, fullness telemetry, and debug bus selection: `DSCC0_DSCC_MEM_POWER_CONTROL[0-1]`, squared-error lower/upper counters for R/Y, G/Cb, and B/Cr, max absolute error registers, output/rate buffer max fullness registers, debug indexes 0-3, and `DSCC0_DSCC_TEST_DEBUG_BUS_ROTATE`.

## Control Flow

This header chunk has no runtime control flow. Its control-flow role is indirect: register accessor macros and tables in DCN401 code compile these constants into read/modify/write sequences.

A typical generated flow in the AMD display stack is: a DCN401 component constructor builds a register table from offset macros and a shift/mask table from this header, component methods call common helpers such as field reads/writes, and those helpers use the shift/mask values to preserve unrelated register bits while setting or testing the requested hardware field. For example, GPIO factory/translate paths use DDC/HPD/AUX pad masks to create and route I2C/AUX/HPD GPIO objects; resource creation uses DIO, DSC, I2C, AUX, IRQ, and timing component tables; DMUB DCN401 code uses the same generated style for firmware-facing register access.

Hardware sequencing implied by the fields is mostly in external code. Panel power sequencing depends on writes to target-state, delay, ref-divider, PWM, and lock/update fields, then reads of `PANEL_PWRSEQ_STATE` and update-pending/status fields. DSCC programming depends on loading `DSCC0_DSCC_PPS_CONFIG*` and compressor config fields before enabling or validating DSC streams, while status and interrupt fields are later read or cleared when overflows, underflows, or end-of-frame failures occur.

## State And Persistence Behavior

The macros themselves are stateless and persistent only as source-level constants compiled into the kernel driver. They define how driver state maps to MMIO register state. Runtime state lives in hardware registers and in the AMD display component structs that hold offset, shift, and mask tables.

Several groups map to durable hardware configuration while the display engine is powered:

- UNIPHY inversion, crossbar source, and channel-enable bits describe physical link routing.
- DCIO straps expose hardware strap state and platform policy; some are read-only or platform-owned from the driver's perspective.
- GPIO/DDC/AUX/HPD fields represent live pad ownership, output enables, input values, electrical tuning, pull-up/pull-down, receive state, and AUX/DDC mode.
- Panel power sequence and backlight PWM fields persist as panel-control hardware state until changed, reset, or power-gated.
- DSCC PPS/config registers persist compressor setup for active DSC streams; DSCC status, error, fullness, and interrupt fields are telemetry or latched event state.

The reserved UNIPHY macro-control registers are especially sensitive state because the field names do not describe individual semantics. Treating them as ordinary bitfields risks writing undocumented PHY state.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCN401 register set. Offset macros from the matching `dcn_4_1_0_offset.h` identify MMIO addresses, while this file provides field positions and masks. The broader AMD display code turns those macros into typed register tables through per-block `*_MASK_SH_LIST_DCN401` and `*_REG_LIST_DCN401` macro lists.

Primary integration points in this source tree are:

- DCN401 resource construction, which includes this header and builds register/mask/shift tables for DIO, I2C, AUX, DSC, clock, timing, OPP, HUBP, DCCG, and hardware sequencer objects.
- DCN401 GPIO factory/translation, which needs the DDC, AUX, HPD, generic GPIO, sync, and power-sequence masks to map BIOS connector objects and GPIO IDs onto physical pads.
- DCN401 IRQ service, which depends on hotplug and display interrupt masks elsewhere in the same generated header and may interact with HPD/DSCC status fields.
- DMUB DCN401 support, which includes the same generated header for firmware-controller register access and boot/panel-power sequencing interactions.
- DRM/KMS display modesetting, where the higher-level pipe, link, panel, audio, DSC, and HPD flows ultimately rely on these constants for correct MMIO access.

The DSCC0 PPS fields integrate with DisplayPort DSC and link bandwidth policy. The values programmed into `DSCC0_DSCC_PPS_CONFIG*` should correspond to the negotiated DSC PPS sent over the link; mismatches can produce visible corruption, link training failures, or sink-side decode errors.

## Risks And Edge Cases

The highest risk is generated-header drift. If any shift or mask differs from the hardware specification or from the matching offset header, register writes can silently target the wrong bits. Because many DC helpers use generic macros, a wrong constant may compile cleanly and fail only on DCN401 hardware.

GPIO and AUX/DDC pad controls are electrical and connector-facing. Incorrect masks for pull-ups, pull-downs, RX enables, AUX polarity, AUX DP/DN swap, I2C mode, VOD tune, termination, or power-good handling can break DDC reads, AUX transactions, HPD detection, link training, or panel/backlight control.

Panel power sequencing fields have user-visible and hardware-safety impact. Bad delay/ref-divider/PWM/update-lock masks can cause a panel to power up or down out of order, fail to light the backlight, update brightness at the wrong frame boundary, or leave update-pending bits stuck.

DSCC PPS fields are packed densely and many widths are non-byte-aligned. Off-by-one shifts or masks in `BITS_PER_PIXEL`, `CHUNK_SIZE`, `SLICE_WIDTH`, BPG offsets, RC thresholds, or QP range fields can produce DSC streams that are accepted by driver code but invalid for the compressor or sink. Status clear bits also share registers with occurred bits, so incorrect masks can clear or miss latched error conditions.

The reserved UNIPHY macro-control banks expose full 32-bit masks with no semantic subfields. Driver changes should avoid speculative writes to these fields unless backed by hardware documentation or matching upstream code.

Some fields have paired per-instance repetition with slightly different layouts, such as HPD 1-6 positions and DDC/AUX 1-6 registers. Mechanical copy/paste mistakes are easy, and tests should catch per-connector rather than only connector-0 behavior.

This chunk starts in the middle of `UNIPHYA_CHANNEL_XBAR_CNTL` and ends in the middle of the DSCC0 debug section. A final per-file analysis must reconcile preceding and following chunks before making complete claims about all UNIPHYA fields or the full DSCC0/DSCC instance surface.

## Test Signals

Build-level signals are the first guard: DCN401 display objects that include `dcn_4_1_0_sh_mask.h` should compile with the matching offset header and table initializers. Any missing, renamed, or type-incompatible macro breaks generated register-table construction.

Runtime display signals should cover HPD detection on all exposed connectors, DDC EDID reads over each DDC/AUX pad, AUX transactions, DisplayPort link training, HDMI disable/strap behavior where testable, and connector hotplug interrupt delivery. Multi-connector tests are important because this chunk contains repeated DDC1-6, AUX1-6, HPD1-6, and UNIPHYB-G fields.

Panel/eDP signals should cover panel power on/off, suspend/resume, backlight enable/disable, PWM brightness changes, frame-start synchronized PWM update behavior, and `PANEL_PWRSEQ_STATE` completion/error observation. Tests should include at least one full power-cycle and one brightness change while the panel is active.

DSC signals should include DSC-enabled modes across representative slice counts, picture sizes, bits-per-pixel values, and color formats. Useful failure indicators are DSCC interrupt status for rate-buffer overflow, output-buffer overflow/underflow, end-of-frame-not-reached, max absolute/squared error counters, output buffer fullness, link CRC/visual corruption, and sink-side DSC decode failures.

Power-management signals should include display suspend/resume, DC power-gating, low-power entry/exit for DSCC memory controls, and AUX/I2C pad all-power-good reads after resume. These paths are where stale pad state or incorrect low-power masks tend to surface.

Regression review should compare generated DCN401 shift/mask values against AMD's authoritative register description or a known-good upstream snapshot rather than hand-editing this header. For this source tree, cross-checking with adjacent DCN/DPCS generated headers can catch obvious structural differences, but hardware spec or upstream validation is the stronger signal.
