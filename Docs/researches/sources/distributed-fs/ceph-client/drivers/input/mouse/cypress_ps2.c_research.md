# sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.c

## Purpose

`cypress_ps2.c` implements support for Cypress PS/2 trackpads in the psmouse stack. It detects Cypress hardware, sends Cypress extension commands, queries firmware and optional geometry metrics, switches the device into absolute pressure mode, configures Linux input capabilities, parses variable-length absolute packets, reports semi-multitouch events, and handles reconnect/disconnect/rate callbacks.

## Important APIs, Types, and Functions

The psmouse entry points are `cypress_detect` and `cypress_init`. Command transport is handled by `cypress_ps2_sendbyte`, `cypress_ps2_ext_cmd`, `cypress_verify_cmd_state`, and `cypress_send_ext_cmd`. Hardware setup uses `cypress_read_fw_version`, `cypress_read_tp_metrics`, `cypress_query_hardware`, `cypress_set_absolute_mode`, `cypress_reset`, and `cypress_set_input_params`. Packet flow uses `cypress_get_finger_count`, `cypress_parse_packet`, `cypress_process_packet`, `cypress_validate_byte`, and `cypress_protocol_handler`. Lifecycle callbacks are `cypress_set_rate`, `cypress_disconnect`, and `cypress_reconnect`.

## Control Flow

Detection sends the encoded read-ID command and requires Cypress signature bytes `0x33 0xCC`. Initialization allocates `struct cytp_data`, resets the device, queries firmware/metrics, enters absolute-with-pressure mode, configures input ABS/MT/key capabilities, and installs psmouse callbacks. The protocol handler dynamically adjusts expected packet size based on the first byte and pressure mode, then processes a full packet. Packet parsing extracts one or two coordinate contacts, maps high-bit finger-count encodings including horizontal-scroll overloads for four/five-finger signals, suppresses left click on multifinger tap packets, and reports two semi-MT slots with button state.

## State and Persistence Behavior

All state is volatile in `struct cytp_data`: firmware version, packet size, mode bits, dimensions, pressure range, resolution, and metrics-support flag. Hardware mode persists only until reset or reconnect. `psmouse->private`, callback pointers, packet size, model, and rate fields bind this state into the psmouse core.

## Dependencies and Integration Points

The driver integrates with serio/libps2/psmouse, Linux input MT, and constants/types from `cypress_ps2.h`. It uses `ps2_command`, `ps2_sendbyte`, `psmouse_reset`, and psmouse protocol-handler callbacks rather than I2C.

## Risks and Edge Cases

Firmware version 11 and newer disable TP metrics because known devices return bogus data, leaving hardcoded default dimensions. `cypress_process_packet` ignores its `zero_pkt` argument; leave events are instead represented by zero contacts through normal reporting. Packet validation only inspects the first byte after mode is set, so malformed trailing bytes can still reach parsing. The code supports at most two actual coordinate slots while reporting higher finger counts through pointer emulation/tool count. Reconnect restores absolute mode but does not re-query geometry.

## Test Signals

Tests should cover detect success/failure signatures, extension-command retry/recovery, metrics-supported and default paths, invalid geometry rejection, absolute-mode setup, input capability setup, first-byte validation, dynamic 4/5/7/8-byte packet sizing, one/two/four/five-finger count decoding, tap suppression of button clicks, semi-MT slot assignment, reconnect failure and success, disconnect reset/free, and rate changes around the 80 Hz threshold.
