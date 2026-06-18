# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.c

Purpose: legacy Samsung S3C64xx GPIO controller implementation for non-DT platforms.

Important APIs/types/functions: implements config/pull helpers for 2-bit and 4-bit banks, gpiolib direction/get/set callbacks, chip registration helpers, IRQ mapping helpers, S3C64xx bank tables, `samsung_gpiolib_init()`, and exported APIs `s3c_gpio_cfgpin()`, `s3c_gpio_cfgpin_range()`, `s3c_gpio_cfgall_range()`, and `s3c_gpio_setpull()`.

Control flow: `core_initcall` skips if DT is populated, otherwise initializes config defaults and registers S3C64xx 2-bit, 4-bit, and split 4-bit banks. Runtime GPIO operations lock per chip, update data/control/pull registers, and optionally track global pin-to-chip mappings for config helpers.

State and persistence: static bank arrays describe every GPIO bank. Optional `s3c_gpios[]` tracks pin ownership. Hardware state lives in bank control/data/pull registers and sleep/PM hooks.

Dependencies and integration points: integrates Linux gpiolib, S3C IRQ constants, CPU ID helpers, Samsung PM GPIO code, and legacy board/platform device setup.

Risks: skipped on DT systems, so legacy callers must not expect it there. Register layouts vary by bank; split 4-bit base offset handling is fragile. `BUG_ON` in tracking can panic on bad ranges. PM hook absence logs errors but does not stop registration.

Test signals: non-DT gpiochip registration for all banks, direction/input/output, pull and special-function config, GPIO-to-IRQ for GPN/GPL/GPM, PM save/restore, and no registration when DT is populated.
