# sources/distributed-fs/ceph-client/include/linux/phy/phy-common-props.h

## Purpose
Common firmware-node property accessors for generic PHY polarity configuration.

## Important APIs, Types, and Functions
Declares `phy_get_rx_polarity()`, `phy_get_tx_polarity()`, `phy_get_manual_rx_polarity()`, and `phy_get_manual_tx_polarity()`. These functions parse receive/transmit polarity values for a named mode, validate them against supported flags from `dt-bindings/phy/phy.h`, and return chosen values via output pointers.

## Control Flow
No inline flow. Implementations are expected to read properties from a `struct fwnode_handle`, apply defaults, enforce supported masks, and report parse/validation errors.

## State and Persistence
No persistent state. Parsed polarity values become consumer or PHY-driver configuration state elsewhere.

## Dependencies and Integration Points
Depends on firmware-node abstractions and device-tree PHY binding constants. Integrates with PHY providers that share common RX/TX polarity properties.

## Risks
Risk centers on inconsistent binding names, unsupported polarity values being accepted, and callers ignoring `__must_check` errors.

## Test Signals
DT schema examples, fwnode property parser tests, and driver probe tests with default, automatic, and manual polarity settings.
