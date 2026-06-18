# sources/distributed-fs/ceph-client/include/linux/dpll.h

## Purpose
This header declares the kernel API for Digital Phase Locked Loop devices and pins. It lets hardware drivers register DPLL devices, register pins, expose mode/lock/frequency/phase operations over generic netlink, and attach DPLL pin handles to network devices.

## Important APIs, types, and functions
Provider operation tables are `struct dpll_device_ops` and `struct dpll_pin_ops`. Device ops cover mode get/set, supported modes, lock status, temperature, clock quality level, phase offset monitor, phase offset averaging, and frequency monitor state. Pin ops cover frequency, direction, state on parent pin or DPLL, priority, phase offset/adjustment, fractional frequency offset, measured frequency, embedded sync, and reference sync state.

Data types include `struct dpll_pin_frequency`, `struct dpll_pin_phase_adjust_range`, `struct dpll_pin_esync`, `struct dpll_pin_properties`, notifier info structs, and the optional `dpll_tracker` ref-tracking type. APIs include `dpll_device_get/put/register/unregister`, `dpll_pin_get/put/register/unregister`, `dpll_pin_on_pin_register/unregister`, `dpll_pin_fwnode_set()`, `dpll_pin_ref_sync_pair_add()`, device and pin change notification helpers, netdev pin-handle helpers, and DPLL notifier registration.

## Control flow, state, and persistence
DPLL and pin objects are reference-counted objects obtained by clock ID and driver ID, then registered with ops and private data. Pin properties persist labels, type, capabilities, supported frequencies, phase range, and granularity. Notifier events report created/deleted/changed state for devices and pins. Optional ref tracking records acquisition sites when configured.

## Dependencies and integration points
It depends on DPLL UAPI enums, device model, generic netlink, network devices, notifier chains, and rtnetlink. Drivers expose hardware clock synchronization control, while netdev integrations allow user space to correlate network ports with DPLL pins. When `CONFIG_DPLL` is disabled, netdev handle helpers are harmless stubs, but core declarations remain visible.

## Risks and test signals
Risks include mismatched get/put lifetimes, registering pins without stable properties, exposing unsupported ops, netlink extack omissions, and missing notifications after hardware state changes. Tests should cover registration/unregistration ordering, pin-on-pin topology, ref-sync pairs, extack errors for invalid mode/frequency/phase requests, netdev pin handle encoding, and notifier delivery.
