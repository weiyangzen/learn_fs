# sources/distributed-fs/ceph-client/drivers/usb/atm/speedtch.c

## Purpose
`speedtch.c` is the `usbatm` mini-driver for Alcatel/Thomson SpeedTouch USB DSL modems. It handles multi-interface claiming, two-stage firmware upload, interface altsetting selection for bulk or isochronous data, modem synchronization commands, status polling, and interrupt-driven line state hints.

## Important APIs, Types, And Functions
- Module parameters include `altsetting`, `dl_512_first`, `enable_isoc`, `sw_buffering`, `BMaxDSL`, `ModemMode`, and `ModemOption`.
- `struct speedtch_instance_data` stores a snapshot of parameters, status and resubmit timers, status work, interrupt URB/data, poll delay, and scratch buffer.
- `speedtch_upload_firmware()` uploads stage 1 and stage 2 firmware through endpoint 5, sets the data interface, optionally enables software buffering, and sends the magic test/option sequence.
- `speedtch_check_status()` reads multiple control status fields and updates ATM signal/link rate.
- `speedtch_handle_int()` handles known up/down interrupt packets and resubmits or schedules recovery.
- `speedtch_bind()` claims all interfaces, chooses data altsetting, detects isochronous support, allocates the interrupt URB, and detects preloaded firmware.
- `speedtch_atm_start()` derives ESI from USB serial, starts synchronization, submits interrupt URB, and starts polling.

## Control Flow
Probe delegates to `usbatm_usb_probe()`. Bind verifies vendor-specific class, claims companion interfaces, snapshots mutable module parameters, tries requested or default altsettings, sets `UDSL_USE_ISOC` if applicable, allocates timers/work/interrupt URB, and resets the device if firmware is absent. Heavy init requests `speedtch-1.bin*` and `speedtch-2.bin*`, uploads both firmware blocks, then configures the modem. ATM start prods synchronization and starts both interrupt URB and periodic status timer. Status work reads modem state and adapts the polling delay after failures.

## State And Persistence Behavior
The driver keeps per-device parameter snapshots so later module parameter changes do not affect an already-bound modem. Runtime state includes last status, adaptive poll delay, interrupt URB lifecycle, and timers. Firmware-loaded state exists in the modem, not on disk. The driver does not persist line settings.

## Dependencies And Integration Points
It depends on USB core, firmware loader, workqueues, timers, `usbatm`, and ATM. It integrates with `usbatm` through `bind`, `heavy_init`, `unbind`, `atm_start`, `atm_stop`, and endpoint declarations for bulk and isochronous data.

## Risks And Edge Cases
Firmware naming falls back through device-revision-specific names to generic names. Interrupt URB and resubmit timer can schedule each other, so `speedtch_atm_stop()` uses a two-step shutdown with `instance->int_urb = NULL`, barriers, kills, and timer deletion. MAC parsing from the serial string assumes 12 hex characters. Status polling backs off and eventually disables itself after repeated failures. Interface claiming must be released on every bind failure.

## Test Signals
Test cold firmware upload and already-loaded detection. Verify bulk default and isochronous altsetting paths. Confirm ESI from serial number, line-up/down ATM signal changes, status polling backoff, interrupt URB resubmission, and clean disconnect during active polling. Validate all claimed interfaces are released on unbind and bind failures.
