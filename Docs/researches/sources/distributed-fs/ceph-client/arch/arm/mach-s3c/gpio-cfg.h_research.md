# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg.h

Purpose: Samsung legacy GPIO configuration constants and public helper declarations.

Important APIs/types/functions: defines GPIO input/output/special-function encodings, pull values, `S3C_GPIO_SFN()`, `samsung_gpio_is_cfg_special()`, and prototypes such as `s3c_gpio_cfgpin()`, `s3c_gpio_cfgpin_range()`, `s3c_gpio_cfgall_range()`, and `s3c_gpio_setpull()`.

Control flow: no implementation here; callers build encoded configs and invoke functions implemented in `gpio-samsung.c`.

State and persistence: config values map to hardware pin mux and pull registers.

Dependencies and integration points: used by board files and device setup for audio, I2C, SDHCI, keypad, etc.

Risks: encoding differences between 2-bit and 4-bit banks are hidden behind callbacks; wrong special-function number can reroute pins incorrectly.

Test signals: pinmux for every legacy peripheral and invalid config rejection.
