# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/init.c

## Purpose
This file initializes and updates APIC static calls. It lets the kernel route hot APIC operations through patched direct-call trampolines while still supporting runtime APIC driver installation and callback overrides from platform/hypervisor code.

## Important APIs, Types, And Functions
`DEFINE_APIC_CALL()` creates static-call slots for APIC callbacks such as `eoi`, `native_eoi`, `icr_read`, `icr_write`, `read`, IPI senders, `wait_icr_idle`, CPU wakeup, and `write`. `__x86_apic_override` holds optional callback overrides. `restore_override_callbacks()` reapplies overrides after driver switches. `update_static_calls()` patches static-call targets. `apic_setup_apic_calls()` initializes the default APIC static calls, and `apic_install_driver(driver)` switches the global APIC driver, handles `native_eoi`, applies overrides, updates static calls, and logs the selected backend.

## Control Flow
Early boot starts with a default `apic` pointer from the architecture probe file. `apic_setup_apic_calls()` initializes static calls once the default is usable. Later, APIC probe or forced disable paths call `apic_install_driver()`, which updates the global callback table and repatches all static calls so wrapper macros dispatch to the new backend.

## State And Persistence
The central state is the global `apic` pointer, the `__x86_apic_override` initdata object, and static-call patch state. Driver structs become read-only after init; overrides are applied before initdata goes away.

## Dependencies And Integration Points
It depends on Linux static calls and the APIC driver registry. Hypervisors or platform code can populate `__x86_apic_override`. All APIC users benefit indirectly because `apic_read()`, `apic_write()`, `apic_eoi()`, and IPI wrappers route through these patched callbacks.

## Risks
Static calls must be initialized before APIC wrappers are used in paths that assume non-null callbacks. Missing callbacks in a driver can become immediate crashes because wrappers intentionally avoid conditional calls for many operations. Preserving `native_eoi` is important for KVM/Hyper-V style EOI overrides.

## Test Signals
Boot should log `Static calls initialized` and `Switched APIC routing to: ...`. Validate APIC driver switches, hypervisor EOI overrides, IPI delivery, AP startup, and no null static-call faults during early boot.
