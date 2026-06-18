# sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_data-offsets.c

Purpose: emits assembler constants for fields inside `struct at91_pm_data`.

Important APIs/types/functions: `main()` uses `DEFINE()` and `OFFSET()` for `PM_DATA_PMC`, `PM_DATA_RAMC0`, `PM_DATA_RAMC1`, `PM_DATA_RAMC_PHY`, `PM_DATA_MEMCTRL`, `PM_DATA_MODE`, `PM_DATA_PMC_MCKR_OFFSET`, `PM_DATA_PMC_VERSION`, `PM_DATA_PMC_MCKS`, `PM_DATA_PMC_MCKR`, `PM_DATA_PMC_PLLA`, `PM_DATA_PMC_MCKR_CSS`, `PM_DATA_PMC_MCKR_PRES`, `PM_DATA_PMC_MCKR_MDIV`, `PM_DATA_PMC_MCKR_CSS_OFFSET`, and `PM_DATA_PMC_MCKR_PRES_OFFSET`.

Control flow: compiled as a kernel offsets helper, not as runtime code. The generated constants are consumed by `pm_suspend.S`.

State and persistence: no runtime state. Its only persistent output is generated assembly offset metadata during the build.

Dependencies and integration: includes `pm.h` and `asm-offsets.h`; any `struct at91_pm_data` layout change is reflected here for assembly users.

Risks: missing offsets cause assembly to use stale or hardcoded layout assumptions. Incorrect type widths in `pm.h` would surface as broken suspend behavior rather than a normal C type error inside the assembly path.

Test signals: successful kernel build and inspection of generated offsets; suspend tests catch semantic mismatches.
