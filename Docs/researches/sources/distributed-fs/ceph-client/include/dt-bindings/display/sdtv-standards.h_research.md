# sources/distributed-fs/ceph-client/include/dt-bindings/display/sdtv-standards.h

## Purpose
Defines bitmask values for analog SDTV standards in device-tree display bindings. It covers PAL, NTSC, SECAM variants and aggregate masks for standard families and timing groups.

## Important APIs, Types, and Constants
Base bits include `SDTV_STD_PAL_*`, `SDTV_STD_NTSC_*`, and `SDTV_STD_SECAM_*` values. Aggregate masks include `SDTV_STD_PAL`, `SDTV_STD_NTSC`, `SDTV_STD_SECAM`, `SDTV_STD_525_60`, and `SDTV_STD_625_50`. These are bit flags, not ordinal IDs.

## Control Flow and State
No executable logic. The multi-line macros are compile-time OR expressions that define grouped capability masks. Runtime display mode state is owned by encoder/display drivers.

## Dependencies and Integration Points
Self-contained DT binding used by SDTV encoder nodes or display pipeline descriptions that advertise or select supported standards.

## Risks and Test Signals
Risk comes from treating masks as enum values, changing bit assignments, or omitting a variant from aggregate masks. Test signals include preprocessor compilation, DT schema checks, and display validation for PAL/NTSC/SECAM mode selection.
