# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm_common.c

Purpose: Implements the common OMAP CM dispatcher, DT-based CM base mapping, low-level operation registration, and clock provider initialization.

Important APIs/types/functions: Maintains `cm_ll_data`, `cm_base`, and `cm2_base`. Implements `cm_split_idlest_reg()`, module ready/idle waits, module enable/disable, `omap_cm_xlate_clkctrl()`, `cm_register()`, `cm_unregister()`, `omap2_cm_base_init()`, and `omap_cm_init()`. Defines `omap_prcm_init_data` instances and `omap_cm_dt_match_table`.

Control flow: `omap2_cm_base_init()` scans matching DT nodes, ioremaps resources, populates `cm_base`/`cm2_base`, attaches node/memory data, and calls the SoC init hook when enough instances exist. `omap_cm_init()` later initializes clock providers for CM nodes unless flagged `CM_NO_CLOCKS`. Dispatcher functions validate callback presence and call the registered SoC implementation.

State and persistence: Global state includes registered low-level callback pointer and CM base mappings. Mapped MMIO persists for the life of the platform. DT node pointers are stored in init data during setup.

Dependencies: Uses Linux OF/address APIs, `cm2xxx.h`, `cm3xxx.h`, `cm33xx.h`, `cm44xx.h`, and `clock.h`.

Integration points: Central bridge between device tree CM nodes, TI clock providers, CM backends, and hwmod/clock callers.

Risks: `cm_register()` allows only one active low-level implementation, so multi-instance SoCs rely on one backend handling both CM1/CM2 after base setup. Resource mapping errors abort initialization. Missing callbacks produce warnings and `-EINVAL`.

Test signals: Device-tree boot should map the expected compatible nodes, initialize CM backends, and set up clock providers where appropriate. Absence of `WARN_ONCE` dispatcher warnings indicates correct backend registration.
