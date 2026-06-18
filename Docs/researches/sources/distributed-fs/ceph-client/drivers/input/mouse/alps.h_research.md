# sources/distributed-fs/ceph-client/drivers/input/mouse/alps.h

## Purpose

`alps.h` is the private protocol contract for the ALPS PS/2 touchpad driver. It defines protocol version IDs, packet bitfield extraction macros, multitouch packet identifiers, decode result structures, private driver state, quirks, and the psmouse-facing `alps_detect()` / `alps_init()` declarations.

## Important APIs, Types, and Functions

Important protocol constants include `ALPS_PROTO_V1` through `ALPS_PROTO_V9`, `MAX_TOUCHES`, Dolphin and SS4 sensor geometry constants, and `ALPS_QUIRK_TRACKSTICK_BUTTONS`. `enum SS4_PACKET_ID` and `enum V7_PACKET_ID` classify packet kinds. The SS4 macros such as `SS4_1F_X_V2`, `SS4_STD_MF_X_V2`, `SS4_TS_X_V2`, and `SS4_BTN_V2` centralize byte-to-coordinate extraction.

Core structures are `struct alps_protocol_info`, `struct alps_model_info`, `struct alps_nibble_commands`, `struct alps_bitmap_point`, `struct alps_fields`, and `struct alps_data`. `struct alps_data` is the long-lived state object used by `alps.c`; it stores input devices, command tables, device IDs, geometry, callback pointers, packet assembly fields, decoded fields, quirks, and the timer.

## Control Flow

The header does not execute code directly, but it shapes `alps.c` dispatch. Detection fills an `alps_protocol_info`, `alps_set_protocol()` copies it into `alps_data`, and packet handlers write normalized decoded values into `struct alps_fields` before reporting through input core. Packet macros are used by SS4/V8 decode paths to select one-finger, multi-finger, idle, and stick packets.

## State and Persistence Behavior

`struct alps_data` persists for the lifetime of the psmouse protocol binding. `multi_packet` and `multi_data` preserve partial packet streams, `prev_fin` preserves tap/drag transition state, `second_touch` stabilizes semi-MT bounding-box corner choice, and `quirks` records runtime-detected model behavior. All persistence is in kernel memory.

## Dependencies and Integration Points

The header depends on `linux/input/mt.h` for `struct input_mt_pos` and input MT slot semantics. Its public declarations are consumed by psmouse core and `alps.c`. The byte extraction macros must remain aligned with the protocol packet documentation and the report sizes set in `alps.c`.

## Risks and Edge Cases

Many macros assume a six-byte packet and valid indices; callers must validate packet length and type first. `BIT(priv->x_bits) - 1` style consumers rely on geometry values staying within integer widths. Callback pointers in `struct alps_data` must be fully initialized for each protocol version, or runtime packet processing can dereference NULL. The misspelled comment on `ALPS_QUIRK_TRACKSTICK_BUTTONS` is harmless but the quirk itself affects which device receives button events.

## Test Signals

Build tests should ensure the header remains synchronized with `alps.c` callbacks and structure fields. Runtime tests should indirectly validate each packet macro through V7 and SS4 packet decode fixtures, and should verify state fields are initialized/reset correctly across detection, init, reconnect, and disconnect.
