# sources/distributed-fs/ceph-client/include/linux/arm_sdei.h

## Purpose
Declares Arm Software Delegated Exception Interface event registration, GHES integration, CPU masking, and architecture event-handler data structures.

## Important APIs, Types, And Functions
`sdei_event_callback` is the NMI-context callback type. APIs include `sdei_event_register()`, `sdei_event_unregister()`, `sdei_event_enable()`, `sdei_event_disable()`, `sdei_register_ghes()`, `sdei_unregister_ghes()`, `sdei_mask_local_cpu()`, `sdei_unmask_local_cpu()`, `acpi_sdei_init()`, `sdei_handler_abort()`, `sdei_event_handler()`, and `sdei_api_event_context()`. `struct sdei_registered_event` carries interrupted registers, callback, callback arg, event number, and priority.

## Control Flow, State, And Persistence
Firmware-described events are registered and enabled, then architecture entry code passes a `struct sdei_registered_event` back into `sdei_event_handler()` when an event arrives. Unregister can return `-EINPROGRESS` and must be retried. Registered events are driver-maintained state, with private events represented per CPU.

## Dependencies And Integration Points
Depends on UAPI SDEI definitions, ACPI GHES, and `asm/sdei.h` when enabled. Integrates firmware SDEI, GHES/RAS error handling, CPU hotplug/masking, NMI-context callbacks, and architecture exception entry.

## Risks And Test Signals
Callbacks run in NMI context, so sleeping, locking, or allocation mistakes are severe. Retry semantics for unregister are easy to miss. Tests should cover registration/enable/disable/unregister, GHES normal and critical callbacks, CPU mask/unmask, private per-CPU events, firmware absent stubs, and abort path behavior.
