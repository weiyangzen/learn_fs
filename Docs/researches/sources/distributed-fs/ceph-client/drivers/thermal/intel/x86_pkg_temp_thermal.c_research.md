# sources/distributed-fs/ceph-client/drivers/thermal/intel/x86_pkg_temp_thermal.c

## Purpose

`x86_pkg_temp_thermal.c` registers per-package/die thermal zones using package temperature MSRs and handles package threshold interrupts through the global Intel thermal interrupt callback mechanism.

## Important APIs, Types, and Functions

`struct zone_device` stores target CPU, delayed work state, saved package interrupt MSR, thermal zone, and package CPU mask. `sys_get_curr_temp()` uses `intel_tcc_get_temp(..., pkg=true)`. `sys_set_trip_temp()` programs threshold 0/1 in `MSR_IA32_PACKAGE_THERM_INTERRUPT`. `pkg_thermal_notify()` is assigned to `platform_thermal_package_notify`. CPU hotplug callbacks create/remove package zones.

## Control Flow

Module init matches Intel PTS, allocates a zone pointer array sized by packages times dies, registers CPU hotplug state, and installs package notification callbacks. First CPU in a package creates an `x86_pkg_temp` zone with writable passive trips based on CPUID threshold count and saved MSR thresholds. Package threshold interrupt disables threshold interrupts and schedules delayed work. Work clears sticky status, reenables valid threshold interrupts, and updates the zone. CPU offline migrates work target or unregisters/frees the zone for the last CPU.

## State and Persistence Behavior

Global `zones[]`, debug counters, and callback pointers persist while loaded. Each zone saves the original package interrupt MSR and restores it when the last CPU in the package exits. Delayed work state is protected by raw spinlock and zone mutex.

## Dependencies and Integration Points

It depends on Intel TCC library, CPU hotplug, topology logical die IDs, thermal core, debugfs, MSR threshold definitions, and `thermal_interrupt.h` callback hooks.

## Risks and Test Signals

Risks include hotplug/work/interrupt races, callback pointer synchronization, package/die indexing, threshold unit conversion against TjMax, interrupt remaining disabled if work migration fails, and debugfs-only observability for interrupt/work counts. Test signals include CPU hotplug package creation/migration/removal, trip set/clear MSR writes, threshold interrupt rate control, work cancellation on offline, MSR restore on last CPU, and module unload callback cleanup.
