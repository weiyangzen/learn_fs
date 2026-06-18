# sources/distributed-fs/ceph-client/drivers/hid/hid-elo.c

## Purpose
`hid-elo.c` supports ELO USB touchscreen 4000/4500 devices. It corrects input capabilities so the device is treated as a touchscreen, decodes ELO touch packets from raw HID reports, and contains a periodic SmartSet diagnostics workaround for firmware level `M` devices that otherwise need repeated pokes.

## Important APIs, Types, And Functions
`struct elo_priv` stores the USB device, delayed work item, and 8-byte SmartSet buffer. `elo_input_configured()` removes `BTN_LEFT`, adds `BTN_TOUCH`, and configures `ABS_PRESSURE`. `elo_process_data()` decodes X/Y, pressure, touch-down, and touch-up from ELO packet bytes. `elo_raw_event()` recognizes report ID 0 packets beginning with `'T'` and consumes them after input reporting. `elo_smartset_send_get()` sends vendor control messages for SmartSet send/get, and `elo_flush_smartset_responses()` clears pending responses. `elo_work()` implements the periodic diagnostics sequence. `elo_broken_firmware()` decides whether to enable the workaround by checking `bcdDevice`, the `use_fw_quirk` module parameter, and sibling IBM video devices. `elo_probe()` and `elo_remove()` manage HID and work lifetime. Custom module init/exit create and destroy a singlethread workqueue.

## Control Flow
Module init creates workqueue `elousb` before registering the HID driver. Probe requires a USB-backed HID device, allocates `elo_priv`, initializes delayed work, stores the USB device pointer, parses HID, and starts HID. If `elo_broken_firmware()` returns true, probe schedules the first delayed work run after one second. Remove stops HID, cancels delayed work synchronously, and frees private state.

Runtime touch reports flow through `elo_raw_event()`: if input is claimed and report ID is zero, packets starting with `'T'` are decoded. X uses bytes 3:2, Y uses 5:4, pressure is bytes 7:6 only when bit 7 of byte 1 is set, bits 0-1 indicate touch down, and bit 2 indicates touch release. The workaround work item flushes responses, sends diagnostics, reads the result and possibly an ack, flushes again, and reschedules itself regardless of intermediate failures.

## State And Persistence
State is runtime-only: per-device work item, USB pointer, SmartSet buffer, module-wide workqueue, and `use_fw_quirk` parameter. The workaround sends vendor commands but does not persistently change device settings.

## Dependencies And Integration Points
The driver depends on HID core, Linux input, USB control messaging, workqueues, module parameters, and ELO IDs from `hid-ids.h`. User-visible integration is a touchscreen input device with `ABS_X`, `ABS_Y`, `ABS_PRESSURE`, and `BTN_TOUCH`, plus periodic USB vendor traffic for affected firmware.

## Risks
The work item always reschedules itself from the `fail` path, so remove must cancel synchronously after stopping HID. Firmware detection walks sibling USB devices and uses hardcoded IBM product IDs; topology assumptions must stay accurate. Touch parsing assumes packet length is sufficient for bytes through index 7, relying on device/report correctness. Periodic diagnostics add USB traffic and can log repeated errors on failing hardware. The module parameter can disable a needed workaround.

## Test Signals
Test with ELO 4000/4500 devices should show touchscreen classification rather than mouse classification, correct X/Y/pressure/touch release in `evtest`, raw unknown reports passed upstream with logs, firmware `0x010d` scheduling diagnostics except on excluded IBM sibling combinations, clean unload while work is pending, and no workqueue leaks when `hid_register_driver()` fails.
