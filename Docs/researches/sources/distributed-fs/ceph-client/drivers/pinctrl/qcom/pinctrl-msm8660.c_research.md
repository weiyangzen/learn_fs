# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8660.c

## Purpose
Provides the TLMM pin controller table for Qualcomm MSM8660. It covers 173 GPIO groups and additional SDC3/SDC4 pad groups, with functions for display, DSUB, GPS, GP clocks, GSBI buses, HDMI, I2S/MI2S/PCM, PS_HOLD, SD controllers, TSIF, USB FS, VFE, voltage-sense alarm, and EBI2.

## Important APIs, Types, And Data
`PINGROUP()` describes older TLMM GPIO registers at `0x1000 + 0x10 * id`, with separate interrupt target registers at `0x400 + 0x4 * id`, high-ack interrupt status, one-bit interrupt detection, and KPSS target value 4. That one-bit detection means both-edge interrupts rely on common software emulation. `SDC_PINGROUP()` describes SDC3/SDC4 drive/pull groups. `ps_hold_groups[]` maps PS_HOLD to gpio92, enabling common reset/poweroff registration. EBI2 and EBI2 chip-select group arrays cover many high-numbered pins and are called out separately in the function list.

## Control Flow
`arch_initcall(msm8660_pinctrl_init)` registers the platform driver. Matching `qcom,msm8660-pinctrl` invokes `msm8660_pinctrl_probe()`, which calls `msm_pinctrl_probe()`. The shared core maps resources, registers pinctrl and gpiochip state, and scans the functions for `ps_hold` to install restart/poweroff handling. Runtime mux and pinconf operations are entirely table-driven by this file's offsets, function lists, and bit definitions.

## State And Persistence
All file data is static. Runtime state resides in the shared MSM core and TLMM hardware registers. Because `.ngpios = 173`, GPIO lines stop before the SDC3/SDC4 pseudo-groups. PS_HOLD affects persistent platform behavior by registering system-off callbacks, but that is driven by the common core after seeing the function name.

## Dependencies And Integration Points
Depends on `pinctrl-msm.h`, Linux OF/platform driver infrastructure, generic pinctrl consumers, gpiolib, and IRQ handling in `pinctrl-msm.c`. Device trees rely on broad group names for GSBI, LCDC/DSUB, HDMI, SD, TSIF, USB, VFE, EBI2, and PS_HOLD. The separate interrupt target register layout is an important integration detail with older TLMM hardware.

## Risks
MSM8660 uses one-bit interrupt detection, so fast both-edge GPIO IRQs can be lossy under software emulation. The EBI2 and display functions span large pin ranges; table mistakes can break memory/display buses. Several SPI chip-select group arrays are empty, which may surprise clients expecting those named functions to have selectable pins. `ps_hold` misconfiguration can break restart/poweroff. SDC pull values include `-1` for some clock pull fields, which relies on the shared core never applying unsupported configs blindly to those pseudo-groups.

## Test Signals
Signals include probe and gpiochip registration, debugfs showing 173 GPIO groups plus SDC pseudo-groups, GSBI/I2C/SPI/UART pinmux tests, LCDC/HDMI/display pin states, EBI2 bus validation, GPIO IRQ tests emphasizing both-edge behavior, SDC3/SDC4 pull/drive checks, and restart/poweroff tests through PS_HOLD.
