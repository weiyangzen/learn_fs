# sources/distributed-fs/ceph-client/kernel/reboot.c

## Purpose
`reboot.c` implements the generic kernel reboot, halt, poweroff, orderly shutdown, emergency restart, sys-off handler, reboot syscall, reboot tunable, and hardware-protection shutdown logic. Architecture code supplies the final machine-specific restart/halt/poweroff operations, while this file coordinates notifiers, device shutdown, syscore shutdown, CPU migration, usermode helper shutdown, and user/kernel control surfaces.

## Important APIs, Types, and Functions
- Restart/halt/poweroff APIs: `emergency_restart()`, `kernel_restart_prepare()`, `kernel_restart()`, `kernel_halt()`, `kernel_power_off()`, `do_kernel_restart()`, `do_kernel_power_off()`, and `kernel_can_power_off()`.
- Notifier APIs: `register_reboot_notifier()`, `unregister_reboot_notifier()`, `devm_register_reboot_notifier()`, `register_restart_handler()`, and `unregister_restart_handler()`.
- Sys-off APIs: `struct sys_off_handler`, `register_sys_off_handler()`, `unregister_sys_off_handler()`, `devm_register_sys_off_handler()`, `devm_register_power_off_handler()`, `devm_register_restart_handler()`, `register_platform_power_off()`, and `unregister_platform_power_off()`.
- User entry points: `SYSCALL_DEFINE4(reboot)`, `ctrl_alt_del()`, `orderly_poweroff()`, and `orderly_reboot()`.
- Hardware protection: `__hw_protection_trigger()`, `hw_failure_emergency_schedule()`, `hw_failure_emergency_action_func()`, and `hw_protection_setup()`.
- Configuration surfaces: `reboot_setup()` parses `reboot=`, sysfs under `/sys/kernel/reboot` exposes mode/type/force/cpu/hw_protection, and sysctls expose `kernel.poweroff_cmd` and `kernel.ctrl-alt-del`.

## Control Flow
Emergency restart is the shortest path: dump emergency kmsg, set `SYSTEM_RESTART`, and call `machine_emergency_restart()` without normal shutdown. Clean restart calls reboot notifiers, sets system state, disables usermode helpers, shuts down devices, runs restart-prepare handlers, migrates to the reboot CPU, shuts down syscore, dumps shutdown kmsg, and calls `machine_restart()`.

Halt and poweroff share `kernel_shutdown_prepare()` for reboot notifiers, system state, usermodehelper disable, and device shutdown. Poweroff additionally runs power-off prepare handlers and calls `machine_power_off()`, which is expected to call `do_kernel_power_off()` if needed. The generic poweroff handler chain can include new sys-off handlers and a temporary legacy `pm_power_off` adapter.

The reboot syscall checks namespace capability, validates magic values, delegates child pid namespaces to `reboot_pid_ns()`, falls back from poweroff to halt when no poweroff handler exists, serializes transitions with `system_transition_mutex`, and dispatches restart, CAD toggles, halt, poweroff, `RESTART2`, kexec, or hibernation. Orderly reboot/poweroff schedule work that invokes `/sbin/reboot` or configurable `/sbin/poweroff`; forced paths call `emergency_sync()` and then kernel restart/poweroff if usermode execution fails.

Hardware protection triggers only once via an atomic guard, logs the reason, schedules a delayed forced action, and starts orderly reboot or forced orderly poweroff. If the delayed backup fires, it tries kernel restart/poweroff and finally `emergency_restart()`.

## State and Persistence
Important state includes `C_A_D`, `cad_pid`, `reboot_mode`, `panic_reboot_mode`, `reboot_default`, `reboot_cpu`, `reboot_type`, `reboot_force`, `poweroff_fallback_to_halt`, `pm_power_off`, notifier chains, sys-off handler allocations, `system_transition_mutex`, `poweroff_cmd`, `poweroff_force`, hardware-protection action, and delayed work. Values are in memory; boot parameters and sysfs/sysctl writes configure live state but are not persistent across reboot.

## Dependencies and Integration Points
The file integrates with architecture machine operations, kexec, hibernation, pid namespaces, capabilities, device core shutdown, syscore operations, kmsg dumpers, usermode helper execution, workqueues, notifier chains, devres, sysfs, sysctl, CPU hotplug/affinity, and platform/driver poweroff or restart providers.

## Risks
System transition paths are destructive by design. Risks include handlers registered at incorrect priority, legacy `pm_power_off` coexistence, poweroff fallback to halt surprising callers, missed serialization around concurrent transitions, CPU migration to an offline or unsuitable reboot CPU, usermode helper failure in orderly paths, and forced hardware-protection actions preempting normal shutdown. Sys-off platform priority permits only one platform handler; misuse returns `-EBUSY`.

## Test Signals
Signals include syscall return codes for invalid magic/capability/commands, sysfs/sysctl read/write behavior, notifier registration/unregistration and priority ordering, orderly shutdown fallback logs, kmsg dump reasons, `Power down`/`Restarting system`/halt emergency messages, hardware-protection delayed work behavior, and architecture-level confirmation that machine restart/halt/poweroff callbacks are invoked.
