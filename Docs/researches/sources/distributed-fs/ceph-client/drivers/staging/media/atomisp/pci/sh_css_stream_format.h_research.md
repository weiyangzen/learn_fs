# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.h

## Purpose
Declares the stream-format bit-depth helper for AtomISP CSS.

## Important APIs, Types, and Functions
Exports `sh_css_stream_format_2_bits_per_subpixel(enum atomisp_input_format format)`.

## Control Flow
No runtime flow in the header; callers include it before invoking the implementation in `sh_css_stream_format.c`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on `ia_css_stream_format.h` for `enum atomisp_input_format`. Used by input system and stream configuration code.

## Risks
Any signature drift must match the C file and all callers.

## Test Signals
Compile coverage and bit-depth tests through the C implementation.
