# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.h

## Purpose
This header exposes the legacy command-table helper selection and shared translation routines.

## Important APIs, Types, And Functions
It declares `dal_bios_parser_init_cmd_tbl_helper()`, controller/transmitter/encoder/clock-source mapping helpers, legacy DIG encoder parameter packing, PHY ID mapping, PHY clock source mapping, and engine-to-ATOM encoder mapping.

## Control Flow
No executable control flow is present. The included DCE helper headers make the family-specific table providers visible to the implementation.

## State And Persistence
The header defines no state. It exposes functions that either return static helper tables or fill caller-provided outputs.

## Dependencies And Integration Points
It includes DCE60 conditionally, DCE80, DCE110, DCE112, and `command_table_helper_struct.h`. It is included by legacy command-table code and DCE-specific helper implementations.

## Risks
Because the interface exposes raw ATOM conversion helpers, callers must know which helper fields are valid for their DCE generation. The header shape also ties SI/DCE6 availability to build configuration.

## Test Signals
Build coverage for all enabled DCE configs catches missing helper providers. Runtime light-up on DCE6, DCE8, DCE11, and DCE11.2 validates the dispatch table selection.
