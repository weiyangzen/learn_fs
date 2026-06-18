# sources/distributed-fs/ceph-client/drivers/input/mouse/alps.c

## Purpose

`alps.c` is the PS/2 protocol implementation for ALPS GlidePoint and DualPoint touchpads. It detects many ALPS generations, switches devices into absolute or multitouch reporting modes, decodes protocol-specific packets, reports Linux input events for the touchpad and optional pointing stick, and manages difficult PS/2 pass-through/interleaving behavior.

## Important APIs, Types, and Functions

The exported psmouse entry points are `alps_detect()` and `alps_init()`. Detection is driven by `alps_identify()`, `alps_rpt_cmd()`, the `alps_model_data[]` E7 signature table, firmware EC report heuristics, and `alps_set_protocol()`. Runtime byte handling uses `alps_process_byte()` as `psmouse->protocol_handler`, with protocol-specific callbacks stored in `struct alps_data`: `hw_init`, `process_packet`, `decode_fields`, and `set_abs_params`.

Packet/reporting code includes `alps_process_packet_v1_v2()`, `alps_process_touchpad_packet_v3_v5()`, `alps_process_packet_v4()`, `alps_process_packet_v6()`, `alps_process_packet_v7()`, and `alps_process_packet_ss4_v2()`. The important decoders are `alps_decode_pinnacle()`, `alps_decode_rushmore()`, `alps_decode_dolphin()`, `alps_decode_packet_v7()`, and `alps_decode_ss4_v2()`. Hardware setup is split across `alps_hw_init_v1_v2()`, `alps_hw_init_v3()`, `alps_hw_init_rushmore_v3()`, `alps_hw_init_v4()`, `alps_hw_init_dolphin_v1()`, `alps_hw_init_v6()`, `alps_hw_init_v7()`, and `alps_hw_init_ss4_v2()`.

## Control Flow

`alps_detect()` first does a trial identify, rejects ALPS CS19 trackpoint-only devices so `trackpoint.c` can own them, resets the PS/2 device, allocates `struct alps_data`, identifies again, and optionally sets psmouse vendor/name/model. `alps_init()` runs the selected hardware initializer, converts the primary input device from relative to absolute/multitouch reporting, creates an optional second input device for DualPoint stick data, initializes delayed registration for bare pass-through PS/2 mice, and installs psmouse callbacks.

At runtime `alps_process_byte()` validates packet sync bytes, handles bare PS/2 packets and interleaved PS/2 packets, applies protocol-specific partial-packet validation for V7/V8, and calls the selected `process_packet()` on complete packets. Early generations report single-touch absolute data plus buttons. V3/V5 combine position and bitmap packets into semi-MT bounding boxes through `alps_process_bitmap()`. V7 and SS4/V8 decode direct multitouch coordinates and use MT slot assignment. Trackstick packets are routed to `dev2` with relative movement and pressure when supported.

## State and Persistence Behavior

Persistent driver state is `struct alps_data`, stored in `psmouse->private`. It holds protocol identity, device and firmware IDs, flags, input devices, coordinate limits/resolution, nibble-command tables, packet assembly state (`multi_packet`, `multi_data`, `second_touch`, `prev_fin`), quirks, a flush timer, and delayed work for registering a bare PS/2 mouse. No on-disk state is used. Hardware state is changed by command/monitor-mode register writes to enable absolute mode, trackstick extended format, passthrough, raw mode, and stream reporting.

## Dependencies and Integration Points

The file integrates with psmouse core (`struct psmouse`, packet callbacks, polling, reconnect/disconnect), `libps2` commands, the Linux input subsystem including MT helpers, DMI quirks, serio pause helpers, workqueues, timers, and TrackPoint ID reads. `alps.h` supplies protocol constants and state structures. Documentation for wire formats is referenced in `Documentation/input/devices/alps.rst`.

## Risks and Edge Cases

ALPS hardware uses fragile magic command sequences; failures can leave devices in command mode, so error paths repeatedly call `alps_exit_command_mode()`. Packet validation is heuristic, especially for interleaved PS/2 and Rushmore last-byte corruption. Multi-packet bitmap flows can lose sync or reject palm-like packets. Some devices dynamically reveal trackstick-button quirks only after a button press. `alps_disconnect()` disables delayed work and unregisters optional devices, but race-sensitive paths involve timers, serio RX pause, and delayed `dev3` registration. Coordinate/resolution derivation from OTP/register data can fail, preventing protocol setup.

## Test Signals

Tests should cover detection through known E6/E7/EC signatures and fallback heuristics, CS19 rejection, every protocol initializer, command-mode failure unwinds, packet validation/resync for V1 through V8, semi-MT bitmap corner selection, V7/SS4 MT slot reporting, DualPoint trackstick setup and button routing, interleaved bare PS/2 packet handling, reconnect after reset, and disconnect while the flush timer or `dev3_register_work` is pending.
