# sources/distributed-fs/ceph-client/drivers/input/keyboard/hil_kbd.c

## Purpose

`hil_kbd.c` is a serio driver for HP-HIL keyboards, mice, tablets, and touchscreens. It queries HIL device records, configures an input device as either keyboard or pointer, parses packetized HIL bus data, and reports Linux input events.

## Important APIs, Types, and Functions

- `struct hil_dev` stores input/serio pointers, packet assembly buffer/index, raw ID/RSC/EXD/RNM records, command completion, pointer flag, axis/button metadata, and button map.
- `hil_dev_interrupt()` assembles four-byte `hil_packet` words from serio bytes and dispatches complete command responses or poll events.
- `hil_dev_handle_command_response()` stores IDD/RSC/EXD/RNM records and completes the waiting command.
- `hil_dev_handle_kbd_events()` decodes HIL keyboard chartypes and key sets.
- `hil_dev_handle_ptr_events()` decodes relative/absolute axes and buttons.
- `hil_dev_connect()` queries device records, selects keyboard or pointer setup, optionally enables keyboard autorepeat, and registers input.

## Control Flow

Connect allocates state/input, opens serio, sends four-byte HIL commands for IDD, RSC, RNM, and EXD, waiting for completions filled by interrupt parsing. Based on the DID type, it rejects unsupported combo devices, configures keyboard keybits/keymap or pointer axes/buttons, fills input IDs, enables HIL keyboard autorepeat when appropriate, and registers input. Incoming serio bytes are packed into HIL packets; command records complete setup waits, while poll records dispatch to keyboard or pointer event handlers and then reset packet assembly.

## State and Persistence Behavior

The packet assembly index and buffered packets persist between bytes. Device information records persist after connect and drive event decoding. Pointer button maps and axis capabilities persist for the device lifetime. Command completions synchronize setup commands with interrupt responses.

## Dependencies and Integration Points

It depends on the serio HIL MLC transport, `linux/hil.h` protocol definitions/keycode maps/locales, input core, completions, PCI vendor IDs for HP, and serio modaliases for HIL keyboard/mouse devices.

## Risks and Edge Cases

Malformed packets reset assembly and complete waiters defensively. Setup waits are killable but have no explicit timeout in this file, so missing responses can block until interrupted. Combo keyboard/pointer devices are unsupported. Axis/button parsing depends on IDD metadata and HIL packet count fields. Some optional tablet auto-adjust/mouse simulation behavior is compile-time disabled.

## Test Signals

Test keyboard chartypes Set1/Set2/Set3/ASCII/binary, pointer relative and absolute devices, multi-axis and alternate-axis packets, button maps including mouse middle/right swap, malformed packets, missing command responses, unsupported combo devices, RNM naming, disconnect during input activity, and serio modalias matching.
