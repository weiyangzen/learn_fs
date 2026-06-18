# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq4019.c

## Purpose
Describes the Qualcomm IPQ4019/QCA TLMM pin controller for the common MSM pinctrl core. It exposes 100 GPIO pins and their alternate functions for networking-oriented IPQ4019 peripherals such as BLSP, Ethernet, Wi-Fi, LED, QPIC, SDIO, JTAG, I2S, and PCIe.

## Important APIs, Types, and Functions
Important data includes `ipq4019_pins[]`, per-pin arrays from `DECLARE_QCA_GPIO_PINS`, `enum ipq4019_functions`, the function group arrays, `ipq4019_functions[]`, `ipq4019_groups[]`, and `ipq4019_pinctrl`. `PINGROUP()` creates each `struct msm_pingroup` with 15 function slots, 0x1000-per-pin register spacing, open-drain bit `12`, mux/pull/drive/output fields, and two-bit interrupt detection. `QCA_PIN_FUNCTION()` maps function enum values to group lists. `ipq4019_pinctrl_probe()` calls `msm_pinctrl_probe()`.

## Control Flow
At `arch_initcall()` time the platform driver is registered. A device-tree node compatible with `qcom,ipq4019-pinctrl` probes through `ipq4019_pinctrl_probe()`, which hands `ipq4019_pinctrl` to the common Qualcomm driver. The common core then provides the runtime pinmux, pinconf, GPIO, and IRQ behavior.

## State and Persistence Behavior
No driver-local mutable state exists. Static tables persist in kernel memory; runtime pin configuration and interrupt state persist in TLMM registers. `.ngpios = 100` exposes all listed pins as GPIOs. `.pull_no_keeper = true` tells the common core this SoC lacks keeper-bias support, changing how generic pinconf bias requests are interpreted.

## Dependencies and Integration Points
Depends on `pinctrl-msm.h`, platform-device and OF infrastructure, generic pinctrl, GPIO, and IRQ support. It integrates with IPQ4019 board DTs and consumers for MDIO/MDC, RGMII/RMII, Wi-Fi control pins, BLSP I2C/SPI/UART, LED functions, QPIC NAND, SDIO, I2S/SPDIF/audio PWM, JTAG, PCIe, PMU, PRNG ROSC, and test-monitor functions.

## Risks
Many high-numbered pins are present but have only `NA` functions, so accidental function assignment can expose unsupported muxes. `pull_no_keeper = true` is SoC-specific and must not be removed if generic bias keeper requests are invalid in hardware. Open-drain bit support is encoded in the IPQ-specific macro and differs from some APQ/MSM files. As in other table-driven Qualcomm pinctrl drivers, enum and function-list ordering directly affect hardware selector values.

## Test Signals
Expected signals include binding to `qcom,ipq4019-pinctrl`, 100 pins/GPIOs in debugfs, correct muxing for Ethernet, Wi-Fi, BLSP, LED, QPIC, SDIO, JTAG, and I2S groups, GPIO IRQ tests including dual-edge detection, open-drain behavior on relevant pins, and no keeper-bias configuration errors from board DT pin states.
