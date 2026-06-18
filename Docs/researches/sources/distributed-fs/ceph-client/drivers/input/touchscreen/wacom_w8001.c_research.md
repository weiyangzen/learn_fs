# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_w8001.c

## Purpose
`wacom_w8001.c` is a serio driver for Wacom W8001 serial penabled/touch devices. It can register separate pen and finger input devices, support one- or two-finger touch packets, and scale touch coordinates to pen coordinates when both capabilities exist.

## Important APIs, Types, And Functions
`struct w8001` stores pen/touch input devices, serio state, command completion, response/data buffers, packet lengths, maximum pen/touch dimensions, current tool type, open count, and mutex. `parse_pen_data()`, `parse_single_touch()`, `parse_multi_touch()`, and `parse_touchquery()` decode protocol packets. `w8001_command()` sends start/stop/query commands and optionally waits for a control response. Setup functions query pen and touch capabilities and initialize input axes/MT slots.

## Control Flow
Connect allocates state and both input devices, opens serio, stops/query-detects the controller, probes pen and touch support, registers whichever devices are present, and composes names based on capabilities. The interrupt parser accumulates serial bytes, validates leading bits, dispatches complete pen/touch/control/multitouch packets, and completes command queries. Open starts the device on the first opener; close stops it after the last input device closes.

## State And Persistence
State includes partial packet index, command response, open count shared by pen and touch devices, current tool classification, and learned maximum dimensions. No persistent hardware settings are stored.

## Dependencies And Integration Points
It uses serio, completions, input MT slot helpers, input absolute resolution metadata, and Wacom serial protocol IDs.

## Risks
Pen and touch devices share one serial stream and open count, so error paths must avoid double-free or premature stop. Tool disambiguation for eraser versus second stylus button is heuristic. Query timeouts return `-EIO`; noisy serial streams can desynchronize packet parsing.

## Test Signals
Test pen-only, touch-only, combined, and 2FG devices; command timeout paths; packet resynchronization; shared open/close ordering; eraser transition behavior; MT slot reporting; and connect failure unwinding after one device registers.
