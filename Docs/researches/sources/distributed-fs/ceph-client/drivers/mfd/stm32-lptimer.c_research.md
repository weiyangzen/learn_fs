# sources/distributed-fs/ceph-client/drivers/mfd/stm32-lptimer.c

## Purpose
`stm32-lptimer.c` is the MFD parent for STM32 low-power timers. It maps timer registers through a clocked regmap, detects hardware capabilities, and populates child devices.

## Important APIs, Types, and Functions
`stm32_lptimer_regmap_cfg` configures 32-bit MMIO register access. `stm32_lptimer_detect_encoder()` probes legacy encoder support by writing and reading the encoder bit. `stm32_lptimer_detect_hwcfgr()` reads version and HW configuration registers for encoder and capture/compare channel count. `stm32_lptimer_probe()` performs resource, regmap, clock, capability, and child setup.

## Control Flow
Probe allocates `struct stm32_lptimer`, maps the MMIO resource, initializes a regmap gated by the `"mux"` clock, gets the timer clock, detects capability from `HWCFGR` or the legacy write/readback fallback, stores driver data, and calls `devm_of_platform_populate()`.

## State and Persistence
State is the parent `stm32_lptimer` structure: regmap, clock, version, encoder support, and channel count. Hardware registers are volatile and no explicit suspend cache is provided here.

## Dependencies and Integration Points
It depends on STM32 LPTIM register definitions, platform resources, regmap MMIO with clock support, and child drivers under the low-power timer DT node.

## Risks and Edge Cases
Legacy detection writes `STM32_LPTIM_ENC`, so the timer should be inactive or safe to probe. Missing or unreadable HWCFGR falls back only when the first HWCFGR value is zero. Clock name `"mux"` must match device tree/clock provider expectations.

## Test Signals
Probe on legacy and HWCFGR-capable timers, correct encoder detection, channel-count detection, child population, and failures from MMIO, regmap, or clock acquisition.
