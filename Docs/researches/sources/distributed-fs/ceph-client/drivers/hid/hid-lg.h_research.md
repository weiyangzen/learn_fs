# sources/distributed-fs/ceph-client/drivers/hid/hid-lg.h

## Purpose

`hid-lg.h` is the shared internal header for the Logitech special HID driver and its force-feedback helper files. It provides the common per-device state shape and feature-gated initializer declarations.

## Important APIs, Types, And Functions

`struct lg_drv_data` contains `unsigned long quirks` and `void *device_props`. `quirks` is set by `hid-lg.c` device-table driver data and read by event, raw-event, mapping, and FF paths. `device_props` is intentionally untyped so `hid-lg4ff.c` can attach its `struct lg4ff_device_entry` without exposing wheel internals in the main header. The header declares `lgff_init()`, `lg2ff_init()`, and `lg3ff_init()` when their Kconfig symbols are enabled and provides inline stubs returning `-1` otherwise.

## Control Flow

The header has no standalone runtime flow. Compile-time Kconfig decides whether the main driver can call real FF initializers or receives a guaranteed failure from the stub, causing `lg_probe()` to unwind if a device table selects a disabled FF backend.

## State And Persistence Behavior

No state is allocated here. The struct layout is persistent ABI only inside this driver family: `hid-lg.c` allocates and frees `lg_drv_data`, while force-feedback modules read or extend it during probe and remove.

## Dependencies And Integration Points

The prototypes assume `struct hid_device` is visible from including C files. This header is included by `hid-lg.c`, `hid-lgff.c`, `hid-lg2ff.c`, `hid-lg3ff.c`, and `hid-lg4ff.c`, forming the compile-time contract among the Logitech driver pieces.

## Risks And Test Signals

The main risk is config mismatch: a product table entry using `LG_FF`, `LG_FF2`, or `LG_FF3` will fail probe if the corresponding Kconfig option is disabled. Build tests across Logitech FF config combinations and probe tests for FF-enabled devices are the primary signals.
