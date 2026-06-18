# sources/distributed-fs/ceph-client/fs/ntfs/collate.h

## Purpose

`collate.h` declares NTFS collation support and provides a fast inline check for supported collation rules.

## Important APIs, Types, And Functions

- `ntfs_is_collation_rule_supported(__le32 cr)` returns true for the implemented binary, filename, single ULONG, and ULONG-array rules, after checking the numeric rule range.
- `ntfs_collate()` compares two values using a selected collation rule.

## Control Flow And Usage

Index setup or validation code can call `ntfs_is_collation_rule_supported()` before accepting an index root's rule. Comparison call sites pass the volume, rule, two data pointers, and their byte lengths to `ntfs_collate()`.

## State And Persistence Behavior

The header owns no state and performs no persistence. It gates which on-disk index collation rules the driver is willing to process.

## Dependencies And Integration Points

It includes `volume.h` because comparisons require `struct ntfs_volume`, especially for filename collation through the upcase table.

## Risks And Edge Cases

The support predicate is easy to misread because of mixed `unlikely()` and `&&`/`||` precedence, but semantically it rejects rules outside the four implemented values and their expected numeric ranges. Any new collation implementation must update both the predicate and dispatcher.

## Test Signals

Tests should check support detection for each implemented constant, nearby unsupported values in the `0x00..0x02` and `0x10..0x13` ranges, and completely unknown rules.
