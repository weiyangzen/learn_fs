# sources/distributed-fs/ceph-client/drivers/input/mouse/atarimouse.c

## Purpose

`atarimouse.c` is the Linux/m68k Atari mouse input driver. Low-level ACIA keyboard/mouse handling lives in Atari architecture code; this driver registers an input device and installs a callback hook that converts IKBD relative mouse packets into standard Linux relative motion and button events.

## Important APIs, Types, and Functions

`mouse_threshold` is a module parameter array passed to the Atari keyboard controller. `atamouse_interrupt()` is the hook called with three-byte relative mouse data. `atamouse_open()` programs IKBD mouse mode and assigns `atari_input_mouse_interrupt_hook`; `atamouse_close()` disables IKBD mouse reporting and clears the hook. `atamouse_init()` checks Atari hardware, initializes keyboard support, allocates/registers the input device, and `atamouse_exit()` unregisters it.

## Control Flow

Module init exits unless running on Atari hardware with ST MFP present. It then initializes the Atari keyboard layer and registers a BUS_HOST relative mouse input device. On open, the driver sets top-origin Y mode, applies movement thresholds, selects relative-position packets, and installs its interrupt hook. Each hook call decodes button bits from `buf[0]`, takes signed `dx`/`dy` from bytes 1 and 2, reports `REL_X`, `REL_Y`, left/middle/right buttons, and syncs. Close disables mouse reporting and removes the hook.

## State and Persistence Behavior

`atamouse_dev` is a single global input device pointer. Optional `FIXED_ATARI_JOYSTICK` code shares `atari_mouse_buttons` with architecture joystick handling. Thresholds persist as module parameter values for the module lifetime. There is no dynamic per-open allocation or durable state.

## Dependencies and Integration Points

The file depends on Atari-specific architecture APIs and globals (`MACH_IS_ATARI`, `ATARIHW_PRESENT`, `atari_keyb_init`, `ikbd_mouse_*`, and `atari_input_mouse_interrupt_hook`), plus input core and module infrastructure. It relies on the architecture keyboard/ACIA code to receive and classify mouse packets.

## Risks and Edge Cases

The global hook supports only one device instance. Open/close ordering must not race with architecture interrupt delivery after the hook is cleared. Button bit mapping is hardware-specific and includes optional joystick-derived middle button behavior under `FIXED_ATARI_JOYSTICK`. Invalid `mouse_threshold` values are not range-clamped in this file.

## Test Signals

Build and boot tests on Atari/m68k configurations should verify hardware gating, keyboard init failure handling, input registration, threshold programming, relative packet decoding including signed movement, all button combinations, close hook removal, and module unload.
