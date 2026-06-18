# sources/distributed-fs/ceph-client/drivers/usb/typec/retimer.h

## Purpose

`retimer.h` is the private header for the Type-C retimer class implementation. It defines the internal retimer object layout and type-check helper.

## Important APIs, Types, and Functions

`struct typec_retimer` embeds a `struct device` and stores the provider `typec_retimer_set_fn_t set` callback. `to_typec_retimer()` converts a device pointer to the wrapper. `typec_retimer_dev_type` and `is_typec_retimer()` identify retimer devices in class searches.

## Control Flow

There is no runtime flow in the header. It provides the object contract used by `retimer.c` and retimer provider/consumer code.

## State and Persistence Behavior

The structure holds runtime device-model state only. The callback remains valid while the provider device and module are referenced.

## Dependencies and Integration Points

It includes the public `linux/usb/typec_retimer.h` definitions and is included by `retimer.c`. It is the private bridge between public Type-C retimer APIs and the Linux device core representation.

## Risks and Test Signals

Risks are local coupling around `dev.type` checks and callback lifetime. Test signals are compile coverage of `is_typec_retimer()`, class lookup matching, set callback invocation, and release through `typec_retimer_dev_type`.
