# sources/distributed-fs/ceph-client/drivers/parisc/power.c

## Purpose
This file implements the HP PA-RISC soft power switch driver. It enables the firmware soft-power facility, polls the power button in a kernel thread, exposes a sysctl to disable handling, prints LCD feedback, requests orderly shutdown, and re-enables firmware power-button behavior on panic.

## Important APIs, Types, And Functions
Important functions are `process_shutdown()`, `kpowerswd()`, `parisc_panic_event()`, `qemu_power_off()`, `power_init()`, and `power_exit()`. Sysctl registration is handled by `init_power_sysctl()` and `power_sysctl_table`, exposing `kernel/soft-power`. The driver uses architecture-specific diagnostic-register access macros for Gecko-style machines.

## Control Flow
`init_power_sysctl()` registers the sysctl at arch init. `power_init()` asks PDC for the soft-power register, enables the firmware soft-power button, reports the detected mode, registers a QEMU sys-off handler when appropriate, starts `kpowerswd()` when polling is useful, and registers a panic notifier. The polling thread sleeps according to `pwrsw_enabled`, reads either the soft-power MMIO bit or Gecko diagnostic register bit, resets an in-progress shutdown if released early, or calls `process_shutdown()` while held. After a configured hold interval, `process_shutdown()` writes an LCD message and sends `SIGINT` to CAD/init, falling back to `machine_power_off()` if signaling fails.

## State And Persistence
Persistent runtime state is `shutdown_timer`, `power_task`, and the sysctl-backed `pwrsw_enabled`. Hardware state includes PDC soft-power enablement and, on QEMU, a firmware power-off MMIO write. Panic handling calls `pdc_soft_power_button_panic(0)` to re-enable direct switch-off behavior.

## Dependencies And Integration Points
The file depends on PDC soft-power calls, PA-RISC GSC/DIAG register access, kernel threads, sysctl, panic notifier chain, reboot/sys-off framework, CAD signal delivery, and `lcd_print()` from the chassis display driver.

## Risks
Polling rather than interrupts means button response depends on scheduler progress and `HZ`. The Gecko diagnostic bit may not reset on some machines, noted by the code. `power_exit()` calls `kthread_stop(power_task)` without a visible NULL guard, but this is mostly relevant to modular unload. The sysctl path in the comment differs from the registered name: the table registers `soft-power` under `kernel`.

## Test Signals
Signals include PDC detection logs, sysctl presence and enable/disable behavior, hold-to-shutdown timing, abort message on early release, LCD shutdown message, CAD signal delivery, QEMU power-off behavior, and panic-path re-enablement. Tests should cover Gecko and MMIO-register machines separately.
