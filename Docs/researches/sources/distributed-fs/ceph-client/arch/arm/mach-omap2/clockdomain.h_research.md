# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomain.h

Purpose: Declares the OMAP clockdomain model, capability flags, dependency structures, backend operation table, public clockdomain APIs, and SoC init hooks.

Important APIs/types/functions: Defines `struct clockdomain`, `struct clkdm_dep`, `struct clkdm_autodep`, and `struct clkdm_ops`. Capability macros include `CLKDM_CAN_FORCE_SLEEP`, `CLKDM_CAN_FORCE_WAKEUP`, `CLKDM_CAN_ENABLE_AUTO`, `CLKDM_CAN_DISABLE_AUTO`, `CLKDM_NO_AUTODEPS`, `CLKDM_ACTIVE_WITH_MPU`, `CLKDM_MISSING_IDLE_REPORTING`, `CLKDM_STANDBY_FORCE_WAKEUP`, and combined `CLKDM_CAN_HWSUP`, `CLKDM_CAN_SWSUP`, `CLKDM_CAN_HWSUP_SWSUP`. It declares all public operations implemented by `clockdomain.c` plus per-SoC init functions.

Control flow: Static data files instantiate `struct clockdomain` with names, powerdomain names, CM offsets, flags, dependency arrays, and optional dependency bits. The framework resolves name fields into pointers during registration and completion, then dispatches through `struct clkdm_ops` callbacks selected by the SoC.

State and persistence: `struct clockdomain` contains persistent static descriptors plus mutable runtime fields: `_flags`, dependency pointers in arrays, `usecount`, `forcewake_count`, `node`, and `context`. These fields bridge software reference counting and hardware CM register context.

Dependencies: Includes `powerdomain.h` and `clock.h`, and forward declares `struct omap_hwmod`. Consumers include SoC clockdomain data, CM backend implementations, clock code, hwmod code, and PM code.

Integration points: Exported operation-table symbols (`omap2_clkdm_operations`, `omap3_clkdm_operations`, `omap4_clkdm_operations`, `am33xx_clkdm_operations`, `am43xx_clkdm_operations`) are registered by SoC-specific init functions. Shared 24xx dependency arrays and `wkup_common_clkdm` are exported for OMAP2420/2430 data.

Risks: The header encodes hardware layout assumptions in small integer fields (`u8` partitions, `u16` offsets, `u8` dep bits). Incorrect flag combinations can make the generic framework call unsupported backend transitions. The deprecated autodep model remains part of the ABI for OMAP3.

Test signals: Compile coverage across OMAP2, OMAP3, AM33xx, AM43xx, OMAP4, OMAP5, DRA7xx, and TI81xx configurations verifies conditional declarations. Runtime validation should confirm each static descriptor has a valid powerdomain name and correct flags for its backend.
