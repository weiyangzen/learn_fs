# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx75.c

## Purpose
Defines the SDX75 TLMM pin controller data for the shared Qualcomm MSM pinctrl driver. It models 133 GPIOs, SDC1 and SDC2 pseudo-pads, expanded mux options, eGPIO metadata bits, and a large GPIO-to-PDC wake map for the `qcom,sdx75-tlmm` binding.

## Important APIs, Types, And Functions
`PINGROUP()` creates `struct msm_pingroup` entries with `REG_BASE = 0x100000`, 0x1000 stride, eleven mux selectors per group, and eGPIO fields `.egpio_enable = 12` and `.egpio_present = 11`. `SDC_QDSD_PINGROUP()` supplies non-GPIO SD pad groups at offsets 0x19a000 and 0x19b000. `sdx75_pins[]`, `enum sdx75_functions`, `sdx75_functions[]`, and many group-name arrays enumerate QUP, Ethernet/RGMII, PCIe, QLINK, UIM, QDSS, audio, and test functions. `sdx75_pdc_map[]` provides wakeirq routing. The probe uses `of_device_get_match_data()` instead of passing a file-local singleton directly.

## Control Flow
`sdx75_pinctrl_init()` registers the platform driver early. The OF match table carries `.data = &sdx75_pinctrl`; `sdx75_pinctrl_probe()` retrieves it, returns `-EINVAL` if absent, and calls `msm_pinctrl_probe()`. After registration, common pinctrl/gpio/irq callbacks use the per-group offsets and mux lists to program TLMM and route wake IRQs.

## State And Persistence
The file has static configuration only. Runtime state belongs to the common driver and hardware registers. `ngpios = 133`; pins 133-139 are SDC-only and not gpiolib GPIOs. eGPIO presence/enable bits add another hardware state dimension that the shared driver may inspect or configure for external GPIO-capable pads.

## Dependencies And Integration Points
Depends on `pinctrl-msm` support for eGPIO bit fields, PDC wake maps, OF match data, and standard TLMM register semantics. Integrates with QUP serial engines, two Ethernet MAC/PHY interfaces through RGMII/SGMII/MDIO/PTP/PPS groups, PCIe clock request lines, SD card detect/write-protect style signals, UIM, QLINK, QDSS, and audio/debug/test functions.

## Risks
This file has a high risk of table transcription errors because Ethernet, QUP, QDSS, and wake mappings are dense and selector positions are hardware ABI. The nonzero `REG_BASE` means a missing base adjustment would target wrong registers for every GPIO. SDC offsets sit in the same numerical region as `REG_BASE`-relative GPIOs, so register-map validation matters. The probe now depends on match `.data`; adding a compatible without data would fail probe. The license string is `GPL` while the SPDX is GPL-2.0-only, which is common but worth noticing in automated license checks.

## Test Signals
Boot probe, debugfs pin/function inspection, GPIO direction/value/IRQ tests below 133, PDC wake validation across representative mapped pins, Ethernet RGMII/MDIO/PTP operation, PCIe clock request pin states, QUP serial/I2C/SPI operation, SD1/SD2 pad drive and pull validation, and eGPIO present/enable behavior where hardware exposes it. Source size reviewed: 1140 lines.
