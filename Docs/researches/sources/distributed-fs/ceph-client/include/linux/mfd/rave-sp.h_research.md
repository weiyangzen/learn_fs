# sources/distributed-fs/ceph-client/include/linux/mfd/rave-sp.h

## Purpose
`rave-sp.h` exposes the shared command and event interface for the Zodiac RAVE Supervisory Processor MFD driver. It is used by child drivers that need firmware/version data, watchdog control, EEPROM access, reset reason, GPIO state, backlight control, or event notifications.

## Important APIs, Types, And Constants
`enum rave_sp_command` lists firmware, bootloader, board revision, GPIO, status, watchdog, EEPROM, backlight, reset, I2C-device status, silicon revision, and event-control commands. `struct rave_sp` is opaque. `rave_sp_action_pack()`, `rave_sp_action_unpack_event()`, and `rave_sp_action_unpack_value()` encode event/value pairs into a notifier action. `rave_sp_exec()` sends a command frame and receives a reply. `devm_rave_sp_register_event_notifier()` registers a managed notifier block for SP events.

## Control Flow And State
Child drivers build command payloads, call `rave_sp_exec()`, and decode replies. Event-capable users register a notifier; the MFD core receives events from the SP, packs event/value into an unsigned long action, and dispatches through the notifier chain. Device-managed registration ties notifier lifetime to the child device.

## State And Persistence Behavior
Hardware state includes watchdog configuration, reset cause, backlight level, EEPROM contents, event enablement, and firmware data. Runtime notification state is stored in the core and notifier registrations. The action packing is transient and only valid for notification dispatch.

## Dependencies And Integration Points
The header depends on Linux notifier APIs and forward-declares `struct device`. It integrates with watchdog, nvmem/EEPROM, backlight, reset, GPIO/status, and board-management child drivers. The command values are firmware ABI and must match SP firmware.

## Risks
The command ABI uses raw buffers and sizes, so command-specific length mistakes are likely failure points. Notifier action packing only preserves one byte of event and one byte of value; larger values would be truncated by design. Firmware version differences can make commands unavailable or semantically different.

## Test Signals
Tests should validate command framing and reply sizes, notifier registration/unregistration lifetime, event packing/unpacking round trips, watchdog pet/control commands, reset reason reads, and unavailable-command error handling across firmware revisions.
