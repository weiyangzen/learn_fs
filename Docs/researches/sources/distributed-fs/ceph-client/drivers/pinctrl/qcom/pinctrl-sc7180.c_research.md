# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7180.c

## Purpose
This file describes the Qualcomm SC7180 TLMM pin controller. It is a static data driver for `pinctrl-msm`, but unlike several newer flat-register variants it also models TLMM tiles (`north`, `south`, `west`) and a wake IRQ dual-edge erratum. It defines 120 GPIO-capable pads, UFS reset, SD card pads for `sdc1` and `sdc2`, alternate functions, and a GPIO-to-PDC wake map.

## Important APIs, Types, And Functions
`sc7180_tiles` and the `NORTH`, `SOUTH`, `WEST` enum name the register regions used by group descriptors. `PINGROUP(id, _tile, ...)` supplies a tile plus standard MSM register offsets and mux/config/IRQ bit positions. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` place special storage groups in the south tile. The data tables are `sc7180_pins`, `sc7180_functions`, `sc7180_groups`, `sc7180_pdc_map`, and `sc7180_pinctrl`. The SoC descriptor sets `.tiles`, `.ntiles`, `.ngpios = 120`, `.wakeirq_map`, and `.wakeirq_dual_edge_errata = true`.

## Control Flow
`sc7180_pinctrl_init()` registers the platform driver at `arch_initcall()`. A DT node with `qcom,sc7180-pinctrl` calls `sc7180_pinctrl_probe()`, which hands `sc7180_pinctrl` to `msm_pinctrl_probe()`. The platform driver also supplies `.pm = &msm_pinctrl_dev_pm_ops`, so system power management is handled by the shared MSM code. Runtime operations are data-driven by the common pinctrl, pinconf, gpiolib, irqchip, and wakeirq logic.

## State And Persistence
All local data is static and immutable. Hardware state is split across the TLMM tile register regions and persists until reset or reconfiguration. The common core tracks runtime state, applies pinctrl states, and handles suspend/resume with the PM ops. Wake IRQ behavior uses the static PDC map plus the dual-edge erratum flag, which changes how dual-edge wake handling is treated by the common code.

## Dependencies And Integration Points
The driver depends on OF platform matching and `pinctrl-msm.h`. It integrates with SC7180 device tree pinctrl clients including QUP I2C/UART, QSPI, MI2S, LPASS external signals, display hotplug/vsync, UIM, GPS/PPS, WLAN/QLINK, USB PHY, UFS reset, and SDHCI `sdc1`/`sdc2`. It integrates with suspend wake through PDC mappings and with power management through `msm_pinctrl_dev_pm_ops`.

## Risks And Test Signals
Tile assignment is a key risk: a correct mux function with the wrong tile points the common core at the wrong MMIO region. The dual-edge wake erratum flag is another SoC-specific behavior that should not be dropped during refactors. `.ngpios = 120` must exclude UFS and SD special groups at indices 119-126 as GPIO lines where appropriate. Test signals include successful probe, line count, pinctrl states across all three tiles, UFS reset and both SD controller pad groups, GPIO IRQs, suspend/resume with PM ops, and dual-edge wake testing on representative PDC-mapped GPIOs.
