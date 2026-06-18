<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypervisor.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/hypervisor.h

## Purpose
This header exposes ARM Xen early boot globals and initialization hooks.

## Important APIs, Types, And Functions
- `HYPERVISOR_shared_info` points to Xen's shared info page.
- `xen_start_info` points to Xen start information.
- `xen_early_init()` is declared under `CONFIG_XEN` and stubbed otherwise.
- CPU hotplug registration hooks are empty inline functions when `CONFIG_HOTPLUG_CPU` is enabled.

## Control Flow
ARM Xen boot code calls `xen_early_init()` during early initialization to establish Xen shared state. CPU hotplug paths may call the arch register/unregister hooks, but this architecture implementation is a no-op in the header.

## State And Persistence
Persistent state is the shared-info and start-info pointers maintained by the Xen ARM implementation. The header itself stores no data.

## Dependencies And Integration Points
It depends on Linux init annotations and Xen architecture code. Consumers include early boot, event handling, time, and memory setup paths needing shared Xen data.

## Risks And Edge Cases
Non-Xen builds get a no-op early init, so callers must not assume Xen state exists. Shared info pointers must be initialized before consumers dereference them.

## Test Signals
Signals include early boot detecting Xen, valid shared-info mapping, safe non-Xen stub behavior, and CPU hotplug paths building cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypervisor.h -->
