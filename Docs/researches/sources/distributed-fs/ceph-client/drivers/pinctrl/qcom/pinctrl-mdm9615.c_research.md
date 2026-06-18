# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-mdm9615.c

## Purpose
Provides the TLMM pin controller description for Qualcomm MDM9615. It exposes 88 GPIO groups to the shared `pinctrl-msm` driver and describes a relatively small set of alternate functions: GSBI buses, SDC2, EBI2 LCD, primary/secondary audio, codec MCLK, and `ps_hold`.

## Important APIs, Types, And Data
The file builds `mdm9615_pins[]`, `mdm9615_functions[]`, `mdm9615_groups[]`, and `mdm9615_pinctrl`. `PINGROUP()` is the key macro: each GPIO gets control, I/O, interrupt config, interrupt status, and a separate interrupt target register at `0x400 + 0x4 * id`. It marks `intr_ack_high = 1`, uses `intr_raw_status_bit = 3`, and only one interrupt detection bit, so the common core may emulate both-edge interrupts in software. `MSM_GPIO_PIN_FUNCTION(gpio)` marks the GPIO function for the generic pinmux core. The `ps_hold_groups[]` entry places `ps_hold` on gpio83.

## Control Flow
`arch_initcall(mdm9615_pinctrl_init)` registers the platform driver early. The driver matches `qcom,mdm9615-pinctrl`; probe calls `msm_pinctrl_probe()` with the MDM9615 data. The shared core then registers pin groups/functions, installs pinconf and pinmux callbacks, adds a gpiochip with 88 GPIOs, and configures the summary interrupt handler. Presence of the `ps_hold` function lets `msm_pinctrl_setup_pm_reset()` install restart and poweroff handling through the PS_HOLD register path.

## State And Persistence
The file is static data only. Runtime state is maintained by `pinctrl-msm.c` in MMIO register values and in `struct msm_pinctrl` bitmaps for enabled IRQs, software dual-edge IRQs, mux-disabled IRQs, and first-GPIO glitch avoidance. The `ps_hold` integration creates system-off behavior through core-managed global hooks, but the SoC file itself does not mutate state.

## Dependencies And Integration Points
Depends on the generic MSM pinctrl core, Linux OF platform matching, pinctrl/pinmux APIs, and gpiolib. Device tree states select groups like `gpio4`/`gpio5` for `gsbi2_i2c`, gpio83 for `ps_hold`, or GPIO groups 25-30 for `sdc2`. Older register layout details are captured here through separate interrupt target registers and high-ack interrupt status semantics.

## Risks
The main behavior risk is the one-bit interrupt detection configuration: both-edge GPIO IRQs require the common software polarity-flip loop, making edge loss possible if a line toggles too quickly. `ps_hold` has system-wide reset/poweroff impact, so a wrong group/function association can break restart or poweroff. Many groups are `NA` only; clients expecting undocumented alternate functions will fail until the table is expanded. Interrupt target and ack-high fields must remain aligned with this older TLMM generation.

## Test Signals
Probe logs and `/sys/kernel/debug/pinctrl` should show 88 GPIO groups and the expected function names. Practical tests include GSBI I2C/UART/SPI pin states, audio pins, GPIO IRQ edge/level tests with attention to both-edge behavior, and restart/poweroff validation through `ps_hold`.
