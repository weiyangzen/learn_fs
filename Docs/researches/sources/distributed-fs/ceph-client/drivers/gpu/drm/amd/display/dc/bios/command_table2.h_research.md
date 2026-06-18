# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table2.h

## Purpose
This header declares the firmware-parser variant of the BIOS command dispatch table.

## Important APIs, Types, And Functions
- `struct cmd_tbl` defines function pointers for firmware command operations. Compared with the legacy header, it omits select-CRTC-source, DAC load detection, and some legacy DAC action signatures, and adds `get_smu_clock_info` and `enable_lvtma_control`.
- `dal_firmware_parser_init_cmd_tbl(struct bios_parser *bp)` initializes the table.

## Control Flow
The header defines the callable surface used after `command_table2.c` probes firmware command revisions and assigns handlers.

## State And Persistence
The populated function table persists within `struct bios_parser` for the parser lifetime.

## Dependencies And Integration Points
The header is tied to firmware parser internals and DC BIOS parameter structures. The added SMU and LVTMA hooks connect display clock management and embedded-panel power sequencing to firmware/DMUB paths.

## Risks
This header reuses the name `struct cmd_tbl`, so it must not be included in a translation unit expecting the legacy layout at the same time. Nullable function pointers and variant-specific fields require parser wrappers to use the correct parser type.

## Test Signals
Build coverage should catch mismatched parser layout use. Runtime coverage should exercise firmware-parser command availability on DCN-era ASICs and verify that SMU/LVTMA pointers are initialized.
