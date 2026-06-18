# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.c

## Purpose

`hns_dsaf_xgmac.c` implements the 10G XGMAC MAC-driver backend for HNS. It supplies the `struct mac_driver` callbacks used by the DSAF MAC abstraction to reset, enable/disable, configure pause and frame behavior, query link and MAC info, collect XGMAC MIB counters, and dump XGMAC registers.

## Important APIs, Types, And Functions

The public constructor is `hns_xgmac_config`, which allocates a `struct mac_driver` and populates callback pointers. Internal helpers include TX/RX enable setters, LF/RF insertion control, PMA FEC enable, interrupt clear/mask, initialization/reset/free, pad/CRC configuration, pause frame configuration, pause MAC address programming, TX pause-time programming, max frame length programming, stats update/get/string/count helpers, link/status/info getters, and register dump routines.

The static `g_xgmac_stats_string` table maps ethtool stat names to `struct mac_hw_stats` offsets via `MAC_STATS_FIELD_OFF`.

## Control Flow

`hns_xgmac_config` is called with `hns_mac_cb` and `mac_params`, allocates a devm-managed driver, assigns IDs, mode, base address, device and MAC callback, then installs all XGMAC-specific operations. `hns_xgmac_init` toggles XGE soft reset through `dsaf_dev->misc_op`, initializes LF/RF control, clears and masks exceptions, disables FEC, and disables TX/RX. Enable/disable callbacks toggle `XGMAC_MAC_ENABLE_REG` bits and manage LF insertion state.

Stats flow is two-stage: `hns_xgmac_update_stats` reads each 64-bit XGMAC MIB register into `mac_cb->hw_stats`; `hns_xgmac_get_stats` copies fields into ethtool buffers according to the static descriptor table. Register dump reads base config, MAC, PCS, PMA, and MIB counters into a fixed 214-register array with sentinel values at the end.

## State And Persistence

XGMAC state lives primarily in hardware registers. The `mac_driver` stores static driver pointers and the MMIO base. `mac_cb->hw_stats` stores the latest sampled 64-bit counters. Pause configuration, max frame length, LF/RF insert mode, FEC, TX/RX enablement, and control bits are volatile and reinitialized on reset.

## Dependencies And Integration Points

The file depends on Linux 64-bit MMIO read support, OF MDIO headers, `hns_dsaf_main.h`, `hns_dsaf_mac.h`, `hns_dsaf_xgmac.h`, and `hns_dsaf_reg.h`. It integrates with DSAF MAC selection, ethtool stats/register callbacks, link-status reporting, pause controls, and netdev MTU/pause operations through the generic AE/MAC callback layer.

## Risks And Test Signals

Risks include missing support for autoneg/loopback callbacks in this backend, incorrect signed `char` handling when constructing pause MAC registers, stale stats if update is not called before get, and register dump count mismatches. Test signals include stable 10G link up/down reporting, correct pause enable state from ethtool, traffic counters matching hardware expectations, no XGMAC exception interrupt storms, successful reset/reopen, and valid 214-register dumps.
