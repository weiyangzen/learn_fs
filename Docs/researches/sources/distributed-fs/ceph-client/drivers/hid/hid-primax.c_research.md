<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-primax.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-primax.c

## Purpose
This driver fixes Primax keyboards that send modifier keys in-band in the key array instead of in the modifier byte. It rewrites raw keyboard input reports so generic HID keyboard handling sees standard modifier bits.

## Important APIs, types, and functions
`px_raw_event` is the only behavioral callback and is registered as `.raw_event` in `px_driver`. The device table binds `USB_VENDOR_ID_PRIMAX` and `USB_DEVICE_ID_PRIMAX_KEYBOARD`.

## Control flow
For report ID 0, the handler scans report bytes from the end down to index 2. Values 0xe0 through 0xe7 are USB HID modifier key usages. Each such value sets the corresponding bit in `data[0]` and clears the in-band key slot to zero. The adjusted report is immediately fed back into HID parsing through `hid_report_raw_event`, and the callback returns 1 to consume the original report. Unknown report IDs are logged and passed upstream.

## State and persistence behavior
No per-device state exists. The mutation is per input report and only affects the current event buffer.

## Dependencies and integration points
The file integrates with HID raw-event handling and generic HID keyboard parsing. It depends on the report being unnumbered/report ID 0 keyboard input with standard modifier usages.

## Risks and test signals
Risks are report layout assumptions and recursion or double-processing if the consumed return value changes. Tests should send reports with left/right modifiers in key slots, mixed normal keys, no modifiers, and unknown reports; expected output is one standard keyboard event stream with modifier bits set and no phantom key usages 0xe0-0xe7.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-primax.c -->
