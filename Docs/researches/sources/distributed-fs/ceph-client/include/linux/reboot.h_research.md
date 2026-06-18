# sources/distributed-fs/ceph-client/include/linux/reboot.h

## Purpose

`reboot.h` is the kernel-facing system restart, halt, power-off, emergency-restart, and sys-off handler interface. It centralizes reboot modes/types, notifier registration, architecture-specific machine hooks, ordered shutdown helpers, and hardware-protection emergency actions.

## Important APIs, Types, and Functions

System event constants are `SYS_DOWN`, `SYS_RESTART`, `SYS_HALT`, and `SYS_POWER_OFF`. `enum reboot_mode` covers cold, warm, hard, soft, and GPIO reboot modes; `enum reboot_type` covers architecture/firmware mechanisms such as keyboard controller, BIOS, ACPI, EFI, and CF9 variants. Global policy variables include `reboot_mode`, `panic_reboot_mode`, `reboot_type`, `reboot_default`, `reboot_cpu`, and `reboot_force`.

Notifier and restart APIs include `register_reboot_notifier()`, `unregister_reboot_notifier()`, `devm_register_reboot_notifier()`, `register_restart_handler()`, `unregister_restart_handler()`, and `do_kernel_restart()`. Machine hooks include `migrate_to_reboot_cpu()`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, `machine_shutdown()`, and `machine_crash_shutdown()`.

The sys-off API defines priorities, `enum sys_off_mode`, `struct sys_off_data`, `register_sys_off_handler()`, `unregister_sys_off_handler()`, devm variants, and platform power-off registration. Higher-level commands include `kernel_restart_prepare()`, `kernel_restart()`, `kernel_halt()`, `kernel_power_off()`, `kernel_can_power_off()`, `ctrl_alt_del()`, `orderly_poweroff()`, `orderly_reboot()`, `hw_protection_trigger()`, and `emergency_restart()`.

## Control Flow

Normal restart/poweroff flows notify registered clients, prepare devices and architecture state, optionally migrate to the selected reboot CPU, and call architecture machine operations or sys-off handlers by mode and priority. `SYS_OFF_MODE_*_PREPARE` handlers may sleep; final `POWER_OFF` and `RESTART` handlers must not.

`hw_protection_trigger()` funnels to `__hw_protection_trigger()` with a default action that can be configured to shutdown or reboot. `emergency_restart()` is the interrupt-safe path and includes architecture emergency restart support.

## State and Persistence Behavior

Runtime state includes global reboot policy variables, notifier chains, restart handlers, sys-off handler registrations, and platform power-off hooks. Persistent behavior is external: firmware, platform reset causes, reboot-mode storage, or hardware protection state may survive reset, but this header only declares the entry points.

## Dependencies and Integration Points

The header depends on `linux/notifier.h`, UAPI reboot constants, `struct device`, `pt_regs`, and architecture `asm/emergency-restart.h`. It integrates with driver core devm cleanup, architecture shutdown code, panic/crash paths, orderly userspace shutdown, PMIC/power controller drivers, and thermal/hardware protection code.

## Risks

Wrong priority or mode selection can run handlers in an unsafe context. Sleeping in final sys-off handlers is invalid. Reboot notifiers and restart handlers may execute after many subsystems are quiescing, so bus and allocation assumptions are fragile. Emergency restart bypasses orderly cleanup. Hardware-protection triggers must avoid delaying beyond the damage-prevention window.

## Test Signals

Validation includes registration ordering tests, devm cleanup, restart/poweroff mode coverage, panic reboot behavior, emergency restart smoke tests, hardware-protection forced timeout behavior, and platform tests proving final handlers actually reset or power off the system.
