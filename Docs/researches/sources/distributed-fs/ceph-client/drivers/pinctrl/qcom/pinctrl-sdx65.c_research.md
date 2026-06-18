# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx65.c

## Purpose
Describes the Qualcomm SDX65 TLMM controller for the common MSM pinctrl implementation. It covers 108 regular GPIOs, a UFS reset pseudo-pin, four SDC/QDSD pins, SoC mux functions, and GPIO-to-PDC wake interrupt routing for the `qcom,sdx65-tlmm` compatible.

## Important APIs, Types, And Functions
`PINGROUP()` defines normal GPIO group register offsets from `REG_BASE + 0x1000 * id` with mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, value bits 0/1, and IRQ fields at bits 0-5. `SDC_QDSD_PINGROUP()` describes SD controller pads without mux/GPIO/IRQ support. `UFS_RESET()` defines the dedicated reset output with pull, drive, and output value support but no mux or interrupt fields. `sdx65_pdc_map[]` maps selected GPIO numbers to PDC IRQ lines, and `sdx65_pinctrl` packages pins, functions, groups, `ngpios = 109`, and wakeirq metadata.

## Control Flow
The platform driver is registered from `arch_initcall`. Matching `qcom,sdx65-tlmm` invokes `sdx65_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`. The common driver then consumes `sdx65_groups[]` to resolve device-tree pinctrl states, service GPIO requests, and register IRQ domains. Wake-capable GPIOs are connected through `sdx65_pdc_map[]` when the common code arms wake interrupts.

## State And Persistence
All state in this file is static descriptor data. Hardware state persists in TLMM, UFS reset, and SD controller pad registers after common-driver writes. `ngpios = 109` includes GPIO0-107 plus the UFS reset group as a GPIO-like controllable line, while SDC pins 109-112 are pinctrl-only special groups.

## Dependencies And Integration Points
Integrates with `pinctrl-msm`, gpiolib, irqchip/PDC wake routing, UFS reset control via pinctrl/GPIO semantics, SD/eMMC pad configuration, and device-tree consumers for BLSP, UIM, QLINK0/1/2, QDSS, SPMI, PCIe, audio, TSENS, DDR/BIMC test, and USB PHY analog control functions. The DT compatible differs from SDX55 by using `-tlmm`.

## Risks
The UFS reset group uses offset 0x0 while normal GPIO0 also starts at base 0x0; correctness depends on the hardware map and common driver treating the pseudo-group as intended. Wake routing is hand-coded, so wrong GPIO/PDC pairs can produce missed suspend wakeups or spurious wake events. Empty mux alternatives represented by `_` still consume mux selector positions; any enum or table reorder changes ABI-visible function numbers. SDC/QDSD groups have no interrupt or output-enable fields, so accidental GPIO use should be rejected by the core.

## Test Signals
Probe with `qcom,sdx65-tlmm`; verify 113 pins, 109 GPIO-capable groups, UFS reset toggling, SD/eMMC card operation, PDC wake from mapped GPIOs in suspend, and mux application for BLSP/UIM/QLINK/QDSS states. Debugfs should expose function groups consistent with `sdx65_functions[]`. Source size reviewed: 955 lines.
