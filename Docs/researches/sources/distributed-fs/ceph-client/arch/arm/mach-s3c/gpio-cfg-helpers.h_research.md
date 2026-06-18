# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg-helpers.h

Purpose: small inline wrappers for Samsung GPIO configuration operations.

Important APIs/types/functions: `samsung_gpio_do_setcfg()` and `samsung_gpio_do_setpull()` call the active chip config callbacks.

Control flow: callers pass a `samsung_gpio_chip`, offset, and desired config/pull; helper dispatches through `chip->config`.

State and persistence: mutates GPIO configuration registers indirectly through callback implementations.

Dependencies and integration points: used by `gpio-samsung.c` public helpers and relies on `struct samsung_gpio_chip`/`struct samsung_gpio_cfg`.

Risks: assumes config callbacks are initialized; missing callbacks would crash or fail depending on caller setup.

Test signals: GPIO mux/pull changes through `s3c_gpio_cfgpin()` and `s3c_gpio_setpull()`.
