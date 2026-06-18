# sources/distributed-fs/ceph-client/include/linux/phy/phy-hdmi.h

## Purpose
HDMI configuration payload for the generic PHY framework, covering TMDS and FRL style operation.

## Important APIs, Types, and Functions
Defines `enum phy_hdmi_mode` with `PHY_HDMI_MODE_TMDS` and `PHY_HDMI_MODE_FRL`, plus `struct phy_configure_opts_hdmi` containing bits per color channel and either TMDS character rate or FRL per-lane rate/lane count.

## Control Flow
No inline logic. Display consumers select mode-specific fields before calling PHY validate/configure operations.

## State and Persistence
The structure is transient. Applied clocking and lane/rate settings persist in HDMI PHY hardware.

## Dependencies and Integration Points
Included by generic PHY `union phy_configure_opts` and used by HDMI display controller/bridge PHY providers.

## Risks
The union requires callers and providers to agree on TMDS versus FRL mode outside the structure. Wrong rate, lane, or color-depth assumptions can cause failed HDMI training or unstable output.

## Test Signals
HDMI mode-set tests for TMDS and FRL, PHY validation of rate/lane combinations, and display compliance tests.
