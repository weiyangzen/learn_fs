# sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.h

## Purpose
This header defines the OPEN Alliance 1000BASE-T1 HDD.TDR bit layout and declares helper functions for converting TDR status and distance into Linux-facing diagnostics.

## Important APIs, Types, and Functions
Important definitions include activation masks/values, TDR status mask and status constants for short, open, noise, cable OK, test in progress, and test not possible, plus distance mask and special no-error/resolution-not-possible values. It declares `oa_1000bt1_get_ethtool_cable_result_code()` and `oa_1000bt1_get_tdr_distance()`.

## Control Flow
The header has no runtime control flow. Its constants are consumed by the companion C file and by drivers that need to program or interpret OPEN Alliance TDR registers.

## State and Persistence
There is no state. The header is a compile-time contract for bit interpretation.

## Dependencies and Integration Points
It uses `GENMASK()` and `u16` types from kernel headers included by consumers. It is intended for automotive Ethernet PHY drivers implementing OPEN Alliance advanced diagnostics.

## Risks
Because the actual register offset is device-specific, callers must not assume this header identifies where to read. Vendors may extend or vary the semantics, especially around distance resolution and in-progress/not-possible states.

## Test Signals
Build coverage for consumers, plus conversion tests through the C helper, are sufficient. Static checks should catch missing bitfield include dependencies in consumers.
