# sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.h

## Purpose

`cypress_ps2.h` is the protocol definition and private-state header for the Cypress PS/2 trackpad driver. It defines Cypress extension-command encoding, mode/status bits, packet bitfields, default geometry, MT limits, report/private-data structures, and the psmouse-visible detect/init prototypes.

## Important APIs, Types, and Functions

The command macros `ENCODE_CMD`, `DECODE_CMD_AA/BB/CC/DD`, and `CYTP_CMD_*` describe how four two-bit nibbles are sent through PS/2 extension commands. Mode flags include absolute-with-pressure, absolute-without-pressure, Cypress relative, standard relative, high-rate, and report-mode bits. Packet and response masks describe button bits, absolute scroll/tap bits, status response bits, and TP metrics flags. `struct cytp_contact`, `struct cytp_report_data`, and `struct cytp_data` are consumed by `cypress_ps2.c`. Public prototypes are `cypress_detect` and `cypress_init`.

## Control Flow

The header itself has no executable control flow, but it defines the encoding used by `cypress_send_ext_cmd`: each Cypress command is decomposed into DD, CC, BB, and AA nibbles and sent as PS/2 set-resolution extension bytes before a get-info command reads the response. Packet constants drive `cypress_validate_byte` and `cypress_parse_packet`.

## State and Persistence Behavior

`struct cytp_data` is the persistent per-device runtime cache held in `psmouse->private`. It stores firmware version, current packet size, Cypress mode bits, pressure/dimension/resolution values, and whether TP metrics are supported. `struct cytp_report_data` is transient parsed packet state for the current input report.

## Dependencies and Integration Points

The header includes `psmouse.h` for `struct psmouse` and is private to the psmouse Cypress implementation. Its constants are tightly coupled to the packet parser, input setup, and command transport in `cypress_ps2.c`.

## Risks and Edge Cases

The misspelled `FW_VERSION_MASX` and `CYTP_CMD_PALM_GEMMETRY_MASK` names are ABI-internal but can trip search/readability. Defaults are based on specific Dell XPS dimensions and become the fallback for devices without trustworthy metrics. `CYTP_MAX_MT_SLOTS` is two even though tool-count constants represent up to five fingers, so consumers must treat this as semi-MT.

## Test Signals

Build coverage should catch macro/prototype drift with `cypress_ps2.c`. Behavioral tests should validate command encode/decode round trips, mode-bit combinations, packet bit masks used by finger/button parsing, default dimension constants, and structure layout expectations for two contact slots and cached device parameters.
