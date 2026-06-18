# sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra20.c

## Purpose

`regulators-tegra20.c` registers a Tegra20-specific regulator coupler that keeps CPU, core, and RTC rails within hardware voltage relationships across DVFS, suspend, and reboot. It compensates for incomplete core-voltage scaling by holding safe minimum voltages until PMC core-domain state is synchronized.

## Important APIs, Types, and Functions

The file defines `struct tegra_regulator_coupler` with a generic `regulator_coupler`, attached core/CPU/RTC regulator devices, reboot and suspend notifiers, cached boot/min voltages, and requested/current reboot/suspend mode flags. The coupler callbacks are `tegra20_regulator_attach()`, `tegra20_regulator_detach()`, and `tegra20_regulator_balance_voltage()`.

Important helpers include `tegra20_core_limit()`, `tegra20_core_rtc_max_spread()`, `tegra20_cpu_nominal_uV()`, `tegra20_core_nominal_uV()`, `tegra20_core_rtc_update()`, `tegra20_core_voltage_update()`, `tegra20_cpu_voltage_update()`, and suspend/reboot preparation notifiers.

## Control Flow

At `arch_initcall`, the file checks `of_machine_is_compatible("nvidia,tegra20")`, registers reboot and PM notifiers, and registers the coupler. Regulator attach identifies rails by DT boolean properties `nvidia,tegra-core-regulator`, `nvidia,tegra-rtc-regulator`, and `nvidia,tegra-cpu-regulator`.

On balance, the coupler verifies the regulator and `PM_SUSPEND_ON` state, snapshots requested reboot/suspend flags, and either updates CPU then core/RTC or updates core/RTC based on the initiating rail. CPU changes raise core/RTC before CPU when CPU voltage rises, and lower CPU before core/RTC when CPU voltage falls. Core/RTC updates step both rails while respecting RTC-core max spread, CPU-to-core/RTC minimum offset, regulator constraints, consumer constraints, suspend nominal voltages, and reboot restoration of boot CPU voltage.

## State and Persistence Behavior

The coupler caches `core_min_uV` from boot or board constraints until `tegra_pmc_core_domain_state_synced()` allows full scaling. It caches `cpu_min_uV` boot voltage for reboot restoration. Reboot/suspend flags are communicated through `WRITE_ONCE`/`READ_ONCE`. Hardware regulator voltages persist until changed by the regulator framework, suspend, reboot, or bootloader.

## Dependencies and Integration Points

It depends on the regulator coupler internals, regulator constraints/consumer APIs, PM/reboot notifier chains, OF machine compatibility, `tegra_sku_info.soc_speedo_id`, and `tegra_pmc_core_domain_state_synced()`. It requires DT coupling metadata including max-spread entries and rail-identifying boolean properties.

## Risks and Edge Cases

The RTC rail cannot be changed directly; attempts return `-EPERM`. Missing max-spread falls back to 150 mV with an error. If no CPU consumers exist, CPU voltage is held at current value to avoid undervolting a running CPU at unknown frequency. The code logs existing constraint violations but proceeds to calculate a safe sequence. Notifier registration warnings do not abort coupler registration.

## Test Signals

Test attach/detach for all three rails, CPU voltage raise/lower sequencing, core-only updates, missing max-spread fallback, suspend prepare/post suspend nominal voltage transitions, reboot boot-voltage restoration, unsynced versus synced PMC core-domain behavior, regulator constraint failure injection, and no-consumer CPU rail behavior.
