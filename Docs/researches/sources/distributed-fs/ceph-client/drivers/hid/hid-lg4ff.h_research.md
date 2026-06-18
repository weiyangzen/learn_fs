# sources/distributed-fs/ceph-client/drivers/hid/hid-lg4ff.h

## Purpose

`hid-lg4ff.h` is the compile-time interface between the main Logitech HID driver and the Logitech wheel force-feedback module.

## Important APIs, Types, And Functions

When `CONFIG_LOGIWHEELS_FF` is enabled, it declares the module parameter storage `lg4ff_no_autoswitch` and four functions: `lg4ff_adjust_input_event()`, `lg4ff_raw_event()`, `lg4ff_init()`, and `lg4ff_deinit()`. The adjustment functions receive `struct lg_drv_data *` so they can access FF4 wheel properties stored by the initializer. When the config is disabled, inline stubs return neutral values: event/raw adjustments return `0`, init/deinit return `-1`.

## Control Flow

The header has no runtime flow. `hid-lg.c` uses it to compile the same delegation calls regardless of Kconfig. With FF4 enabled, wheel products selected by `LG_FF4` enter the real module. With FF4 disabled, a selected FF4 product will fail probe after `lg4ff_init()` returns `-1`.

## State And Persistence Behavior

No state is owned here. The only declared state is the external `lg4ff_no_autoswitch`, which is defined and exposed as a module parameter in `hid-lg.c` when FF4 is built.

## Dependencies And Integration Points

The header assumes the including file has the HID and Logitech private types visible. It is included by both `hid-lg.c` and `hid-lg4ff.c` and is the boundary that allows FF4 support to be optional.

## Risks And Test Signals

Risks are limited to Kconfig behavior and prototype drift. Build with and without `CONFIG_LOGIWHEELS_FF`, then probe an `LG_FF4` wheel to verify enabled builds initialize and disabled builds fail predictably rather than linking missing symbols.
