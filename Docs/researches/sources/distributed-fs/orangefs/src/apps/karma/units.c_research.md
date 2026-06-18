# sources/distributed-fs/orangefs/src/apps/karma/units.c

## Purpose
`units.c` provides unit-selection helpers for Karma graph labels and detail tables. It chooses a human-scale divisor and abbreviation for time, byte sizes, counts, and operation rates.

## Important APIs, Types, and Functions
The public functions are `gui_units_time(uint64_t, float *)`, `gui_units_size(PVFS_size, float *)`, `gui_units_count(uint64_t, float *)`, and `gui_units_ops(PVFS_size, float *)`. Each function walks a static descending table of divisors and returns the first unit where value/divisor is greater than 1.0, falling back to the base unit. The selected divisor is returned through the pointer argument.

## Control Flow
All four helpers are table scans with identical structure. There is no allocation and no external I/O.

## State and Persistence
The tables and abbreviation arrays are static read-only process data. No persistent state is used. Returned strings point to static storage and must not be freed or modified.

## Dependencies and Integration Points
The file depends on `karma.h` for `PVFS_size` and prototypes. It is used by `prep.c` and `details.c` to keep units consistent across graphs and tables.

## Risks and Edge Cases
The threshold uses `> 1.0`, so exactly 1 KB displays as bytes, exactly 1 MB displays as KB, and so on. Float divisors and casts can lose precision for very large 64-bit values. The count labels include words such as "million" while size labels use abbreviations, so UI text is not stylistically uniform.

## Test Signals
Boundary tests should cover 0, 1, exact unit thresholds, just-over thresholds, and very large values for each helper. Verify divisor and returned label pairs, especially exact powers of 1024/1000.
