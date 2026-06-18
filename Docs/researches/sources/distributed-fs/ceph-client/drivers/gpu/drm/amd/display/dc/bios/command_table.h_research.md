# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.h

## Purpose
This header declares the legacy BIOS command-table dispatch structure and initializer for the display BIOS parser.

## Important APIs, Types, And Functions
- `struct cmd_tbl` is a table of function pointers for all legacy ATOM command operations supported by the parser.
- `dal_bios_parser_init_cmd_tbl(struct bios_parser *bp)` initializes those function pointers based on VBIOS command table revisions.
- Forward declarations cover `struct bios_parser` and `struct bp_encoder_control`; the remaining parameter types are expected from included BIOS parser type headers before use.

## Control Flow
The header does not implement control flow. It defines the ABI that command table implementation files populate and BIOS parser callers invoke.

## State And Persistence
Instances of `struct cmd_tbl` are embedded in `struct bios_parser`. The function pointers persist for the parser lifetime and encode the active VBIOS capability set.

## Dependencies And Integration Points
It is consumed by `command_table.c` and parser code that invokes BIOS command functions. The function pointer signatures bind this module to display core BIOS types such as `bp_pixel_clock_parameters`, `bp_transmitter_control`, and `controller_id`.

## Risks
Because the dispatch table contains nullable function pointers, callers must check availability or rely on parser wrappers to do so. Signature changes are ABI-sensitive across all parser implementations.

## Test Signals
Compile coverage catches signature drift. Runtime coverage should verify that every initialized parser path checks or handles absent function pointers for unsupported VBIOS tables.
