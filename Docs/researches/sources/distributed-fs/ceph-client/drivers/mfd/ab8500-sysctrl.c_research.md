# sources/distributed-fs/ceph-client/drivers/mfd/ab8500-sysctrl.c

Purpose: AB8500 system-control child driver. It exposes read/write helpers for AB8500 system-control register banks and installs a platform power-off implementation that can reboot into charge-only mode when a charger and known battery are present.

Important APIs, types, and functions: exported `ab8500_sysctrl_read()` and `ab8500_sysctrl_write()` validate system-control banks and call ABX500 register helpers. `ab8500_power_off()` checks power supplies and writes `AB8500_STW4500CTRL1` shutdown/reset bits. `ab8500_sysctrl_probe()` sets the global device pointer and conditionally assigns `pm_power_off`.

Control flow: platform probe records `sysctrl_dev` and installs `pm_power_off` if empty. Poweroff checks AC/USB supply online state, checks battery technology, calls `machine_restart("charging")` when appropriate, otherwise blocks signals and sets software-off bits. Remove clears the global pointer and uninstalls the poweroff hook if it still owns it.

State and persistence: `sysctrl_dev` is global singleton state. Register writes persist to AB8500 hardware and may power off or reset the PMIC/system.

Dependencies and integration: depends on ABX500 core register ops, AB8500 sysctrl register definitions, platform bus, power_supply class, reboot/poweroff hooks, and signal-mask helpers.

Risks: singleton state supports only one sysctrl instance; `pm_power_off` is a global legacy hook and can conflict with other poweroff providers; poweroff depends on specific power-supply names (`ab8500_ac`, `ab8500_usb`, `ab8500_btemp`); exported helpers return `-EPROBE_DEFER` until probe.

Test signals: probe as AB8500 child, call exported read/write before and after probe, verify invalid-bank rejection, simulate charger/battery states for poweroff path, confirm charge-only restart, and test remove restores `pm_power_off`.
