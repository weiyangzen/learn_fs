# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw.h

## Purpose
`cpsw.h` is the small public header shared by TI CPSW driver pieces. It provides MAC address packing helpers and declarations for external platform helpers used by the CPSW drivers.

## Important APIs, Types, And Functions
`mac_hi(mac)` and `mac_lo(mac)` pack a six-byte Ethernet address into the two register values used by CPGMAC slave source-address registers. `cpsw_phy_sel()` is declared when `CONFIG_TI_CPSW_PHY_SEL` is enabled and replaced by an empty inline otherwise, allowing callers to configure legacy GMII selection without conditional call sites. `ti_cm_get_macid()` is declared as a TI control-module MAC address fallback.

## Control Flow
This header has no independent control flow. Its macros are used by `cpsw_set_slave_mac()` in `cpsw_priv.c`, while `cpsw_phy_sel()` and `ti_cm_get_macid()` are called during DT/probe and slave open paths in `cpsw.c` and `cpsw_new.c`.

## State And Persistence
The header owns no mutable state. The packed MAC values are transient register-write inputs. The optional `cpsw_phy_sel()` stub preserves build-time behavior by turning absent PHY select support into a no-op rather than a runtime branch.

## Dependencies And Integration Points
It includes `linux/if_ether.h` and `linux/phy.h`, and integrates CPSW with optional TI PHY select code and TI control-module MAC ID lookup.

## Risks
The `mac_hi()`/`mac_lo()` byte order must match CPSW register layout; changing it would silently break programmed source MACs. The no-op `cpsw_phy_sel()` path means boards without the PHY select driver must rely on an alternative PHY interface configuration path.

## Test Signals
Test by verifying slave `SA_HI`/`SA_LO` register values match the netdev MAC, booting configurations with and without `CONFIG_TI_CPSW_PHY_SEL`, and confirming MAC fallback through `ti_cm_get_macid()` when DT lacks a valid address.
