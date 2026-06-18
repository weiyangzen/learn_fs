# sources/distributed-fs/ceph-client/tools/perf/util/units.c

## Purpose

`units.c` provides simple unit parsing and scaling helpers for perf output and option parsing.

## Important APIs, Types, and Functions

`parse_tag_value()` parses a decimal number followed by a recognized single-character tag multiplier. `convert_unit_double()` scales values by 1000 into K/M/G and returns the scaled double plus unit char. `convert_unit()` wraps that for unsigned long. `unit_number__scnprintf()` formats byte-like numbers using 1024 steps and units B/K/M/G.

## Control Flow and State

The module has no state. Parsing walks the provided tag table and returns `(unsigned long)-1` on no match, overflow, or malformed input.

## Dependencies and Integration Points

It depends on Linux `scnprintf`, time/integer constants, and caller-provided tag tables. It is used by command-line parsers and display code.

## Risks and Test Signals

Risks include confusing 1000 vs 1024 scaling, overflow in multiplier application, and accepting embedded tag positions only when the numeric parse stops at the tag. Tests should cover valid suffixes, unknown suffixes, overflow, boundary values around 1000/1024, and formatting buffer sizes.
