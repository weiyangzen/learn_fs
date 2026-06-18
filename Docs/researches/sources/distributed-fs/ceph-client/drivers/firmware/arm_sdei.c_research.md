# sources/distributed-fs/ceph-client/drivers/firmware/arm_sdei.c

## Purpose
This file implements the ARM Software Delegated Exception Interface core driver. It discovers an SDEI firmware conduit, exposes event registration/enabling APIs, handles CPU hotplug and power-management masking, integrates GHES notifications, and preserves event registrations across suspend, hibernate, reboot, and panic paths.

## Important APIs, Types, And Functions
`sdei_firmware_call` abstracts the SMCCC SMC/HVC conduit selected by `sdei_get_conduit()`. `struct sdei_event` tracks an event number, priority, type, and per-event registered callback argument storage. Shared events use a single `struct sdei_registered_event`; private events allocate one per CPU. `sdei_events_lock` serializes public API mutation; `sdei_list_lock` protects the event list and reregister/reenable flags.

Public kernel APIs include `sdei_event_register()`, `sdei_event_unregister()`, `sdei_event_enable()`, `sdei_event_disable()`, `sdei_mask_local_cpu()`, `sdei_unmask_local_cpu()`, `sdei_register_ghes()`, `sdei_unregister_ghes()`, `sdei_event_handler()`, and `sdei_handler_abort()`. Low-level firmware calls funnel through `invoke_sdei_fn()`, which converts SDEI status codes to Linux errno and returns `-EIO` when the interface is disabled.

## Control Flow, State, And Persistence
Probe chooses HVC/SMC from DT `method` or ACPI PSCI policy, reads the SDEI version, resets the platform, obtains the arch entry point, and registers CPU PM, reboot, and CPU hotplug callbacks. Event registration creates state, queries event info, registers either once for shared events or on all CPUs for private events, then marks `reregister`. Enabling similarly calls shared firmware once or cross-calls all CPUs and marks `reenable`.

Persistence is explicit in the `reregister` and `reenable` flags. Hibernate freeze unregisters private hotplug state and shared events without destroying their records; thaw/restore reregister and re-enable saved shared events and re-add CPU hotplug for private events. Reboot and panic paths mask CPUs and reset firmware. `sdei_handler_abort()` attempts to finish active normal/critical events before a crash kernel takes over.

## Dependencies And Integration Points
The file depends on SMCCC, CPU hotplug, CPU PM notifiers, ACPI SDEI table discovery, OF platform matching, GHES, per-CPU storage, and arch-provided SDEI entry/abort helpers. It registers as an `arch_initcall` platform driver with `arm,sdei-1.0`; ACPI creates a platform device from `ACPI_SIG_SDEI`.

## Risks And Test Signals
Risk concentrates around concurrency and firmware state drift: list mutation must respect mutex-then-spinlock ordering, private event registration must be symmetric across CPUs, and suspend/restore must not leave stale firmware registrations. Test signals include conduit selection, version rejection, shared/private register-enable-disable-unregister lifecycles, hotplug down/up reregistration, hibernate freeze/thaw, GHES priority callback selection, and disabled-interface `-EIO` behavior.
