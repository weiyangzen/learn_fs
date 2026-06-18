# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.h

## Purpose
This header exposes firmware-parser helper selection and shared atomfirmware translation helpers.

## Important APIs, Types, And Functions
It declares `dal_bios_parser_init_cmd_tbl_helper2()` plus controller, encoder mode, clock-source, transmitter, and encoder object ID mapping helpers with a `2` suffix.

## Control Flow
No executable control flow is present. Header inclusion selects the helper provider headers needed by the implementation.

## State And Persistence
The header defines no persistent state. Implementations return static helper table pointers and fill caller-provided outputs.

## Dependencies And Integration Points
It conditionally includes DCE60 plus DCE80, DCE110, DCE112 helper2, and the shared helper struct. It is the helper interface for `command_table2.c`.

## Risks
The interface is similar but not identical to `command_table_helper.h`; mixing legacy and firmware helper functions can produce incorrect mappings. Not every legacy helper is exported in the v2 interface.

## Test Signals
Build coverage should ensure all declared functions are linked in firmware parser builds. Runtime signals are successful DCN firmware command execution using mapped controller, PLL, transmitter, and encoder IDs.
