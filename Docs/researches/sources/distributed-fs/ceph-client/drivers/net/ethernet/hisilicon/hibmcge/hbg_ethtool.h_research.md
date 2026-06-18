
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.h

## Purpose

This header defines HIBMCGE stats offset helpers and declares ethtool/stat functions.

## Important APIs, Types, and Functions

- `HBG_STATS_FIELD_OFF(f)` computes a field offset within `struct hbg_stats`.
- `HBG_STATS_R(p, offset)` reads a u64 stat through offset arithmetic.
- `HBG_STATS_U(p, offset, val)` adds a value to a u64 stat.
- It declares `hbg_ethtool_set_ops()` and `hbg_update_stats()`.

## Control Flow

No control flow is present. The macros are expanded by ethtool and diagnostics code.

## State and Persistence

No state is declared, but the macros operate on persistent `struct hbg_stats` storage.

## Dependencies and Integration Points

The header integrates stats tables in `hbg_ethtool.c` and `hbg_diagnose.c` with the shared stats layout in `hbg_common.h`.

## Risks and Edge Cases

Offset arithmetic assumes every referenced field is a `u64` and that offsets are correct for the current `struct hbg_stats` layout. Misuse on non-u64 fields would produce invalid reads/writes.

## Test Signals

Builds with all stats tables and runtime stat values matching expected counters validate this header.
