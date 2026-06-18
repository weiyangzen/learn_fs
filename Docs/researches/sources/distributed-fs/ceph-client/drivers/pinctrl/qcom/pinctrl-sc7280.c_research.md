# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280.c

## Purpose
This file describes the Qualcomm SC7280 main TLMM pin controller for `pinctrl-msm`. It enumerates 176 GPIO-capable pads, high-numbered eGPIO-capable pads, UFS reset, SD card special groups for `sdc1` and `sdc2`, alternate function tables, and GPIO-to-PDC wake IRQ mappings. It is the main SoC pinctrl companion to the separate SC7280 LPASS LPI audio pinctrl file.

## Important APIs, Types, And Functions
The primary tables are `sc7280_pins`, `sc7280_functions`, `sc7280_groups`, `sc7280_pdc_map`, and `sc7280_pinctrl`. `PINGROUP()` supplies ten mux slots, standard 0x1000-byte GPIO register spacing, eGPIO bit positions, and IRQ field locations. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` model non-GPIO storage pads. The SoC descriptor sets `.ngpios = 176`, `.wakeirq_map`, `.nwakeirq_map`, and `.egpio_func = 9`. The platform driver also attaches `.pm = &msm_pinctrl_dev_pm_ops`.

## Control Flow
The driver registers at `arch_initcall()` as `sc7280-pinctrl`. A DT node compatible with `qcom,sc7280-pinctrl` invokes `sc7280_pinctrl_probe()`, which calls `msm_pinctrl_probe()` with the static SC7280 descriptor. The MSM core then registers the pin controller, GPIO chip, irqchip, wake IRQ handling, and PM behavior. Local code only handles platform driver registration and unregister.

## State And Persistence
All source-level data is immutable. Hardware state is stored in TLMM registers and controlled by the shared MSM core. eGPIO-capable pads from the high-numbered group range use the eGPIO present/enable bits and mux function index 9. Wake behavior persists through the PDC mapping table and common suspend/resume handling.

## Dependencies And Integration Points
The file depends on OF platform matching, module infrastructure, and `pinctrl-msm.h`. It integrates with DT consumers for QUP serial engines, QSPI, camera, display, audio-adjacent TLMM pins, QDSS trace/debug, USB, UFS reset, SDHCI `sdc1` and `sdc2`, and general GPIO users. Runtime power management and suspend/resume are handled through the common MSM PM ops.

## Risks And Test Signals
SC7280 has many mux aliases and eGPIO-capable high pads, so function ordering and `.egpio_func = 9` are high-risk data points. `.ngpios = 176` must exclude UFS and SD special groups at indices 175-182 from normal GPIO exposure as intended by the common core. The wake map is large enough that single-entry mistakes can produce suspend-only regressions. Test signals include successful probe with 176 GPIO lines, pinctrl state selection for QUP/QSPI/camera/display/UFS/SD clients, eGPIO mode validation on pads 144-174, GPIO IRQ operation, suspend wake from representative PDC-mapped GPIOs, and resume behavior through `msm_pinctrl_dev_pm_ops`.
