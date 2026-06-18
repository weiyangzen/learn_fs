# sources/distributed-fs/ceph-client/drivers/input/tablet/wacom_serial4.c

## Purpose
`wacom_serial4.c` is a serio protocol driver for Wacom protocol 4 serial tablets. It negotiates model, ROM version, resolution, and coordinate limits through ASCII commands, configures packet mode, and decodes seven-byte binary packets into pen/cursor/eraser input events.

## Important APIs, types, and functions
`struct wacom` stores the input device, command completion, expected response type, model flags, resolution and range data, current tool, packet index, data buffer, and phys path. Important functions include response handlers for model/configuration/coordinates, `wacom_handle_packet()`, `wacom_interrupt()`, `wacom_send()`, `wacom_send_and_wait()`, `wacom_setup()`, `wacom_connect()`, and `wacom_disconnect()`. The serio ID table matches `SERIO_RS232` protocol `SERIO_WACOM_IV`.

## Control flow
Connect allocates state, initializes default pressure bit handling, opens the serio port, queries model/version, optionally queries configuration and coordinate strings, sends a model-specific setup command sequence, configures input properties/ranges, and registers the input device. The interrupt handler distinguishes carriage-return-terminated ASCII responses from binary packets whose first byte has the sync bit. A response completes the pending command; a complete packet reports tool proximity, ABS_MISC device ID, X/Y, pressure, stylus buttons or cursor buttons/wheel, and syncs.

## State and persistence
Runtime state is per attached serio port. Model responses determine flags such as screen coverage, stylus2, scrollwheel, eraser mask, extra pressure bits, and ABS resolution. The current tool is tracked to release the previous tool when switching. No state is persisted outside the device session.

## Dependencies and integration points
The driver integrates with the serio bus, serial line discipline/inputattach path, input ABS/REL/KEY events, completions, and Wacom protocol command strings. It assumes serial speed and protocol reset were handled before binding.

## Risks
ASCII response parsing handles timeout by processing partial data, which is needed for some tablets but can accept malformed responses. Unsupported model handling depends on response bytes and may reject compatible devices. Packet parsing does not use the incoming serio error flags. Setup strings include untested model paths and no tilt support despite protocol documentation.

## Test signals
Test model response parsing for Cintiq, Cintiq II, Graphire, PenPartner, ArtPad/Digitizer II, unsupported model rejection, timeout response handling, packet sync recovery after garbage, pressure-bit variants, eraser and cursor transitions, scroll wheel reporting, and disconnect during command wait.
