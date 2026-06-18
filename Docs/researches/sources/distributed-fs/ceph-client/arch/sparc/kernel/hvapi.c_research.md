# sources/distributed-fs/ceph-client/arch/sparc/kernel/hvapi.c

## Purpose
`hvapi.c` manages negotiated sun4v hypervisor API group versions. It centralizes version registration, reference counting, lookup, and mandatory early registration for core groups.

## Important APIs, Types, and Functions
The core type is `struct api_info`, with group, major/minor, refcount, and `FLAG_PRE_API`. Public functions are `sun4v_hvapi_register()`, `sun4v_hvapi_unregister()`, `sun4v_hvapi_get()`, and boot-time `sun4v_hvapi_init()`. The static `api_table` lists supported HV groups.

## Control Flow and State
Registration looks up the group under `hvapi_lock`. If already referenced, only the same major version is accepted and the existing minor is returned. If unreferenced, it calls `sun4v_set_version()`, stores the actual minor on success, or emulates major 1 minor 0 for pre-API groups when the hypervisor reports bad trap/not supported. Successful registration increments refcount. Unregister decrements and when the refcount reaches zero calls `sun4v_set_version(group, 0, 0)` and clears stored versions. Init registers SUN4V 1.0 and CORE 1.6 or halts via PROM.

## Persistence and Dependencies
Persistent state is `api_table` and `hvapi_lock`. Dependencies are hypervisor version calls and PROM halt/printf for fatal early boot.

## Integration Points, Risks, and Test Signals
Integration includes IRQ negotiation, LDC/service channels, performance counters, reboot-data support, and other sun4v drivers. Risks include unbalanced unregister underflow, rejecting compatible minor-only differences due to major-only matching, and assumptions for pre-API fallback. Test signals are boot-time HVAPI registration, successful registration/unregistration by users, correct minor return values, and graceful failure on unsupported groups.
