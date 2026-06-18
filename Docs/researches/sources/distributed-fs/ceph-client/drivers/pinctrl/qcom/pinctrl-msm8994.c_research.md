# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8994.c

## Purpose
This file describes the Qualcomm MSM8994/MSM8992 TLMM pin controller for the shared `pinctrl-msm` core. It defines 146 GPIO pingroups, 10 SDC groups for SDC1/2/3, a 129-entry function table, and an OF platform driver matching both `qcom,msm8992-pinctrl` and `qcom,msm8994-pinctrl`.

## Important APIs, Types, And Functions
`msm8994_pinctrl` is the `struct msm_pinctrl_soc_data` consumed by `msm_pinctrl_probe()`. It references 156 pins, `msm8994_functions`, `msm8994_groups`, and `.ngpios = NUM_GPIO_PINGROUPS` with 146 GPIO groups. `msm8994_pinctrl_probe()` is the handoff to the common core; `msm8994_pinctrl_of_match` provides dual compatible support for MSM8992 and MSM8994; the platform driver is registered through `arch_initcall`.

Local `PINGROUP()` rows have 12 mux slots, compact per-GPIO offsets at `0x1000 + 0x10 * id`, IO/config/status offsets at `+0x4/+0x8/+0xc`, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and KPSS interrupt target value 4. `SDC_PINGROUP()` rows cover SDC1 RCLK/CLK/CMD/DATA, SDC2, and SDC3 with electrical controls only. The function catalog includes BLSP I2C/SPI/UART/UIM instances 1-12, camera master clocks and CCI I2C, QDSS tracing/CTI, HDMI receive, MDP vsync, audio reference, TSIF, PCIe, modem/LTE/GSM, and other SoC integration signals.

## Control Flow
During early init, the driver registers with the platform bus. A matched device probes by passing `msm8994_pinctrl` to `pinctrl-msm.c`. Thereafter, the common core handles all pinctrl, GPIO, and IRQ operations using these tables. Consumer pinctrl states select group/function names from DTS; GPIO operations use groups 0-145; SDC groups participate only in pin configuration because mux and IRQ fields are disabled.

## State And Persistence
All state defined here is immutable table data. Runtime device state is in the common MSM pinctrl driver. TLMM hardware register values produced from the tables persist until later pinctrl/GPIO/IRQ writes or reset. The file does not keep software state across calls beyond platform-driver registration.

## Dependencies And Integration Points
The file depends on Linux module, OF, platform-device, and the local Qualcomm pinctrl core. It integrates through two compatible strings, allowing one data table to serve both MSM8992 and MSM8994 device trees. It does not specify wakeirq maps, reserved GPIOs, tiles, or special bias flags. Downstream integration is through exact function and group names in board DTS files, especially high-fanout BLSP and camera/QDSS/SDC functions.

## Risks And Test Signals
The shared MSM8992/MSM8994 compatible coverage increases the risk of SoC-variant mismatch if a board's TLMM differs from this table. The compact `0x10 * id` register stride differs from newer 4 KiB-per-GPIO descriptions, so offset mistakes can break whole GPIO ranges. Function selector ordering must stay synchronized across enum, function table, and each `PINGROUP()` mux list. Test signals include successful binding for both compatible strings, 146 exported GPIOs, BLSP1-12 pinctrl state coverage, camera and QDSS mux validation, SDC1/2/3 pull/drive programming, and GPIO IRQ routing/polarity tests.
