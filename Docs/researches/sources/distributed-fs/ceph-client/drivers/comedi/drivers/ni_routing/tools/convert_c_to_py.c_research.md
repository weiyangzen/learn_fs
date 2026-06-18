# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/tools/convert_c_to_py.c

## Purpose
This standalone C utility converts checked-in generated NI routing C tables into a Python dictionary file, `ni_values.py`, while preserving route-value marker status for maintenance.

## Important APIs, Types, And Functions
It defines small kernel type aliases, `BIT()`, `__user`, and `NI_ROUTE_VALUE_EXTERNAL_CONVERSION` so it can include kernel routing sources in user space. It includes `../ni_route_values.c`, `../ni_device_routes.c`, and generated `all_cfiles.c`. `family_write()` writes `ni_route_values` entries as `family -> dest -> src -> "V/I/U(value)"`. `device_write()` writes `ni_device_routes` entries as `device -> dest -> [src...]`. `is_valid_ni_sig()` validates signals against `NI_NAMES_BASE` and `NI_NUM_NAMES`. `main()` opens `ni_values.py`, writes both dictionaries, and exits.

## Control Flow
The program iterates `ni_all_route_values[]` and `ni_device_routes_list[]` until null sentinels. Within family tables it scans every destination/source cell, skips zeroes, validates marker bits with `MARKED_V/I/U`, and writes unmarked values. Within device route tables it validates each destination and source before serializing.

## State And Persistence
The only persistent output is `ni_values.py`. There is no retained runtime state after process exit. It exits immediately on invalid marker or invalid NI signal value, making the generated file all-or-nothing only in a coarse sense; it writes directly to the target file rather than via a temporary file.

## Dependencies And Integration Points
It is built by the tools Makefile after `all_cfiles.c` and local `linux/comedi.h` are generated. Its output is consumed by `convert_py_to_csv.py`. It relies on the header's external conversion mode to widen `register_type` and expose `MARKED_*` macros.

## Risks
Including `.c` files directly is fragile: symbol collisions or new kernel-only dependencies can break this utility. The output uses Python syntax with comments, not JSON, despite JSON-like comments in source. Direct writes to `ni_values.py` can leave partial files on interruption. Marker validation is strong, but route-value semantic validation is limited to signal ranges.

## Test Signals
`make csv-files` exercises compilation and conversion. A good regression test intentionally inserts an invalid marker or out-of-range signal and verifies the tool fails. Round-trip tests should compare regenerated CSV with expected route-value and device-route sheets.
