# sources/distributed-fs/ceph-client/drivers/input/tablet/hanwang.c

## Purpose
`hanwang.c` is a USB input driver for Hanwang Art Master II/III/HD tablets. It maps product IDs to feature tables, decodes pen/cursor/eraser/pad packets, and reports coordinates, pressure, tilt, wheel, pad buttons, and tool identity.

## Important APIs, types, and functions
`struct hanwang_features` describes product ID, model name, tablet type, packet length, coordinate ranges, tilt ranges, and pressure range. `struct hanwang` stores the USB/input state, current tool/id, feature pointer, names, and URB buffer. Main functions are `get_features()`, `hanwang_probe()`, `hanwang_parse_packet()`, `hanwang_irq()`, `hanwang_open()`, `hanwang_close()`, and `hanwang_disconnect()`.

## Control flow
Probe accepts a vendor/interface-class match, validates at least one endpoint, finds product features from the USB descriptor, allocates a coherent packet buffer and URB, configures input capabilities from static event arrays and feature ranges, submits the interrupt URB on open, and registers the input device. Packet parsing handles `0x02` tool data/proximity packets and `0x0c` pad packets, with type-specific pressure and pad decoding.

## State and persistence
Current tool and current ID are kept in memory to report proximity and `ABS_MISC`. Feature tables are static and selected at probe. There is no persistent configuration or hardware programming.

## Dependencies and integration points
The driver integrates with USB interrupt input, input ABS/KEY/MSC events, endian helpers for big-endian coordinate fields, and module matching based on vendor plus HID-like interface class/subclass/protocol.

## Risks
The USB ID table matches broad vendor/interface information and relies on `get_features()` to reject unknown product IDs. Probe does not verify that endpoint 0 is interrupt-in before filling the URB. Art Master II has special proximity handling and ignores pad packets; changes to shared parsing can regress that path. Packet parsing assumes `features->pkg_len` bytes are valid for all field accesses.

## Test signals
Test every product in `features_array`, unknown product rejection, endpoint validation, pressure formulas for Art Master III vs HD/II, proximity in/out for stylus and eraser, pad packet decoding for III and HD, Art Master II special cases, and disconnect while an URB is active.
