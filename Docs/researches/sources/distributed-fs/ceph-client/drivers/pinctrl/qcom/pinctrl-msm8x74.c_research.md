# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8x74.c

## Purpose
This file describes the Qualcomm MSM8x74/MSM8974 TLMM pin controller. It is an older Qualcomm pinctrl descriptor with 146 normal GPIO groups, SDC1/SDC2 groups, HSIC groups, a partial mux catalog, and an MPM wake IRQ map for the shared `pinctrl-msm` core.

## Important APIs, types, and functions
The core descriptor data is `msm8x74_pins`, `msm8x74_functions`, `msm8x74_groups`, `msm8x74_mpm_map`, and `msm8x74_pinctrl`. `PINGROUP()` describes normal GPIOs with eight mux slots and compact register spacing: control at `0x1000 + 0x10 * id`, I/O at `0x1004 + 0x10 * id`, interrupt config at `0x1008 + 0x10 * id`, and interrupt status at `0x100c + 0x10 * id`. `SDC_PINGROUP()` describes SDC pads, and `HSIC_PINGROUP()` describes HSIC strobe/data pins with a two-function mux and mux bit 25.

The driver path is `msm8x74_pinctrl_probe()` -> `msm_pinctrl_probe(pdev, &msm8x74_pinctrl)`. It registers through `arch_initcall()` and matches `qcom,msm8974-pinctrl`.

## Control flow
After the platform driver matches, all control is delegated to the shared Qualcomm core. The common core uses the group table for pinmux selection, pinconf, GPIO operations, and IRQ programming. The older layout differs from newer 0x1000-per-GPIO TLMM blocks, so the register offsets in this file are the key control-flow input for all runtime operations.

## State and persistence behavior
The file has no mutable state. It statically advertises 154 pin descriptors: GPIO0-145, SDC1/2 CLK/CMD/DATA, and HSIC STROBE/DATA. `NUM_GPIO_PINGROUPS` sets `ngpios = 146`, so SDC and HSIC descriptors are not exported as standard GPIO lines even though HSIC appears in the `gpio_groups` list for mux grouping.

## Dependencies and integration points
It depends on Linux OF/platform driver support and `pinctrl-msm.h`. Integration points include DT pinctrl states for BLSP UART/SPI/I2C/UIM, UIM, SDC3/4 mux functions, GCC clocks, MI2S/audio, HDMI/eDP, camera clocks, CCI, PDM, TSIF, HSIC, GRFC, BT/FM/WLAN, and slimbus. `msm8x74_mpm_map` integrates selected GPIOs with the low-power MPM wake controller.

## Risks and edge cases
The file contains a TODO stating that not all possible functions are modeled, so DT users can only request the functions listed here. Its older 0x10 register stride and `intr_target_kpss_val = 4` differ from later SoCs, making copy/paste from newer descriptors risky. HSIC groups use special mux semantics and disabled GPIO/IRQ fields. SDC groups share control registers by bus, so pull/drive bit metadata must be exact. Wake IRQ map mistakes will usually surface only in suspend testing.

## Test signals
Validate platform binding for `qcom,msm8974-pinctrl`, the 146 GPIO line boundary, pinctrl debugfs group/function visibility, BLSP and CCI peripheral bring-up, SDC and HSIC operation where populated, GPIO interrupt type handling, MPM wake from suspend, and negative tests for functions not present in the partial mux table.
