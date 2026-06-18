# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos.c

## Purpose
This file implements Exynos-specific external interrupt, wakeup interrupt, suspend/resume, filter, wakeup-mask, and retention behavior for the Samsung pinctrl driver. It is the active SoC logic used by the declarative ARM and ARM64 data files.

## Important APIs, Types, and Functions
`struct exynos_irq_chip` embeds a Linux `irq_chip` and stores EINT register offsets, wakeup-mask register metadata, and a `set_eint_wakeup_mask` callback. `exynos_eint_gpio_init()` initializes external GPIO interrupt handling for EINT GPIO banks. `exynos_eint_wkup_init()` initializes wakeup interrupt domains and chained handlers. `exynos_pinctrl_suspend()`, `exynos_pinctrl_resume()`, `gs101_pinctrl_suspend()`, `gs101_pinctrl_resume()`, `exynosautov920_pinctrl_suspend()`, and `exynosautov920_pinctrl_resume()` save and restore SoC-specific EINT registers. `exynos_retention_init()` creates PMU-backed retention control.

Core IRQ operations are `exynos_irq_mask()`, `exynos_irq_unmask()`, `exynos_irq_ack()`, `exynos_irq_set_type()`, `exynos_irq_request_resources()`, and `exynos_irq_release_resources()`. Wakeup-mask state is held in static `eint_wake_mask_values[MAX_WAKEUP_REG]` and updated by `exynos_wkup_irq_set_wake()` or `gs101_wkup_irq_set_wake()`.

## Control Flow
During probe, the common driver calls `exynos_eint_gpio_init()` for GPIO EINT-capable controllers. That requests the parent IRQ, creates one linear IRQ domain per GPIO EINT bank, duplicates the default `exynos_gpio_irq_chip`, and stores per-bank save state. When the parent IRQ fires, `exynos_eint_gpio_irq()` reads the Exynos service register, derives the bank group and pin number, then dispatches into the bank IRQ domain.

Wakeup initialization scans child nodes for a compatible wakeup EINT controller, clones the matching wakeup `exynos_irq_chip`, and creates domains for EINT wakeup banks. Banks with per-pin interrupts get chained handlers for EINT0-15 style lines; banks without their own `interrupts` property are collected into a muxed handler that reads pending/mask registers and demuxes all active pins.

IRQ resource request locks the GPIO as IRQ and programs the pin function to `EXYNOS_PIN_CON_FUNC_EINT`; release returns it to input. Set-type selects the hardware trigger encoding and switches the Linux IRQ flow handler between edge and level. Suspend writes wakeup masks and saves GPIO EINT registers; resume restores saved registers and, for GS101, toggles EINT filters between analog suspend mode and digital resume mode.

## State and Persistence
Persistent state includes global wakeup-mask values, per-bank `soc_priv` save data for GPIO EINT registers, runtime IRQ domains, and PMU regmap-backed retention control. Retention enable only increments an optional refcount; retention disable writes configured PMU registers when the final shared user resumes. `exynos_retention_init()` also writes retention release values during initialization so pads start in a usable state.

## Dependencies and Integration Points
The file integrates with gpiolib IRQ resource locking, irqdomain, chained IRQ handlers, the common Samsung bank model, Exynos PMU regmap helpers, and OF child nodes for wakeup EINT controllers. It depends on bank metadata such as `eint_offset`, `eint_con_offset`, `eint_mask_offset`, `eint_pend_offset`, `eint_fltcon_offset`, and `eint_num` supplied by SoC tables.

## Risks
Offset selection is subtle: normal Exynos banks use chip-wide EINT base offsets plus per-bank `eint_offset`, while ExynosAuto banks use per-bank offsets relative to `pctl_offset`. A wrong table entry can mask, ack, or configure the wrong interrupt. `eint_num` is static and accumulates during wakeup init, so multiple controller init order must be stable. Wakeup mask arrays are global; overlapping wakeup banks across controllers depend on correct bit numbering. Failing to call `gpiochip_unlock_as_irq()` on release would leave GPIO lines locked as IRQs.

## Test Signals
Tests should exercise IRQ type programming for all edge/level modes, GPIO-to-IRQ mapping, parent service-register dispatch, muxed wakeup IRQ demux, per-pin wakeup chained handlers, set-wake mask updates, suspend/resume of EINT con/filter/mask registers, GS101 three-register wake mask writes, and ExynosAuto v920 explicit-offset register paths. Runtime warnings about missing PMU syscon or missing IRQs are important failure signals.
