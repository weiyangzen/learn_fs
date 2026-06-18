# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-apq8084.c

## Purpose
Provides the APQ8084 TLMM SoC description for the shared Qualcomm MSM pinctrl driver. It covers 147 GPIO-capable groups plus six dedicated SDC1/SDC2 pins and exposes a large APQ8084 function set for BLSP, camera, HDMI/eDP, PCIe, SATA, audio, SD, and debug pins.

## Important APIs, Types, and Functions
Key objects are `apq8084_pins[]`, `enum apq8084_functions`, function group arrays such as `blsp_i2c*_groups`, `cci_*_groups`, `hdmi_*_groups`, `pci_*_groups`, `sdc*_groups`, `apq8084_functions[]`, `apq8084_groups[]`, and `apq8084_pinctrl`. `PINGROUP()` emits each GPIO `struct msm_pingroup` with eight possible alternate-function slots, standard mux/pull/drive/output bits, IRQ bits, and `0x1000 + 0x10 * id` register spacing. `SDC_PINGROUP()` describes SDC1 and SDC2 control registers without GPIO or interrupt semantics.

## Control Flow
The driver registers at `arch_initcall()` time. When OF creates a platform device compatible with `qcom,apq8084-pinctrl`, `apq8084_pinctrl_probe()` calls `msm_pinctrl_probe(pdev, &apq8084_pinctrl)`. All dynamic behavior is then handled by the common Qualcomm pinctrl core.

## State and Persistence Behavior
This file has only static const-like SoC description data. The common core allocates runtime driver state and writes hardware registers when clients select pin states or use GPIO/IRQ APIs. The `.ngpios = NUM_GPIO_PINGROUPS` value intentionally exposes only the first 147 groups as GPIOs; the SDC entries remain pinctrl-only groups for pull/drive configuration.

## Dependencies and Integration Points
Depends on the generic pinctrl framework through `pinctrl-msm.h`, OF matching, and platform-driver registration. Integration points include APQ8084 device-tree pinctrl nodes and peripheral drivers for BLSP UART/I2C/SPI/UIM, camera CCI and MCLK, HDMI/eDP, PCIe, SATA, SD/eMMC, MI2S/Slimbus/SPDIF, HSIC, GCC clocks, and miscellaneous test/debug functions.

## Risks
The APQ8084 table is dense and selector-sensitive. Incorrect enum values, missing `NA` placeholders, wrong group names, or bad SDC register offsets can silently program unrelated pins. Because the GPIO register stride and interrupt fields are encoded in macros, macro drift from other Qualcomm TLMM generations is a common maintenance hazard. GPIO count must remain 147 so the six SDC pins are not exported as GPIO lines.

## Test Signals
Probe should bind to `qcom,apq8084-pinctrl`, debugfs should show 153 pins and 147 GPIO groups, and DT pin states should resolve for BLSP1-12, camera CCI/MCLK, display, PCIe/SATA, SDC1/2/3/4, and audio groups. Functional testing should include GPIO IRQs, drive/pull changes on SDC pins, and peripheral boot logs free of pinctrl lookup failures.
