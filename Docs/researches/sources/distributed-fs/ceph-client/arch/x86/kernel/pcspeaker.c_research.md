# sources/distributed-fs/ceph-client/arch/x86/kernel/pcspeaker.c

## Purpose
Registers the legacy PC speaker platform device so the generic `pcspkr` driver can bind on systems that still expose the PIT/speaker interface.

## APIs, Types, And Functions
The only function is `add_pcspkr()`, registered with `device_initcall()`. It creates a platform device named `pcspkr` with id `-1` and no resources.

## Control Flow
During device init, `platform_device_register_simple()` publishes the device. The function returns `PTR_ERR_OR_ZERO(pd)` so initcall failure is propagated only if allocation/registration fails.

## State And Persistence
Persistent state is the registered platform device in the driver core. This file has no private mutable state.

## Dependencies And Integration
Depends on Linux platform device registration and the separate PC speaker driver. It is part of x86 legacy device bring-up and assumes the actual driver handles hardware probing or absence.

## Risks And Test Signals
Risk is small: registering an unconditional legacy device can create noise on platforms without speaker hardware, but driver binding should handle it. Test signals are platform-device registration logs, presence of the `pcspkr` device, and successful beep/input driver behavior when hardware exists.
