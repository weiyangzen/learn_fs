# sources/distributed-fs/ceph-client/drivers/input/mouse/amimouse.c

## Purpose

`amimouse.c` is a Linux/m68k platform input driver for the Amiga mouse. It reads Amiga custom chip joystick/mouse counters and button registers on the vertical blank interrupt, converts wraparound deltas into relative movement, and reports a three-button relative mouse through the input subsystem.

## Important APIs, Types, and Functions

`amimouse_interrupt()` is the IRQ handler. `amimouse_open()` snapshots the initial `joy0dat` counters and requests `IRQ_AMIGA_VERTB`; `amimouse_close()` frees it. `amimouse_probe()` allocates/registers the `input_dev`, sets `EV_REL` and `EV_KEY` capabilities, and stores it in platform driver data. `amimouse_remove()` unregisters the input device. `module_platform_driver_probe()` registers a non-hot-unbind platform driver named `amiga-mouse`.

## Control Flow

When the platform device probes, the driver creates an input device with BUS_AMIGA IDs and open/close callbacks. On first userspace open, it records the current low/high bytes of `amiga_custom.joy0dat` as the last X/Y counters and requests the vertical blank IRQ. Each interrupt reads the next 8-bit counters, computes signed deltas with 256-count wrap correction, reads `ciaa.pra` and `amiga_custom.potgor` for button state, reports `REL_X`, `REL_Y`, `BTN_LEFT`, `BTN_MIDDLE`, and `BTN_RIGHT`, then syncs the input frame.

## State and Persistence Behavior

The only driver state is `amimouse_lastx` and `amimouse_lasty`, static globals preserving the prior hardware counter values between interrupts. The input device pointer is owned by platform driver data after registration. There is no persistent configuration or storage.

## Dependencies and Integration Points

The file depends on Amiga architecture headers and hardware globals (`amiga_custom`, `ciaa`, `IRQ_AMIGA_VERTB`), platform driver infrastructure, and input core. Its remove function is in exit text and is used only for module unload, matching `module_platform_driver_probe()` constraints.

## Risks and Edge Cases

Button bits are reported directly from hardware bit masks; if the electrical polarity is active-low, consumers rely on the historical convention used here. Delta wrap correction assumes interrupt frequency keeps movement between samples within +/-127 counts. Missed vertical blanks can produce wrong direction after large movement. The driver is Amiga-specific and will not probe without the matching platform device.

## Test Signals

Useful tests are m68k build coverage, probe/open/close with IRQ request/free, synthetic counter wrap cases, button bit reporting for all three buttons, and module unload ensuring the input device is unregistered.
