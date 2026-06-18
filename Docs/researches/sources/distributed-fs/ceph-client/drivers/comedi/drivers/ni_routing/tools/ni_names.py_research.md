# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/tools/ni_names.py

## Purpose
This helper extracts the set of NI global signal/terminal names from generated Python bindings for `comedi.h` and provides both name-to-value and value-to-name maps for routing CSV generators.

## Important APIs, Types, And Functions
`ni_macros` lists macro families to expand, including `NI_PFI`, `TRIGGER_LINE`, `NI_RTSI_BRD`, and counter source/gate/aux/A/B/Z/arm/output/sample-clock macros. `get_ni_names()` seeds static names `PXI_Star` and `PXI_Clk10`, expands each macro over `range(1 + f(-1) - f(0))`, adds non-callable `NI_*` enum values between `NI_COUNTER_NAMES_MAX` and `NI_NAMES_BASE + NI_NUM_NAMES`, then returns `(name_dict, val_dict)`. Module globals `name_to_value` and `value_to_name` hold those maps.

## Control Flow
All work happens at import time after `comedi_h` is imported. Macro expansion relies on the generated callable wrappers in `comedi_h.py`; enum extraction scans `comedi_h.__dict__`.

## State And Persistence
The module creates in-memory dictionaries only. No files are written. Its output affects generated CSV shape and signal-name lookup in later conversion steps.

## Dependencies And Integration Points
It depends on `comedi_h.py`, which the Makefile generates with `ctypesgen` from the kernel UAPI `comedi.h`. `convert_py_to_csv.py` and `make_blank_csv.py` consume `value_to_name`; `convert_csv_to_c.py` uses `comedi_h` directly for numeric sorting.

## Risks
The macro expansion range assumes `f(-1)` returns the last encoded value in a contiguous block relative to `f(0)`. If Comedi macro semantics change, names may be missed or over-generated. Reverse mapping drops aliases when two names have the same value, keeping only the last value in dictionary construction.

## Test Signals
Tests should assert that representative macro and enum names appear in both maps and round-trip to the expected numeric values. Alias behavior should be documented with explicit expectations for duplicate values such as board/backplane names if present.
