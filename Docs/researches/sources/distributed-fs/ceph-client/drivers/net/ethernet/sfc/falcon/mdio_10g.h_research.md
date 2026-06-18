# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.h

## Purpose
`mdio_10g.h` declares and partially implements the common Clause 45 MDIO interface used by Falcon PHY drivers. It exposes small inline wrappers around the NIC's `mdio_if_info` callbacks and prototypes the common reset, link, power, autonegotiation, and liveness helpers implemented in `mdio_10g.c`.

## Important APIs, Types, And Functions
Inline ID helpers `ef4_mdio_id_rev()`, `ef4_mdio_id_model()`, and `ef4_mdio_id_oui()` decode PHY IDs. `ef4_mdio_read()` and `ef4_mdio_write()` call `efx->mdio.mdio_read` and `mdio_write` with the current `prtad`. `ef4_mdio_read_id()` combines `MDIO_DEVID1` and `MDIO_DEVID2`. `ef4_mdio_phyxgxs_lane_sync()` double-reads PHYXS lane status and reports XAUI/XGXS alignment. The header also declares MMD reset/check/link helpers, TX disable, loopback reconfigure, low-power control, ethtool link setting update, AN restart, pause resolution, reset waiting, flag setting, and alive testing.

## Control Flow
Most call paths are thin wrappers around the active MDIO bus implementation. `ef4_mdio_phyxgxs_lane_sync()` performs two lane-status reads before checking `MDIO_PHYXS_LNSTAT_ALIGN`, matching common latched-status semantics. `ef4_mdio_set_flag()` delegates to the kernel `mdio_set_flag()` helper using the driver's bus information.

## State And Persistence
The header does not own state. Its inlines read and write external PHY registers through `efx->mdio`, and therefore persist state in the PHY's MMD registers. The effective target is controlled by `efx->mdio.prtad` and the supplied device address/register pair.

## Dependencies And Integration Points
It depends on Linux `<linux/mdio.h>`, driver `efx.h`, `struct ef4_nic`, and logging helpers. It is used by generic MDIO code and by PHY implementations such as QT202x to avoid open-coding Clause 45 access patterns. It also bridges the driver's PHY operation table with Linux ethtool and MDIO helper APIs.

## Risks
The inline wrappers assume the `efx->mdio` callbacks and `prtad` have been initialized during PHY probe. `ef4_mdio_phyxgxs_lane_sync()` declares `lane_status` without an explicit initial value but always assigns it in the fixed two-iteration loop; changing that loop would create risk. Negative MDIO read results are not handled in every inline, so callers must choose helpers appropriate for error-sensitive paths.

## Test Signals
Signals include correct PHY ID reporting, lane-sync debug logs when alignment is absent, successful MDIO flag toggles, and callers observing consistent behavior across PHY implementations. Compile coverage from all PHY drivers is important because this header is a shared interface boundary.
