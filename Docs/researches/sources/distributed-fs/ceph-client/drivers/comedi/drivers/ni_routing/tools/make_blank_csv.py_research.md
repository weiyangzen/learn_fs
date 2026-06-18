# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/tools/make_blank_csv.py

## Purpose
This utility creates a blank routing CSV template containing every known NI signal name as both a potential source row and destination column. It helps maintainers start a new route-value family or device-route table.

## Important APIs, Types, And Functions
`to_csv()` creates `csv/blank_route_table.csv`. It builds `fieldnames` from `ni_names.value_to_name` sorted by numeric signal value, prepends `CSVCollection.source_column_name`, writes a header, and writes one row per signal with only the source column filled.

## Control Flow
When run as a script, it calls `to_csv()`. It creates the `csv` directory if needed, opens the target file, writes the header, then iterates every signal name for blank rows.

## State And Persistence
The persistent output is `csv/blank_route_table.csv`, overwritten directly. It does not read or modify existing route CSVs.

## Dependencies And Integration Points
It depends on `CSVCollection` for CSV format constants and `ni_names.value_to_name` for the signal universe. The Makefile target `csv-blank` runs this after generating `comedi_h.py`.

## Risks
It catches all exceptions from `os.makedirs`, potentially hiding non-directory filesystem issues. The generated table is only as complete as `ni_names.py`; missing macro families in `ni_names.py` become missing rows/columns here.

## Test Signals
Run `make csv-blank` and confirm the file has the expected source column, semicolon delimiters, and rows/columns for representative signals such as `NI_PFI(0)`, `TRIGGER_LINE(0)`, `PXI_Star`, and counter signals.
