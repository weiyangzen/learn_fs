# sources/distributed-fs/ceph-client/arch/x86/kernel/apm_32.c

## Purpose
This 32-bit x86 driver implements the legacy APM BIOS interface. It provides BIOS power management calls, a kernel APM daemon, `/proc/apm`, `/dev/apm_bios`, optional cpuidle integration, display blanking, power-off support, suspend/standby handling, and a large DMI quirk table for known broken firmware.

## Important APIs, Types, and Functions
The key per-open structure is `struct apm_user`, which tracks reader/writer privilege, event queue positions, pending suspend/standby acknowledgements, and wait state. BIOS calls use `struct apm_bios_call`, `apm_bios_call()`, `apm_bios_call_simple()`, and CPU0 helpers around the assembly entry points. Power operations include `apm_driver_version()`, `apm_get_event()`, `set_power_state()`, `set_system_power_state()`, `apm_get_power_status()`, `apm_engage_power_management()`, `suspend()`, `standby()`, and `apm_power_off()`.

User interfaces are `do_open()`, `do_read()`, `do_poll()`, `do_ioctl()`, `do_release()`, `proc_apm_show()`, and `apm_bios_fops`. Boot and module policy comes from `apm_setup()`, module parameters, `apm_init()`, and `apm_exit()`. Idle integration is implemented by `apm_cpu_idle()` and the `apm_idle_driver`.

## Control Flow
`apm_init()` applies DMI quirks, validates BIOS presence and 32-bit support, rejects unsafe ACPI/SMP combinations unless configured, sets GDT descriptors for BIOS segments on CPU0, creates `/proc/apm`, starts `kapmd`, registers the misc device, and optionally registers cpuidle. The `kapmd` thread pins itself to CPU0, negotiates APM version, enables/engages power management, installs `pm_power_off`, optionally hooks console blanking, then polls the BIOS once per second through `apm_mainloop()`. Events are pulled with `apm_get_event()`, decoded in `check_events()`, queued to interested users, and may drive `standby()` or `suspend()`.

Suspend saves device and syscore state, calls the BIOS, restores processor/syscore/device state, queues a normal resume event, and wakes user waiters. User ioctl paths either acknowledge pending BIOS events or generate user standby/suspend events, with privileged writers participating in vetoable suspend coordination.

## State and Persistence
Persistent driver state includes APM BIOS info in `apm_info`, global pending suspend/standby counters, waitqueues, the user linked list protected by `user_list_lock`, `apm_mutex`, idle thresholds, flags from boot/module parameters, and the `kapmd_task`. Each file descriptor owns a bounded circular event queue. Power management state also persists through global hooks such as `pm_power_off`, `console_blank_hook`, procfs, miscdevice registration, and cpuidle registration. The driver mutates firmware-facing state by enabling/engaging APM and may disengage on module exit.

## Dependencies and Integration Points
The file depends on 32-bit protected-mode APM assembly, GDT descriptor manipulation, CPU0 work execution, syscore and device PM, freezer-safe kthreads, procfs, miscdevice, poll/ioctl/read file operations, cpuidle, DMI, ACPI disable policy, reboot paths, branch speculation restriction, and IBT save/restore around firmware calls.

## Risks and Test Signals
The main risks are firmware hangs, long interrupt-off BIOS calls, unsafe SMP behavior, broken battery reporting, event queue overflow, suspend veto races, and stale global hooks on partial init/exit. Test signals include `/proc/apm` output, `/dev/apm_bios` reads and ioctls, boot messages for DMI quirks and connection version, successful CPU0-pinned BIOS calls, suspend/resume event delivery, power-off behavior, cpuidle registration when enabled, and clean unregister on module removal.
