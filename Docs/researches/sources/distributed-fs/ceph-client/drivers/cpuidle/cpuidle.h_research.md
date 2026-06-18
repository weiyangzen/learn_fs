<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.h

## Purpose

`cpuidle.h` is the private header for the cpuidle implementation. It exposes shared globals and internal helpers across the core, driver registration, governor, sysfs, poll-state, and optional coupled-idle files.

## Important APIs, Types, And Functions

It declares `param_governor`, `cpuidle_curr_governor`, `cpuidle_prev_governor`, `cpuidle_governors`, `cpuidle_detected_devices`, `cpuidle_lock`, and `cpuidle_driver_lock`. It also declares core helpers such as `cpuidle_enter_state()`, idle-handler install/uninstall, governor lookup/switching, and sysfs add/remove functions. Under `CONFIG_ARCH_NEEDS_CPU_IDLE_COUPLED`, it declares coupled-idle validation, registration, unregister, and entry functions; otherwise it provides stubs.

## Control Flow

There is no runtime control flow in the header, but the inline coupled stubs are important: non-coupled builds always report states as not coupled and return failure if the coupled entry path is accidentally requested.

## State And Persistence Behavior

The header does not allocate state itself; it defines the internal visibility boundary for persistent core lists, locks, governor pointers, and coupled-idle behavior.

## Dependencies And Integration Points

It depends on the public cpuidle types and is included by cpuidle core, driver, governor, sysfs, and architecture/platform idle code using private interfaces.

## Risks And Test Signals

Risks include leaking internal APIs outside `drivers/cpuidle`, mismatched coupled stubs masking build-time assumptions, and lock-order changes affecting all users. Test signals are compile coverage across coupled and non-coupled configurations, governor switching, sysfs registration, and coupled platform boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.h -->
