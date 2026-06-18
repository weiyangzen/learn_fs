<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_cir.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_cir.c

## Purpose
This module turns PicoLCD IR receiver HID packets into rc-core raw IR events. It registers an `rc_dev` for raw IR decoding and interprets HID interval data as pulse/space durations in microseconds.

## Important APIs, types, and functions
`picolcd_raw_cir` is called from core raw-event handling for `REPORT_IR_DATA`. `picolcd_init_cir` allocates/registers an `RC_DRIVER_IR_RAW` device with `RC_PROTO_BIT_ALL_IR_DECODER`, `RC_MAP_RC6_MCE`, 100 ms timeout, and 1 us resolution. `picolcd_cir_open` clears `PICOLCD_CIR_SHUN`; `picolcd_cir_close` sets it; `picolcd_exit_cir` unregisters and frees the rc device.

## Control flow
Raw IR data begins with a length byte. The handler ignores input when `rc_dev` is absent or CIR is shunned, then parses 16-bit big-endian interval words. The high bit means pulse and stores a negated-duration encoding; pulse duration is converted with `65536 - w`, while spaces use the raw value. A first interval greater than 15000 us is reduced by 15000 as a device-specific quirk before events are stored and flushed with `ir_raw_event_handle`.

## State and persistence behavior
The module stores only `data->rc_dev` and the `PICOLCD_CIR_SHUN` bit. Open/close controls whether incoming IR data is consumed. No learned remotes or decoded keys are persisted here; rc-core/user space owns protocol decoding configuration.

## Dependencies and integration points
It integrates HID raw reports with media `rc-core`, input identity fields from the HID device, and the shared PicoLCD lock/status. Core dispatches only the report payload, skipping the report ID byte.

## Risks and test signals
Risks are malformed length bytes, interval interpretation quirks, and remove races while raw reports arrive. Tests should open/close the rc device, verify raw event timing with known remotes, check the >15000 us first-interval adjustment, and disconnect during active IR input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_cir.c -->
