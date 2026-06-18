# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/tools/convert_py_to_csv.py

## Purpose
This script converts `ni_values.py`, produced from C route tables, into editable CSV files separated into route-value family sheets and device-route board sheets.

## Important APIs, Types, And Functions
`iter_src_values(D)` yields `(src, value)` pairs for route-value dictionaries. `iter_src(D)` yields `(src, 1)` for device-route dictionaries where only route presence matters. `create_csv(name, D, src_iter)` transforms destination-major dictionaries into source-major CSV rows, maps numeric constants back to names with `value_to_name`, and writes semicolon-delimited CSV. `to_csv()` creates `csv/route_values` and `csv/device_routes`, then exports all families and devices from `ni_values`.

## Control Flow
On execution, `to_csv()` ensures output directories exist. For each route-value family and device, it builds a sorted source dictionary and writes a header containing all destination names plus `Sources / Destinations` as the first column.

## State And Persistence
The script writes CSV files under `csv/`. It overwrites target files directly. It does not mutate source C files or `ni_values.py`.

## Dependencies And Integration Points
It depends on `ni_values.py`, `CSVCollection.source_column_name`, and `ni_names.value_to_name`, which itself depends on generated `comedi_h.py`. It is invoked by the Makefile's `csv-files` target.

## Risks
Any numeric signal missing from `value_to_name` will fail conversion. Directory creation catches all exceptions, so real filesystem errors can be hidden until file writes fail. Output ordering is numeric by source/destination, which is good for diffability but depends entirely on correct `comedi_h.py` constants.

## Test Signals
Run `make csv-files` and verify route-value/device-route CSV files appear with semicolon delimiters and named signal headers. Round-trip tests should compare C -> Python -> CSV -> C output for representative route-value markers and device route presence.
