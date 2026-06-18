# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.c

## Purpose
Maps AtomISP input stream formats to bits per subpixel.

## Important APIs, Types, and Functions
`sh_css_stream_format_2_bits_per_subpixel(enum atomisp_input_format format)` returns bit depths for RGB, YUV, RAW, binary, and user-defined MIPI formats. Unknown formats return `0`.

## Control Flow
The function is a switch table from `atomisp_input_format` to 4, 5, 6, 7, 8, 10, 12, 14, or 16 bits per subpixel.

## State and Persistence Behavior
No state is read or written. Results are deterministic.

## Dependencies and Integration Points
Includes `sh_css_stream_format.h` and `ia_css_stream_format.h`. It feeds input-system, formatter, or MIPI sizing logic that needs bit-depth information.

## Risks
Returning `0` for new/unhandled formats can propagate into size calculations if callers do not validate it. User-defined formats are assumed 8-bit.

## Test Signals
Unit-level checks should cover every `ATOMISP_INPUT_FORMAT_*` enumerator used by sensors and verify unknown/default handling.
