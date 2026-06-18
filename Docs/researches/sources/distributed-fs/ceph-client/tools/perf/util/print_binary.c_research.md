# sources/distributed-fs/ceph-client/tools/perf/util/print_binary.c

## Purpose
This file provides a generic callback-driven binary dump formatter and a helper to identify null-terminated printable strings.

## Important APIs, Types, and Functions
Exports are `binary__fprintf` and `is_printable_array`. The printer callback receives `enum binary_printer_ops` events such as data begin, line begin, address, numeric data, padding, separator, character data, line end, and data end.

## Control Flow
`binary__fprintf` rounds `bytes_per_line` up to a power of two, iterates bytes, emits line start/address events at line boundaries, emits numeric byte data, pads incomplete final lines, emits a separator, emits printable-character phase callbacks, and ends the line/data. `is_printable_array` requires a non-null, non-empty, NUL-terminated buffer whose characters before the terminator are printable or whitespace.

## State and Persistence
There is no persistent state. All formatting state is local to one call and accumulated through callback return values.

## Dependencies and Integration Points
It depends on Linux `roundup_pow_of_two` and ctype helpers. It is used by perf output code that wants customizable binary presentation without hard-coding exact text formatting.

## Risks
`roundup_pow_of_two(0)` would be unsafe if callers pass zero bytes per line. Several callback invocations pass `-1` through an unsigned parameter, relying on callback interpretation. The separator callback return is not added to `printed`.

## Test Signals
Tests should cover full lines, partial final lines, different line widths, null callback, zero-length data, printable string detection, and callback return accounting.
