# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/tools/csv_collection.py

## Purpose
This helper module loads a set of semicolon-delimited routing CSV files into a dictionary-of-dictionaries shape used by the route generators.

## Important APIs, Types, And Functions
`CSVCollection` subclasses `dict`. Class attributes define `delimiter = ';'`, `quotechar = '"'`, and `source_column_name = 'Sources / Destinations'`. Its constructor accepts a glob pattern plus options for skipping commented lines and stripping cell contents. Each CSV file becomes one dictionary entry keyed by the file basename without extension; rows become `source -> {destination: cell}` mappings with blank and commented fields removed.

## Control Flow
The constructor expands `glob.glob(pattern)`, opens each file with `csv.DictReader`, filters rows whose source column starts with `#` or is blank, filters destination columns or cell values that are blank/commented, removes empty row dictionaries, and stores the result.

## State And Persistence
It only builds in-memory dictionaries. There are no writes or persistent state. Consumers decide whether to generate C or CSV from the loaded data.

## Dependencies And Integration Points
It depends only on Python standard modules `os`, `csv`, and `glob`. `convert_csv_to_c.py`, `convert_py_to_csv.py`, and `make_blank_csv.py` use its delimiter and source-column contract.

## Risks
The default comment handling uses a sentinel string when comments are disabled, which is simple but non-obvious. Duplicate source rows in a CSV will be overwritten by later rows because dictionaries are used. `glob.glob()` ordering is filesystem-dependent unless consumers sort later; the generator classes do sort sheets before output.

## Test Signals
Unit tests should feed temporary CSVs with blank cells, commented rows, commented columns, whitespace, and duplicate keys. Integration tests should ensure loaded dictionaries produce stable C output via `convert_csv_to_c.py`.
