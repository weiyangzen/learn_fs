# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm44xx.c

## Purpose
`pm44xx.c` implements OMAP4+ PM initialization and suspend setup for OMAP4, OMAP5, and DRA7-class SoCs. It programs powerdomain targets, logic retention targets, static clockdomain wake dependencies, MPUSS initialization, CPU idle hook, and errata flags.

## Important APIs, Types, and Functions
Key exported functions are `omap4_pm_init_early()` and `omap4_pm_init()`, with global `pm44xx_errata`. Internal functions include `omap4_pm_suspend()`, `pwrdms_setup()`, `omap_default_idle()`, and `omap4plus_init_static_deps()`. Important data includes `struct power_state`, `struct static_dep_map`, `omap4_static_dep_map[]`, and `omap5_dra7_static_dep_map[]`.

## Control Flow
Early init sets errata bits for OMAP446x GICD ROM issue and disables CPU OSWR on OMAP5/DRA7. Main init rejects OMAP4430 ES1.0, creates per-powerdomain target state records, adds static wake dependencies, initializes MPUSS, allows clockdomain idle, registers generic suspend, and sets `arm_pm_idle`. Suspend saves current targets, programs requested targets, calls `omap4_enter_lowpower()` for the active CPU, checks previous states, then restores targets.

## State and Persistence Behavior
State includes `pm44xx_errata`, `cpu_suspend_state`, and `pwrst_list`. Hardware state includes powerdomain target/logic-retention registers, static clockdomain wake dependencies, MPUSS low-power setup, and CPU idle behavior.

## Dependencies and Integration Points
It depends on OMAP low-power CPU entry, MPUSS init, clockdomain/powerdomain frameworks, generic suspend core, and SoC detection. It integrates with `powerdomains44xx_data.c`, `powerdomains54xx_data.c`, and `powerdomains7xx_data.c`.

## Risks
Incorrect target selection can request unsupported power states; the code uses `pwrdm_get_valid_lp_state()` to avoid hangs. Static dependencies work around hardware issues; removing them can cause lockups or bad 32 kHz timer reads. Bootloader version matters for OMAP4 PM.

## Test Signals
Boot OMAP4/5/DRA7, confirm PM init succeeds, powerdomain setup logs no errors, static dependency creation succeeds, MPUSS init succeeds, idle hook works, and suspend reports domains reaching targets. Test CPU hotplug/suspend interactions on dual-core systems.
