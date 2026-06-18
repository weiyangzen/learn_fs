# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qcs615.c

## Purpose
This file describes the Qualcomm QCS615 TLMM controller. It is a modern tile-aware Qualcomm pinctrl descriptor with 123 regular GPIOs, a UFS reset pad, SDC1/SDC2 pads, function/group maps for the SoC peripherals, a PDC wake IRQ map, and a dual-edge wake erratum flag.

## Important APIs, types, and functions
The main structures are `qcs615_tiles`, `qcs615_pins`, `qcs615_functions`, `qcs615_groups`, `qcs615_pdc_map`, and `qcs615_tlmm`. `PINGROUP(id, tile, ...)` creates normal GPIO groups with 0x1000-per-GPIO offsets, tile selection, standard mux/pull/drive/output/input fields, and interrupt fields with `intr_target_kpss_val = 3`. `SDC_QDSD_PINGROUP()` describes SDC pads and records their tile. `UFS_RESET()` describes the dedicated UFS reset output in the WEST tile with output bit 0 and no IRQ/mux fields.

The platform path is `qcs615_tlmm_probe()` -> `msm_pinctrl_probe(pdev, &qcs615_tlmm)`. The driver matches `qcom,qcs615-tlmm`, registers through `arch_initcall()`, and unregisters on module exit.

## Control flow
The platform driver binds early from device tree. Probe passes `qcs615_tlmm` to the common core, which uses tile names to map group offsets, registers pinmux functions, exposes 124 GPIO lines, configures GPIO interrupts, and handles PDC wake routing from `qcs615_pdc_map`. Device-tree pinctrl states select function names from `qcs615_functions` on group names from `qcs615_groups`.

## State and persistence behavior
No local mutable state is kept. The descriptor covers GPIO0-122, UFS_RESET at pin 123, SDC1_RCLK/CLK/CMD/DATA at 124-127, and SDC2_CLK/CMD/DATA at 128-130. `.ngpios = 124` means UFS_RESET is included in the GPIO line range while SDC pins are not. The descriptor sets `.wakeirq_dual_edge_errata = true`, so wake IRQ handling in the shared core must account for SoC-specific dual-edge behavior.

## Dependencies and integration points
The file depends on `pinctrl-msm.h` and Linux OF/platform/module infrastructure. It integrates with DT pinctrl consumers for QUP serial engines, CCI/camera, QSPI, RGMII/EMAC, PCIe, USB, UIM, audio/MI2S/WSA, display hotplug/vsync, QDSS, navigation/GPS, WLAN, SDC, and UFS reset. The PDC wake map connects selected GPIOs to PDC interrupt numbers for suspend/resume wake.

## Risks and edge cases
QCS615 has three tiles and many cross-tile peripheral functions, so an incorrect tile field silently targets the wrong register resource. `.ngpios = 124` includes UFS_RESET, unlike descriptors where special pads are outside the GPIO range; tests should confirm this is intentional for the common core's UFS reset handling. The dual-edge wake erratum flag is easy to drop during refactors and can affect wake IRQ reliability. SDC1 and SDC2 pads live in different tiles and use different control offsets. Function names such as `pa_indicator_or`, `vsense_trigger_mirnat`, and QDSS variants must remain stable for DT bindings.

## Test signals
Validate binding for `qcom,qcs615-tlmm`, tile resource mapping for SOUTH/EAST/WEST, 124 GPIO lines including expected UFS reset behavior, SDC1/SDC2 storage pinconf, QUP/CCI/QSPI/RGMII/USB/UIM/audio/display pinmux states, GPIO IRQ trigger handling, PDC wake from suspend including dual-edge cases, and debugfs visibility for all functions/groups without requestable dummy groups.
