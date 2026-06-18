# sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra30.c

## Purpose

`regulators-tegra30.c` registers a Tegra30 regulator coupler for the CPU and core rails. It enforces Tegra30 CPU/core voltage spread and process-bin-specific core limits during DVFS, suspend, and reboot.

## Important APIs, Types, and Functions

`struct tegra_regulator_coupler` stores the generic coupler, core and CPU regulator devices, reboot/suspend notifiers, cached minimum voltages, and requested/current system mode flags. Coupler callbacks are `tegra30_regulator_attach()`, `tegra30_regulator_detach()`, and `tegra30_regulator_balance_voltage()`.

Key helpers are `tegra30_core_limit()`, `tegra30_core_cpu_limit()`, `tegra30_cpu_nominal_uV()`, `tegra30_core_nominal_uV()`, `tegra30_voltage_update()`, `tegra30_regulator_prepare_suspend()`, and `tegra30_regulator_prepare_reboot()`.

## Control Flow

At `arch_initcall`, the file checks for `nvidia,tegra30`, registers reboot and PM notifiers, and registers the coupler. Attach binds regulators identified by `nvidia,tegra-core-regulator` and `nvidia,tegra-cpu-regulator`.

Every balance request validates that the initiator is CPU or core and active state is `PM_SUSPEND_ON`, snapshots system mode flags, and calls `tegra30_voltage_update()`. That function obtains max spread and max step constraints with fallbacks, holds the core minimum until PMC core-domain sync, applies consumer constraints, computes CPU minimum from core spread and consumers, caches boot CPU voltage, calculates core minimum required for the current and target CPU voltage via `tegra30_core_cpu_limit()`, applies reboot/suspend overrides, then loops CPU and core voltages toward target values in bounded steps while maintaining spread limits.

## State and Persistence Behavior

The coupler caches the boot/current CPU voltage in `cpu_min_uV` and a boot-derived safe `core_min_uV` until safe core-domain sync. Reboot and suspend requested flags persist through notifier transitions and are observed during the next balance. Actual voltage changes persist in regulator hardware.

## Dependencies and Integration Points

It depends on OF machine compatibility, the regulator coupler framework, regulator constraints/consumer APIs, PM/reboot notifiers, Tegra fuse-derived `tegra_sku_info.cpu_speedo_id` and `soc_speedo_id`, and PMC core-domain sync state. Device tree must provide coupled regulator constraints and identifying properties.

## Risks and Edge Cases

Missing max-spread or max-step constraints fall back to 300 mV and 150 mV with error logs, which may be conservative but may not match board hardware. `tegra30_core_cpu_limit()` returns `-EINVAL` for CPU voltages >= 1.25 V, aborting updates. If no CPU consumers exist, the CPU rail is held no lower than current. Reboot/suspend notifiers set flags and force regulator syncs; failures propagate through notifier errno and may block transitions.

## Test Signals

Test voltage increase/decrease sequences with max-step limits, spread violation repair, speedo-ID branches for nominal voltages and core limits, missing DT constraint fallbacks, no-consumer CPU rail protection, suspend prepare/post paths, reboot restoration, and behavior before and after PMC core-domain sync.
