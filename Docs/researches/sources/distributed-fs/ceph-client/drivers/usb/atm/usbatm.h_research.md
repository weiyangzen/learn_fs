# sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.h

## Purpose
`usbatm.h` defines the shared interface between the generic USB ATM core and USB DSL mini-drivers. It declares logging helpers, mini-driver flags and callbacks, endpoint/padding configuration, probe/disconnect exports, channel state, and the main per-device `struct usbatm_data`.

## Important APIs, Types, And Functions
- Logging macros `usb_err`, `usb_info`, `atm_err`, `atm_warn`, and debug variants standardize USB and ATM messages.
- Flags `UDSL_SKIP_HEAVY_INIT`, `UDSL_USE_ISOC`, and `UDSL_IGNORE_EILSEQ` let mini-drivers alter core behavior.
- `struct usbatm_driver` defines `bind`, `heavy_init`, `unbind`, `atm_start`, `atm_stop`, endpoint numbers, and RX/TX padding.
- `usbatm_usb_probe()` and `usbatm_usb_disconnect()` are exported for mini-driver USB probe/disconnect functions.
- `struct usbatm_channel` describes a USB pipe, ATM stride, buffer sizing, spare/completed URB list, tasklet, throttle timer, and back-pointer.
- `struct usbatm_data` combines public mini-driver-visible fields with private core state.
- `to_usbatm_driver_data()` safely retrieves mini-driver state from a USB interface.

## Control Flow
The header itself has no executable control flow. It documents the intended mini-driver callback order: `bind`, optional `heavy_init`, `atm_start`, later `atm_stop`, and `unbind`. The C core enforces that lifecycle and uses endpoint/padding fields to configure URB channels.

## State And Persistence Behavior
`struct usbatm_data` state is runtime-only and owned by the core after probe. Public fields can be initialized by mini-drivers during bind; private fields must not be touched by them. No persistent state is described.

## Dependencies And Integration Points
The header integrates USB mini-drivers with Linux ATM, USB core, kref lifetime, completions, lists, mutexes, timers, and sk_buffs. It is included by `usbatm.c`, `cxacru.c`, `speedtch.c`, `ueagle-atm.c`, and `xusbatm.c`.

## Risks And Edge Cases
The public/private split is by comment, not compiler enforcement. Mini-drivers must set endpoints and padding consistently with hardware or the core will segment cells incorrectly. `to_usbatm_driver_data()` returns NULL after interface data is cleared or after `driver_data` is nulled, which sysfs paths must handle.

## Test Signals
Compile every mini-driver against the header. Add sparse or runtime assertions around mini-driver flags/endpoints. Exercise sysfs reads after disconnect to verify `to_usbatm_driver_data()` NULL handling.
