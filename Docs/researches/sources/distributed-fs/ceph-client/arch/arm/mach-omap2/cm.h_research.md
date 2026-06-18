# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm.h

Purpose: Declares the common OMAP Clock Management interface, timeout constants, CM base globals, low-level operation table, and dispatcher functions.

Important APIs/types/functions: Defines `MAX_MODULE_READY_TIME`, `MAX_MODULE_DISABLE_TIME`, `struct cm_ll_data`, globals `cm_base` and `cm2_base`, and dispatcher APIs `cm_split_idlest_reg()`, `omap_cm_wait_module_ready()`, `omap_cm_wait_module_idle()`, `omap_cm_module_enable()`, `omap_cm_module_disable()`, `omap_cm_xlate_clkctrl()`, `cm_register()`, `cm_unregister()`, `omap_cm_init()`, and `omap2_cm_base_init()`.

Control flow: SoC-specific CM backends fill `struct cm_ll_data` and call `cm_register()`. Shared hwmod/clock code calls the dispatchers without needing to know the SoC register model.

State and persistence: Declares global CM base mappings and a function-pointer interface; runtime storage is implemented in `cm_common.c`.

Dependencies: Includes TI clock provider definitions and `prcm-common.h` outside assembler context.

Integration points: This is the ABI between platform-independent OMAP CM users and per-SoC CM implementations.

Risks: Missing low-level function pointers return `-EINVAL` or `0` with warnings, so callers must handle unavailable operations. Timeout values are hardware-sensitive and too-short waits can cause false failures.

Test signals: Build coverage for each SoC backend and runtime absence of `WARN_ONCE` from missing CM callbacks.
