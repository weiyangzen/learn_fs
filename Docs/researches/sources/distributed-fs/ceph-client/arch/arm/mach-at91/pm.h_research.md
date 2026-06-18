# sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm.h

Purpose: declares the AT91 PM data contract shared between C setup code and the SRAM assembly suspend routine.

Important APIs/types/functions: defines memory-controller IDs `AT91_MEMCTRL_MC`, `AT91_MEMCTRL_SDRAMC`, and `AT91_MEMCTRL_DDRSDR`; suspend mode constants `AT91_PM_STANDBY`, `AT91_PM_ULP0`, `AT91_PM_ULP0_FAST`, `AT91_PM_ULP1`, and `AT91_PM_BACKUP`; and `struct at91_pm_data` with controller bases, PMC metadata, mode, memory-controller type, and masks.

Control flow: C code fills `struct at91_pm_data` during SoC-specific PM init and passes it to `at91_pm_suspend_in_sram()`. Assembly uses generated offsets from `pm_data-offsets.c` to read the same structure without C layout assumptions.

State and persistence: no executable state; the structure carries persistent mapped I/O addresses and selected mode across the final suspend transition.

Dependencies and integration: included by `pm.c`, `pm_suspend.S`, and the offset generator. It couples ARM C code with assembly layout and Atmel PMC/RAMC register conventions.

Risks: field order and type changes require regenerating assembly offsets; mode constants are array indexes into PM mode maps, so renumbering would break validation and fallback logic.

Test signals: build-time offset generation, successful assembly build, and suspend smoke tests for all memory-controller families.
