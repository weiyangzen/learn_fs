# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/tools/Makefile

## Purpose
This helper Makefile orchestrates generation and round-tripping of NI routing data outside the normal kernel build. It can convert existing generated C tables into CSV, create blank CSV templates, and regenerate C files from CSV.

## Important APIs, Types, And Targets
Important targets are `csv-files`, `c-files`, `csv-blank`, `everything`, `clean-partial`, and `clean`. `comedi_h.py` is generated from `include/uapi/linux/comedi.h` with `ctypesgen`. `convert_c_to_py` is built from `convert_c_to_py.c` plus a generated `all_cfiles.c` include aggregator and local `linux/comedi.h` symlink. `ni_values.py` is emitted by running `convert_c_to_py`; CSV files are emitted by `convert_py_to_csv.py`; regenerated C files are emitted by `convert_csv_to_c.py --route_values --device_routes`.

## Control Flow
`make everything` runs `csv-files`, `c-files`, and `csv-blank`. The C-to-CSV path is `all_cfiles.c` -> `convert_c_to_py` -> `ni_values.py` -> `convert_py_to_csv.py` -> `csv/`. The CSV-to-C path is `csv/` plus `comedi_h.py` -> `convert_csv_to_c.py` -> `c/`.

## State And Persistence
Generated state is local to the tools directory: `comedi_h.py`, `ni_values.py`, `convert_c_to_py`, `all_cfiles.c`, `linux/`, `csv/`, and `c/`. `clean-partial` preserves CSV/C output but removes intermediate tool products; `clean` removes generated CSV/C and the local Linux include symlink tree.

## Dependencies And Integration Points
The Makefile depends on `ctypesgen`, GCC, the kernel UAPI `comedi.h`, and the generated/checked-in route files under `../ni_device_routes` and `../ni_route_values`. Generated `c/*.mk` fragments are intended for comparison or inclusion in `drivers/comedi/drivers/Makefile`.

## Risks
`all_cfiles.c` appends with `>>` and is not removed before regeneration unless cleaned, so repeated runs can duplicate includes. The Makefile assumes a specific relative location for `include/uapi`. Missing `ctypesgen` or incompatible Python environments will break the workflow. Generated output may lose handwritten notes if maintainers overwrite annotated files blindly.

## Test Signals
Run `make clean && make everything`, inspect that `csv/` and `c/` are produced, and diff regenerated `c/ni_routing` files against checked-in sources. A robust test should verify `all_cfiles.c` is deterministic after clean and that `convert_csv_to_c.py` emits compilable output.
