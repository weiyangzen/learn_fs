# sources/distributed-fs/ceph-client/drivers/hid/wacom.h

## Purpose

`wacom.h` is the shared public/private header for the Wacom HID driver family. It defines the driver metadata, core runtime structures for Wacom devices, LED groups, batteries, remotes, work scheduling, helper conversions, and cross-file function prototypes used by `wacom_sys.c` and Wacom protocol code.

## Important APIs, Types, And Data

- `DRIVER_VERSION`, `DRIVER_AUTHOR`, and `DRIVER_DESC` describe the Wacom HID driver.
- `USB_VENDOR_ID_WACOM` and `USB_VENDOR_ID_LENOVO` are vendor constants used by the driver.
- `enum wacom_worker` identifies deferred work lanes: wireless, battery, remote, and mode change.
- `struct wacom_led`, `struct wacom_group_leds`, `struct wacom_battery`, and `struct wacom_remote` model LEDs, LED groups, power-supply state, and ExpressKey Remote state.
- `struct wacom` is the top-level per-HID-device runtime object: USB/HID backpointers, `struct wacom_wac`, locks, work items, delayed works, remote pointer, idle proximity timer, LED state, battery state, and a `resources` flag for devres group ownership.
- `wacom_schedule_work()` maps protocol-layer worker requests onto the appropriate work_struct.
- `wacom_s32tou()` undoes sign extension for signed HID fields that should be interpreted as unsigned n-bit values.
- `wacom_rescale()` clamps and rescales integer ranges.

## Control Flow

Most runtime control flow is in `wacom_sys.c` and `wacom_wac.c`; this header provides inline helpers. `wacom_schedule_work()` receives a `struct wacom_wac *`, finds the containing `struct wacom`, and schedules one of four work items. `wacom_s32tou()` selects an exact cast for 8/16/32-bit fields and otherwise masks an n-bit unsigned value. `wacom_rescale()` handles zero maxima, clamps input, and uses rounded integer scaling.

## State And Persistence Behavior

The header declares the layout of Wacom runtime state but does not allocate it. `struct wacom` instances are allocated per HID device in `wacom_probe()` and are normally devm-managed. LED, battery, remote, work, and input-device state is volatile and recreated at probe/reparse time. Shared pen/touch state is referenced through `struct wacom_wac.shared`, whose concrete allocation is managed in `wacom_sys.c`.

## Dependencies And Integration Points

- Includes kernel HID, input, LED, kfifo, USB input, power supply, timer, and unaligned helpers.
- Depends on definitions from `wacom_wac.h` because `struct wacom` embeds `struct wacom_wac` and refers to Wacom feature constants.
- Provides prototypes implemented across `wacom_sys.c`, `wacom_wac.c`, and related Wacom files.
- Integrates Wacom with HID core, input core, LED class, power supply class, workqueues, timers, and USB metadata.

## Risks And Edge Cases

- `wacom_schedule_work()` has no default case. New `enum wacom_worker` values require an update or requests will silently do nothing.
- `wacom_s32tou()` uses `1 << (n - 1)` for non-standard widths; callers must avoid `n == 0` and overly large shifts.
- `wacom_rescale()` multiplies `value * out_max` in 32-bit arithmetic, so very large ranges could overflow before division.
- The top-level `struct wacom` aggregates many subsystems; lifetime and cancellation ordering must be correct in implementation files.

## Test Signals

- Build coverage across Wacom modules should catch struct/prototype drift.
- Runtime tests for protocol code scheduling each `enum wacom_worker` should observe the expected work item running.
- Unit-style tests or static checks for `wacom_s32tou()` and `wacom_rescale()` should cover common bit widths, zero maxima, clamping, and large inputs.
