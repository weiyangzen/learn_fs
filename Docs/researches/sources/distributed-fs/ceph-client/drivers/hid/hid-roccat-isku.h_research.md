# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.h

## Purpose

`hid-roccat-isku.h` defines the Isku report sizes, command IDs, profile report layout, interrupt button report format, char-device event layout, and per-device state used by the Isku driver.

## Important APIs, Types, and Functions

- Size constants such as `ISKU_SIZE_MACRO`, `ISKU_SIZE_KEYS_EASYZONE`, and `ISKU_SIZE_LIGHT` define sysfs binary ABI lengths.
- `ISKU_USB_INTERFACE_PROTOCOL` selects the keyboard interface handled by the driver.
- `struct isku_actual_profile`: three-byte feature report for active profile.
- `enum isku_commands`: command IDs for key groups, macros, info, light, reset, talk, and firmware operations.
- `struct isku_report_button`, `ISKU_REPORT_NUMBER_BUTTON`, and `ISKU_REPORT_BUTTON_EVENT_PROFILE`: interrupt-report contract.
- `struct isku_roccat_report` and `struct isku_device`: event ABI and cached driver state.

## Control Flow

The C file's generated sysfs callbacks are parameterized by the sizes and command IDs in this header. Raw event handling casts button reports to `struct isku_report_button` and emits `struct isku_roccat_report`.

## State and Persistence Behavior

The header defines only layouts. `actual_profile` is cached in `struct isku_device`, while all key/macro/light data is device firmware state accessed through packed command payloads.

## Dependencies and Integration Points

It depends on fixed-width Linux types and is consumed by `hid-roccat-isku.c`. The command constants are also part of the implicit userspace ABI because bin attribute sizes and meanings are stable.

## Risks and Edge Cases

Changing any size constant or packed layout breaks both firmware communication and userspace tools. Firmware-write command IDs are declared but not used in this C file, so future update paths need careful validation.

## Test Signals

Layout-size checks and sysfs attribute size verification should cover each constant. Event tests should verify profile report parsing and one-based profile publication.
