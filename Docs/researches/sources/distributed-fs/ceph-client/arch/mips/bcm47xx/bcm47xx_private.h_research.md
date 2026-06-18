## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/bcm47xx_private.h

Purpose: private BCM47XX platform header for local function declarations and a consistent `pr_fmt()`.

Important APIs and definitions: defines `pr_fmt(fmt)` as `bcm47xx: ` when not already set. Declares init functions from local platform files: `bcm47xx_prom_highmem_init()`, `bcm47xx_buttons_register()`, `bcm47xx_leds_register()`, `bcm47xx_bus_setup()`, and `bcm47xx_workarounds()`.

Control flow: none.

State and persistence: none.

Dependencies and integration: included by local BCM47XX files such as `buttons.c` and `irq.c`. It keeps cross-file init prototypes out of public headers.

Risks: declarations must match implementations in other files; otherwise build/link failures or incorrect init attributes can occur. The header only declares a subset of local functions, so new cross-file calls require updates.

Test signals: compile coverage and log prefix consistency. Runtime signal is successful registration of bus/buttons/LEDs/workarounds through callers that use these declarations.
