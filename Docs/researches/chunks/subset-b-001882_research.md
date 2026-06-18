# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 42176-44691

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable logic; it publishes `#define` constants for field shifts and bit masks used to encode and decode MMIO register values in the AMDGPU display driver.

The requested range starts in the `dce_dc_dio_dio_misc_dispdec` block at the mask half of `DIO_SCRATCH6`, covers DIO memory power, clock gating, soft reset, link control, and a DC perfmon instance, then covers DCIO link/GPIO/AUX pad control, five UNIPHY macro reserved blocks (`DCIO_UNIPHY0` through `DCIO_UNIPHY4`, reserved registers 0 through 57), and enters `dce_dc_pwrseq0_dispdec_pwrseq_dispdec` through the first `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` shift macro. The range contains 2,086 `#define` lines, normally organized as pairs or groups of `__SHIFT` and `_MASK` macros.

Although the file lives under a local `ceph-client` source mirror, this path is AMDGPU display-controller hardware metadata, not Ceph or distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, local includes, allocation paths, locks, or callbacks in this range. The public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used when placing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field in the 32-bit MMIO register.
- Full-width scratch or reserved fields such as `DIO_SCRATCH7__DIO_SCRATCH7_MASK` and `DCIO_UNIPHY*_UNIPHY_MACRO_CNTL_RESERVED*__UNIPHY_MACRO_CNTL_RESERVED_MASK` expose all 32 bits.

Major register families in this chunk:

- DIO misc: `DIO_SCRATCH6` tail, `DIO_SCRATCH7`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIG_SOFT_RESET`, `DIO_CLK_CNTL2`, `DIO_CLK_CNTL3`, HDMI RX status timer control, PSP/generic interrupt clear/message registers, and `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL`.
- `DC_PERFMON18`: perf counter enable/reset/clear/start/stop, event selectors, state flags, overflow/underflow/current-value interrupt fields, and high/low counter-value registers.
- DCIO display core: generic `DC_GENERICA`/`DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA` through `UNIPHYE` link control and channel crossbar fields, `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `INTERCEPT_STATE`, backlight PWM frame-start display selection, genlock/swaplock pad control, and `DCIO_SOFT_RESET`.
- DCIO chip GPIO and pads: generic GPIO mask/A/en/Y registers, DDC1 through DDC5 and DDCVGA mask/A/en/Y registers, GENLK and HPD mask/A/en/Y registers, `DC_GPIO_PWRSEQ0_EN`, pad strength registers, `PHY_AUX_CNTL`, `DC_GPIO_PWRSEQ1_EN`, TX12/RXEN/pull-up controls, AUX control registers 0 through 5, and `AUXI2C_PAD_ALL_PWR_OK`.
- UNIPHY macro reserved ranges: five address blocks, each defining 58 full-width `UNIPHY_MACRO_CNTL_RESERVED` fields. These are opaque 32-bit macro-control slots rather than named functional fields in this generated header.
- PWRSEQ0 and backlight PWM: GPIO power-sequencer enable/control/mask/A/Y fields, panel power-sequence control and state, power-up/down delay fields, reference dividers, backlight PWM duty/enable/fractional/frame-start fields, PWM period fields, and the first shift definition for `BL_PWM_GRP1_REG_LOCK`.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by token-pasting helpers in DCN 3.1.5 display code:

1. DCN 3.1.5 resource, IRQ, and DMUB code include `dcn_3_1_5_offset.h` with this matching `dcn_3_1_5_sh_mask.h`.
2. Register table macros such as `SR(...)`, `SRI(...)`, and DMUB `DMUB_SF(...)` combine offset macros with these field masks and shifts.
3. The resulting tables are consumed through `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, IRQ ack helpers, DIO helpers, DMUB service code, and panel-control paths.
4. Hardware sequencing is owned by the consumers. This generated header does not know when a field may be read, written, polled, write-one-to-clear, or left untouched.

One direct consumer visible in `dcn315_resource.c` is `DIO_MEM_PWR_CTRL`: it is added to hardware-sequencer and DIO register tables, and its `I2C_LIGHT_SLEEP_FORCE` field is exposed through mask/shift structs. `dcn10_dio.c` then writes `DIO_MEM_PWR_CTRL` and optionally sets `I2C_LIGHT_SLEEP_FORCE` in `dcn10_dio_mem_pwr_ctrl()`. The PWRSEQ0/PWM fields in this chunk are part of the same ASIC field namespace; on DCN 3.1 panel control, `dcn31_panel_cntl.c` largely delegates backlight/panel state operations to DMUB commands and persists PWM register values in `stored_backlight_registers`.

## State And Persistence Behavior

The chunk stores no software state. It describes bit positions in MMIO-backed display hardware state:

- DIO power and clock state: I2C and DP link memory power status, light-sleep force/disable bits, DISPCLK/REFCLK/SOCCLK/SYMCLK gate-disable controls, and DIO power-management busy/reset flags.
- Digital encoder reset and link state: DIG front-end/back-end soft reset fields, DIO link enable/swap fields, HDMI RX status timer controls, and generic interrupt clear/message fields.
- Perfmon state: counter enable, event selection, trigger mode, reset/clear, overflow/underflow/current-value status and interrupt mask/ack fields, and latched counter values.
- DCIO routing and pad state: UNIPHY link controls and crossbars, pinstrap/intercept states, DCIO soft resets, GPIO mask/output/enable/readback fields, DDC/HPD/GENLK/power-sequence pins, AUX pad controls, pull-up/RX/TX controls, pad drive strength, and AUX/I2C power-good bits.
- UNIPHY reserved state: opaque full-width reserved registers for UNIPHY macro control. Since the field name is generic, correctness depends on hardware documentation and generated register databases outside this header.
- Panel and backlight state: PWRSEQ0 GPIO routing, target/current panel power states, DIGON/SYNCEN/BLON polarity and override bits, sequencing delays, reference dividers, PWM active count, fractional enable, enable, period, and frame-start update behavior.

Persistence is hardware-defined. Many configuration fields retain values until modeset, power gating, suspend/resume, DMUB intervention, or ASIC reset. Status, interrupt, clear, pending, and readback fields may be sticky, read-only, write-one-to-clear, self-clearing, or timing-sensitive. The macros do not encode those semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which supplies the matching register offsets and base-index selectors.
- DCN 3.1.5 base segment definitions in include sites such as `dcn315_resource.c`, `irq_service_dcn315.c`, and `dmub_dcn315.c`.
- `reg_helper.h` and AMD display register-table structs that expect exact mask/shift names from generated headers.
- DMUB firmware command contracts for panel control and backlight state on DCN 3.1-class hardware.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Integration is mostly compile-time token pasting. For example, `HWS_SF(, DIO_MEM_PWR_CTRL, I2C_LIGHT_SLEEP_FORCE, _MASK)` resolves to `DIO_MEM_PWR_CTRL__I2C_LIGHT_SLEEP_FORCE_MASK`, while `HWS_SF(..., __SHIFT)` resolves to the matching shift. IRQ and DMUB code use the same generated namespace for other registers in the full header. The repeated GPIO, DDC, HPD, AUX, UNIPHY, and PWRSEQ fields integrate with display link bring-up, hotplug detection, EDID/DDC/AUX access, embedded-panel power sequencing, backlight PWM handling, genlock/swaplock pads, and low-power display transitions.

## Risks And Edge Cases

- Mask/shift drift is the main risk. These are untyped constants; a wrong bit position compiles cleanly but can program the wrong hardware field.
- The range is an artificial slice. It starts after the `DIO_SCRATCH6` shift macro and stops before the rest of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`; adjacent chunks are required for complete file-level claims.
- Repeated pin and link families are copy-sensitive. DDC1-DDC5/DDCVGA, HPD, GENLK, PWRSEQ pins, AUX controls, UNIPHY A-E link controls, and UNIPHY0-4 reserved ranges are easy to misalign by instance.
- Power and reset bits are high risk. Incorrect DIO memory power, clock-gate, soft-reset, or light-sleep fields can produce blank links, failed AUX/DDC transactions, resume failures, or blocks that never enter/leave low-power state.
- GPIO and pad fields have board-level effects. Wrong masks or enables can break HPD, EDID, AUX, panel power rails, backlight enables, genlock/swaplock pads, or pin pull-ups.
- Full-width reserved UNIPHY fields are opaque. Accidental writes may affect PHY behavior in ways not explained by the generated field name.
- Panel power sequencing and PWM fields are timing-sensitive. Bad delay, reference-divider, enable, override, polarity, or double-buffer lock fields can cause flicker, no backlight, stuck panel power state, or suspend/resume brightness loss.
- Perfmon fields may be clear/ack/pending sensitive. Misusing overflow, underflow, or current-value interrupt masks can create stuck interrupts or misleading performance counters.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support for DCN 3.1.5; missing or renamed macros should fail in `dmub_dcn315.c`, `irq_service_dcn315.c`, `dcn315_resource.c`, and shared DIO/panel-control code.
- Mechanically compare each `__SHIFT`/`_MASK` pair in lines 42176-44691 against AMD's source register database and the matching `dcn_3_1_5_offset.h` register names.
- Verify the known chunk-boundary exceptions: `DIO_SCRATCH6` is partial at the start and `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` is partial at the end.
- Exercise display link bring-up across available DCN 3.1.5 connectors: DP/HDMI modesets, link training, hotplug, HPD RX, EDID/DDC, AUX DPCD reads/writes, multi-display, and suspend/resume.
- Validate DIO low-power behavior by watching for AUX/DDC timeouts, link-training failures, stuck display clocks, resume failures, or abnormal power-management logs when I2C light sleep and DIO memory power controls are touched.
- Test embedded-panel paths where present: panel power on/off, backlight restore after boot and resume, PWM frequency override, brightness changes, BLON/DIGON/SYNCEN behavior, and no visible flicker during frame-start PWM updates.
- Check GPIO and pad behavior through HPD storms, DDC bus recovery, AUX/I2C pad power-good status, pull-up configuration, genlock/swaplock use cases, and board-specific power-sequence pins.
- Validate perfmon register definitions with counter start/stop/reset/clear, overflow/underflow interrupt handling, and stable high/low counter reads if DC perfmon 18 is exposed by diagnostics.

## Cross-Chunk Notes

Previous chunks own the beginning of the DCN 3.1.5 DIO misc block, including `DIO_SCRATCH0` through the `DIO_SCRATCH6__SHIFT` macro. Later chunks continue `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`, `PWRSEQ0_PANEL_PWRSEQ_REF_DIV2`, `PWRSEQ0_PWRSEQ_SPARE`, and additional power-sequencer blocks. The final per-file research document should merge adjacent chunks before making complete claims about all DIO, DCIO, UNIPHY, GPIO, PWRSEQ, or backlight-PWM field coverage in `dcn_3_1_5_sh_mask.h`.
