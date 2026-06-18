# sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.cc

## Purpose

`FileInspectorStats.cc` implements copy and move assignment for `FileInspectorStats`, including helper templates for fixed-size array members. This lets the inspector move a completed current scan into last-scan storage and copy stats safely when needed.

## Important APIs, Types, and Functions

- `clone(T(&dst)[N], const T(&src)[N])` copy-assigns each element of a fixed-size array.
- `FileInspectorStats::operator=(const FileInspectorStats&)` copies map fields, fixed arrays, counters, totals, scan time, and link statistics.
- `move(T(&dst)[N], T(&src)[N]) noexcept` move-assigns each array element and resets the source element to a default value.
- `FileInspectorStats::operator=(FileInspectorStats&&) noexcept` moves map fields and arrays, then copies scalar counters/totals/time/link fields.

## Control Flow

Both assignment operators self-check first. Copy assignment directly assigns every map and scalar and uses `clone()` for two-element array fields. Move assignment moves map fields and uses `move()` for arrays. Source array elements are reset to default values after move.

These operators are used by `FileInspector` when loading stats, moving `mCurrentStats` into `mLastStats`, resetting current stats, and potentially returning/copying stats in admin paths.

## State and Persistence Behavior

The file does not persist anything directly. It determines which in-memory stats survive copy/move operations. That matters because `FileInspector` relies on move assignment to preserve a completed scan before persisting and dumping it.

## Dependencies and Integration Points

The implementation includes `FileInspectorStats.hh`, qclient headers, and JSON helpers. The qclient/JSON includes are not directly used by the visible assignment code, but the stats type is marshalled elsewhere by `FileInspector::QdbHelper`.

## Risks and Edge Cases

- `UserBytes` is copied twice in copy assignment and moved twice in move assignment; this is redundant and likely a typo.
- `SizeBinsFiles`, `SizeBinsVolume`, `BirthVsSizeFiles`, and `BirthVsSizeVolume` exist in the header but are not copied or moved here. That means these computed histograms are lost when `mCurrentStats` is moved into `mLastStats`.
- Move assignment copies scalar fields from `other` but does not reset them in the source. This is legal for moved-from objects but can surprise debugging code.
- Extra includes may hide unused dependency drift.

## Test Signals

Tests should create a fully populated `FileInspectorStats`, copy it, move it, and assert that every field declared in the header survives in the destination. This should specifically catch missing size and birth-vs-size map handling and the duplicate `UserBytes` operation. Tests should also assert moved-from array elements are defaulted if that behavior is relied on.
