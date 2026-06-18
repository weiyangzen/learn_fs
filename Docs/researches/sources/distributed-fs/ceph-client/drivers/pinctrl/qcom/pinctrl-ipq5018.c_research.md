# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5018.c

Purpose: IPQ5018 TLMM pin controller description for the Qualcomm `pinctrl-msm` core. It does not implement GPIO logic itself; it declares the SoC pin, function, group, register-bit, and OF-match data consumed by `msm_pinctrl_probe()`.

Important APIs, types, and tables: `PINGROUP()` builds `struct msm_pingroup` entries with one GPIO group, 10 mux slots, 0x1000 register stride, mux bit 2, pull bit 0, drive bit 6, OE bit 9, input/output value bits 0/1, and two-bit interrupt detection. `ipq5018_pins[]` exposes GPIO 0-46, `DECLARE_MSM_GPIO_PINS()` creates one-pin arrays, `enum ipq5018_functions` assigns `msm_mux_*` IDs, function group arrays list legal pins, `ipq5018_functions[]` maps names through `MSM_PIN_FUNCTION()`/`MSM_GPIO_PIN_FUNCTION()`, and `ipq5018_groups[]` contains 47 pingroups. `ipq5018_pinctrl` reports 47 GPIOs.

Control flow: `arch_initcall(ipq5018_pinctrl_init)` registers `ipq5018_pinctrl_driver`. OF matching on `qcom,ipq5018-tlmm` invokes `ipq5018_pinctrl_probe()`, which delegates all setup to `msm_pinctrl_probe(pdev, &ipq5018_pinctrl)`. Module exit unregisters the platform driver.

State and persistence: all SoC metadata is static const data. Runtime pin state, GPIO state, IRQ handling, and register writes live in the common `pinctrl-msm` implementation and TLMM hardware registers, not in this file.

Dependencies and integration: depends on Linux platform/OF module infrastructure and `pinctrl-msm.h`. Device trees must use the compatible string and mux function names declared here. The table integrates BLSP, QSPI/SDC1, PCIe wake/clock, audio, MDIO/MDC, PWM, QDSS, LED, EUD, WCI/XFEM, and related TLMM functions.

Risks: table-only drivers are sensitive to off-by-one GPIO counts, wrong mux enum ordering, wrong group membership, and mismatched register bit definitions. Pins with repeated or alternative audio/QDSS functions need board-level validation because the common core trusts these tables. No reserved GPIO list is present, so ownership restrictions must come from DT or consumers.

Test signals: build coverage should catch missing enum/function/group symbols. Runtime signals include successful probe for `qcom,ipq5018-tlmm`, pinctrl debugfs listing 47 GPIO groups, GPIO direction/value changes through gpiolib, interrupt delivery on TLMM GPIOs, and peripheral smoke tests for BLSP, PCIe wake, QSPI/SDC1, MDIO/MDC, audio, PWM, and QDSS routes.
