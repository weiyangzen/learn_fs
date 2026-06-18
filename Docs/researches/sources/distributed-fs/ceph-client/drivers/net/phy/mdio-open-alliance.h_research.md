# sources/distributed-fs/ceph-client/drivers/net/phy/mdio-open-alliance.h

## Purpose
`mdio-open-alliance.h` is a register-definition header for OPEN Alliance TC14 10BASE-T1S PHY features. It contains no executable logic; it gives PHY drivers common constants for PLCA control/status and advanced diagnostic features located in the Vendor 2 MMD.

## Important APIs, Types, And Constants
- PLCA register addresses include `MDIO_OATC14_PLCA_IDVER`, `CTRL0`, `CTRL1`, `STATUS`, `TOTMR`, and `BURST`.
- PLCA field masks include ID/version, enable/reset, node count/local ID, PLCA status, transmit opportunity timer, maximum burst count, and burst timer.
- `OATC14_IDM` names the expected PLCA MAP identifier.
- Advanced diagnostic registers include `MDIO_OATC14_ADFCAP`, `MDIO_OATC14_HDD`, `MDIO_OATC14_DCQ_SQI`, and `MDIO_OATC14_DCQ_SQIPLUS`.
- Diagnostic masks describe harness defect detection control/ready/start/valid/status bits, SQI/SQI+ capability and value fields, and the maximum 3-bit SQI level.
- `enum oatc14_hdd_status` translates two-bit harness defect status to cable OK, open, short, or not-detectable values.

## Control Flow And State Behavior
There is no runtime control flow or allocated state. Including drivers use these constants with MDIO MMD accessors, normally against `MDIO_MMD_VEND2`, to discover PLCA support, configure PLCA timing and node identity, start diagnostics, poll readiness, and interpret SQI or harness-defect results.

## Dependencies And Integration Points
The header depends on `<linux/mdio.h>` and common bit macros. It integrates with 10BASE-T1S PHY drivers and ethtool diagnostic reporting by providing source-of-truth field names for OPEN Alliance registers. It is intentionally separate from any one vendor driver so multiple PHY implementations can share the same ABI definitions.

## Risks And Edge Cases
- The header assumes the OPEN Alliance TC14 registers are in `MDIO_MMD_VEND2`; a PHY with nonstandard placement needs driver-specific handling.
- Field masks are raw register encodings, so users must use `FIELD_GET()`/`FIELD_PREP()` correctly.
- Diagnostic status may be valid only when the ready/valid bits are asserted; consumers must not treat stale register bits as fresh cable results.
- Specification comments include an external document reference; future spec revisions may add registers without preserving all semantics.

## Test Signals
Validation is mainly compile-time and consumer-driven: drivers should build with the header, read PLCA ID/version, enable/reset PLCA, configure NCNT/ID/timers, poll PLCA status, check SQI range 0-7, start harness diagnostics, wait for ready/valid, and map all four `oatc14_hdd_status` values to user-visible diagnostics.
