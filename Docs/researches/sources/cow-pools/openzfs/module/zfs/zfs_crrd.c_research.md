# File Research: sources/cow-pools/openzfs/module/zfs/zfs_crrd.c

## Summary
Implements compact round-robin databases mapping timestamps to TXGs for recent, daily, and monthly history.

## Main Responsibilities
- Maintains fixed-size circular RRD arrays.
- Adds timestamp/TXG entries with overwrite-on-full behavior.
- Maintains minute, day, and month databases in one `dbrrd_t`.
- Queries closest TXG using floor or ceiling rounding.

## Key APIs
- `rrd_tail_entry()`
- `rrd_tail()`
- `rrd_len()`
- `rrd_entry()`
- `rrd_get()`
- `rrd_add()`
- `dbrrd_add()`
- `dbrrd_query()`

## Important Behavior
`rrd_add()` updates the tail entry if the timestamp matches and the new TXG is greater; otherwise it appends and advances the circular tail, moving the head when full.

`dbrrd_add()` stores at most one monthly record every 30 days, one daily record every 24 hours, or otherwise a minute-resolution record. It rejects backwards time movement by requiring nonnegative differences from the current tail.

`dbrrd_query()` queries all three databases and chooses the entry closest to the requested timestamp.

## Risks
The data is explicitly approximate. Clock jumps into the future can suppress new entries after time moves back. Query is linear over small fixed arrays rather than binary search.
