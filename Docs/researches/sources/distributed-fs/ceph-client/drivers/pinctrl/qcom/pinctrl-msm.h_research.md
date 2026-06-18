# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.h

## Purpose
Defines the shared data contract between Qualcomm TLMM SoC description files and `pinctrl-msm.c`. It provides function declaration macros, pin group/register metadata structures, wake IRQ mapping types, SoC-level configuration, PM ops export, and the `msm_pinctrl_probe()` API.

## Important APIs, Types, And Data
Function macros such as `MSM_PIN_FUNCTION()`, `MSM_GPIO_PIN_FUNCTION()`, `APQ_PIN_FUNCTION()`, `IPQ_PIN_FUNCTION()`, and `QCA_PIN_FUNCTION()` build `struct pinfunction` entries from enum naming conventions and `<function>_groups` arrays. `struct msm_pingroup` embeds `struct pingroup`, lists mux function IDs, and describes register offsets plus bit positions for mux, pull, drive, I2C pull, open drain, eGPIO ownership, output enable, input/output values, interrupt enable/status/target/wakeup/raw/polarity/detection, and interrupt ack semantics. `struct msm_gpio_wakeirq_map` maps a GPIO to a wake-controller IRQ. `struct msm_pinctrl_soc_data` packages pins, functions, groups, GPIO count, pull behavior, tiles, reserved GPIOs, wake maps, dual-edge wake errata, GPIO function index, and eGPIO function index.

## Control Flow
There is no runtime control flow in the header. Its declarations shape how SoC files compile their static tables and how `pinctrl-msm.c` interprets them during probe and runtime operations. `msm_pinctrl_probe()` is the handoff point used by each TLMM platform driver's probe function. `msm_pinctrl_dev_pm_ops` lets SoC platform drivers attach the common sleep/default pinctrl PM behavior.

## State And Persistence
The header defines metadata, not state. Persistence emerges when these fields are instantiated in SoC files and consumed by the core to program TLMM registers. The bitfield layout in `struct msm_pingroup` constrains valid values; many fields are five-bit bit positions and must represent hardware bit indices correctly.

## Dependencies And Integration Points
Includes Linux PM/types and pinctrl definitions, forward-declares platform and pin descriptor types, and is included by Qualcomm TLMM variant drivers. It is the compatibility boundary for adding new SoCs: any new hardware capability needs a field here and corresponding support in the shared core.

## Risks
Because this header is a cross-driver ABI inside the kernel tree, semantic changes can break many SoC tables. Bitfield widths can truncate invalid large bit positions. The fallback rule for `intr_target_reg` means zero has special meaning, so SoCs with a real target register at offset zero would need careful handling. `gpio_func` and `egpio_func` are indices into each group's mux list, so mismatches between enum order, function arrays, and group mux arrays lead to wrong hardware programming.

## Test Signals
Build coverage across Qualcomm pinctrl drivers is the first signal. Runtime signals come from representative SoCs using optional features: separate interrupt target registers, wakeirq maps, no-keeper pulls, reserved GPIO masks, multi-tile mappings, and eGPIO. Static review should verify group arrays, enum values, and function macros remain aligned.
