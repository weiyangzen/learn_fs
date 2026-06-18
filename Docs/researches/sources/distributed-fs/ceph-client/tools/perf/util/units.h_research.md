# sources/distributed-fs/ceph-client/tools/perf/util/units.h

## Purpose

`units.h` declares unit parsing and scaling helpers.

## Important APIs, Types, and Functions

It defines `struct parse_tag { char tag; int mult; }` and declares `parse_tag_value()`, `convert_unit_double()`, `convert_unit()`, and `unit_number__scnprintf()`.

## Control Flow and State

No header-level state exists. Callers provide null-terminated tag arrays.

## Dependencies and Integration Points

It depends on Linux `u64` and standard `size_t`. It is included by option parsing and output formatting code.

## Risks and Test Signals

Callers must ensure the tag table ends with `tag == 0`. Compile tests should check declaration consistency with the implementation.
