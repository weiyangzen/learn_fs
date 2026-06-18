# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-basstreble.h

## Purpose

This header provides TAS3004 bass and treble lookup tables used by the TAS codec driver to convert ALSA control indices into hardware tone-control values.

## Important APIs, types, and functions

It defines min, max, and zero constants for treble and bass, `tas3004_treble_table`, `tas3004_bass_diff_to_treble`, and inline helpers `tas3004_treble()` and `tas3004_bass()`.

## Control Flow

The treble helper directly indexes the table. The bass helper starts from the treble table and adds a compact difference table for indices 50 and above.

## State and Persistence

The lookup arrays are static const data included exactly once by `tas.c`. They encode datasheet-derived tone curves.

## Dependencies and Integration Points

It depends on kernel integer types from the includer. `tas.c` uses these helpers in tone setter callbacks and reset initialization.

## Risks and Test Signals

Risks include out-of-range indices if ALSA validation changes, table/data-sheet mismatches, and the compact bass delta hiding off-by-one errors. Tests should verify min/max/zero controls and expected hardware values at low, zero, and high tone settings.
