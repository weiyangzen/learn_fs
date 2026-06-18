# sources/distributed-fs/ceph-client/drivers/net/phy/open_alliance_helpers.c

## Purpose
This helper file translates OPEN Alliance 1000BASE-T1 Time Delay Reflection diagnostic register values into Linux ethtool cable-test result codes and distances.

## Important APIs, Types, and Functions
It exports `oa_1000bt1_get_ethtool_cable_result_code()` and `oa_1000bt1_get_tdr_distance()` with `EXPORT_SYMBOL_GPL()`. Both operate on a 16-bit HDD.TDR-like register value using masks from `open_alliance_helpers.h`.

## Control Flow
`oa_1000bt1_get_ethtool_cable_result_code()` extracts TDR status and distance fields. Known statuses map to ethtool OK, open, same-short, and noise. Unknown statuses return resolution-not-possible when the distance field is the special `0x3f` value, otherwise unspecified. `oa_1000bt1_get_tdr_distance()` extracts the distance field, returns `-ERANGE` when resolution is not possible, or returns distance in centimeters by multiplying the meter-scale value by 100.

## State and Persistence
The file is stateless. It performs pure conversions and does not touch hardware directly.

## Dependencies and Integration Points
It depends on Linux bitfield helpers, ethtool netlink constants, errno values, and the companion header. PHY drivers that implement OPEN Alliance TDR can call these helpers after reading their device-specific diagnostic register.

## Risks
The helpers assume the caller provides a register formatted like the documented OPEN Alliance HDD.TDR layout. Distance scaling is coarse and may not match vendor-specific interpretations. The result-code helper prioritizes status except for unknown status with resolution-not-possible distance.

## Test Signals
Unit-style tests should cover every defined TDR status, the resolution-not-possible distance field, distance conversion for representative values, and unknown statuses.
