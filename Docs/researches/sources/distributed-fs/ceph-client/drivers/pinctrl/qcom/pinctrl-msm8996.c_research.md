# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8996.c

## Purpose
This file is the Qualcomm MSM8996 TLMM pin controller descriptor. It does not implement pinctrl algorithms directly; instead it enumerates the SoC's pins, mux functions, pingroups, register offsets, interrupt bit layout, SDC/QDSD special groups, and MPM wake IRQ mappings, then hands all of that static data to the shared Qualcomm `pinctrl-msm` core.

## Important APIs, types, and functions
The driver builds `struct pinctrl_pin_desc msm8996_pins[]`, `struct pinfunction msm8996_functions[]`, `struct msm_pingroup msm8996_groups[]`, `struct msm_gpio_wakeirq_map msm8996_mpm_map[]`, and one `struct msm_pinctrl_soc_data msm8996_pinctrl`. The `PINGROUP()` macro describes normal GPIO groups with ten mux choices, 0x1000 register spacing, GPIO I/O bits, and interrupt configuration bits. `SDC_QDSD_PINGROUP()` describes SD card/QDSD pins where mux, GPIO I/O, and interrupt fields are intentionally disabled with `-1`.

The only executable driver path is `msm8996_pinctrl_probe()`, which calls `msm_pinctrl_probe(pdev, &msm8996_pinctrl)`. `msm8996_pinctrl_init()` registers the `platform_driver` through `arch_initcall()`, and `msm8996_pinctrl_exit()` unregisters it on module exit. Device-tree binding is through `qcom,msm8996-pinctrl`.

## Control flow
At init time the platform driver is registered before many normal modules because TLMM is needed early by board devices. On a matching DT node, the platform bus invokes probe. Probe passes the static SoC descriptor to `pinctrl-msm`, which registers pinctrl, pinmux, pinconf, GPIO, irqchip, and wake IRQ integration based on the descriptor. Runtime pin selection, GPIO direction/value, IRQ type, IRQ masking, and wake setup are handled by the common core using the offsets and bit positions from this file.

## State and persistence behavior
The file owns no mutable runtime state and has no persistence. Its arrays are static constants or static data referenced for the lifetime of the driver. Hardware state persists only in TLMM registers programmed by the common core. The descriptor advertises 150 GPIO-capable pins and seven SDC/QDSD pins, with `ngpios = 150` preventing the non-GPIO SDC descriptors from being exported as GPIO lines.

## Dependencies and integration points
The driver depends on Linux platform devices, OF matching, module infrastructure, and `drivers/pinctrl/qcom/pinctrl-msm.h`. It integrates with DT pinctrl consumers by exposing function and group names such as BLSP, CCI, QDSS, HDMI/eDP, PCIe, QSPI, UIM, TSIF, audio, and SDC groups. The MPM map connects selected GPIO numbers to always-on wake interrupt numbers for suspend/resume wake handling.

## Risks and edge cases
The main risk is descriptor drift: an incorrect function enum order, group name, register offset, or mux slot will cause the common core to program the wrong hardware function while the C code still compiles. The SDC groups share control registers with different pull/drive bit positions, so off-by-one register or bit mistakes can break storage pins. `msm_mux_NA` entries must remain placeholders for unavailable mux slots. Wake IRQ map errors can cause missed wake events or unintended wakeups. Because the file is table-driven, duplicate or missing group names are more likely to be found by functional testing than by compilation.

## Test signals
Useful signals are successful boot with the `qcom,msm8996-pinctrl` node bound, `debugfs` pinctrl listings showing 157 pins and 150 GPIO lines, DT pinmux users selecting BLSP/CCI/SDC/QDSS functions without `-EINVAL`, GPIO direction/value tests, interrupt trigger tests on mapped GPIOs, suspend/resume wake tests for the MPM map, and storage validation for SDC1/SDC2 including pull and drive strength changes.
