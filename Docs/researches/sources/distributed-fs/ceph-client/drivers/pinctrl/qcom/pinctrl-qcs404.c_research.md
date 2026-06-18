# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qcs404.c

## Purpose
This file is the Qualcomm QCS404 TLMM pin controller descriptor. It enumerates pins, mux functions, tile membership, GPIO/SPI/I2C/audio/display/ethernet-related groups, SDC special groups, and the SoC data needed by the shared Qualcomm pinctrl core.

## Important APIs, types, and functions
The key objects are `qcs404_tiles`, `qcs404_pins`, `qcs404_functions`, `qcs404_groups`, and `qcs404_pinctrl`. The tile enum maps `NORTH`, `SOUTH`, and `EAST` to tile names for the common core. `PINGROUP(id, tile, ...)` uses 0x1000-per-GPIO offsets, sets the tile, and provides standard GPIO, mux, and IRQ bit fields with `intr_target_kpss_val = 4`. `SDC_QDSD_PINGROUP()` describes SDC1/SDC2 pads in the SOUTH tile and disables GPIO/IRQ fields.

The executable path is `qcs404_pinctrl_probe()` -> `msm_pinctrl_probe(pdev, &qcs404_pinctrl)`. The driver registers at `arch_initcall()` and matches `qcom,qcs404-pinctrl`.

## Control flow
After DT match and probe, `pinctrl-msm` registers the pinctrl and GPIO/IRQ surfaces using the QCS404 descriptor. Tile names and tile ids let the common core map each group's register offsets into the correct memory resource. Function selection and pin configuration are entirely table-driven by `qcs404_groups`.

## State and persistence behavior
This file has no mutable state. The pin descriptors cover GPIO0-119 and SDC special pins 120-126. `.ngpios = 120` restricts GPIO export to the real GPIO range. There is no wake IRQ map in `qcs404_pinctrl`, so this descriptor does not advertise TLMM-to-MPM/PDC wake routing.

## Dependencies and integration points
The file depends on Linux module/platform/OF APIs and `pinctrl-msm.h`. It integrates with DT pinctrl states for HDMI, BLSP UART/SPI/I2C, QDSS, RGB/LCDC-style display pins, PWM LEDs, I2S/MI2S audio, EBI, RGMII Ethernet, NFC, SD write protect, clocks, WSA, and SDC1/2. The tile list is a direct integration point with multi-resource TLMM register mapping in the common driver.

## Risks and edge cases
The tile value on each group is critical; the numeric register offset alone is not sufficient. Several group arrays intentionally repeat GPIO names where one logical function uses multiple mux slots on the same pad, so naive duplicate cleanup can change behavior. There is no wake map, so adding wake support requires more than adding DT properties. The many function names with suffixes such as `_a`, `_b`, and QDSS trigger variants must align with DT binding expectations.

## Test signals
Validate binding for `qcom,qcs404-pinctrl`, three tile resource mapping, 120 GPIO lines, pinctrl debugfs function/group output, BLSP and RGMII peripheral bring-up, display/audio mux states, SDC1/2 pinconf behavior, GPIO IRQ handling in each tile, and expected absence of wakeirq map behavior from this descriptor.
