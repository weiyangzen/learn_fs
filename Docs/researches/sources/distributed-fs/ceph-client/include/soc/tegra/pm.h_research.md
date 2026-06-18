# sources/distributed-fs/ceph-client/include/soc/tegra/pm.h

## Purpose

`pm.h` declares Tegra low-level suspend modes and ARM power-management hooks for LP2, LP1, LP0, resume, CPU parking, and suspend initialization.

## Important APIs, Types, and Functions

`enum tegra_suspend_mode` defines `TEGRA_SUSPEND_NONE`, `TEGRA_SUSPEND_LP2`, `TEGRA_SUSPEND_LP1`, `TEGRA_SUSPEND_LP0`, `TEGRA_MAX_SUSPEND_MODE`, and `TEGRA_SUSPEND_NOT_READY`. Enabled sleep builds declare `tegra_pm_validate_suspend_mode()`, `tegra_resume()`, `tegra30_pm_secondary_cpu_suspend()`, `tegra_pm_clear_cpu_in_lp2()`, `tegra_pm_set_cpu_in_lp2()`, `tegra_pm_enter_lp2()`, `tegra_pm_park_secondary_cpu()`, and `tegra_pm_init_suspend()`. Disabled builds provide no-op or `-ENOTSUPP` stubs.

## Control Flow

Suspend code validates mode, initializes suspend support, parks or suspends secondary CPUs, marks LP2 state, enters low-power mode, and returns through the low-level resume path.

## State and Persistence

The header defines no storage. Runtime state is in platform PM bookkeeping, CPU state, and hardware.

## Dependencies and Integration Points

It depends on Linux errno and integrates with PMC, flow controller, CPU hotplug, cpuidle, suspend/resume assembly, and platform PM code.

## Risks

Bad mode validation or CPU parking can hang resume. Disabled stubs can make unsupported suspend modes appear harmless while real PM functionality is absent.

## Test Signals

Test enabled/disabled builds, suspend mode validation, LP2 entry/exit, secondary CPU suspend, CPU parking, and platform suspend/resume for supported low-power modes.
