# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.c

## Purpose

`odm_CfoTracking.c` implements carrier-frequency-offset tracking for a linked RTL8723BS station. It adjusts crystal capacitance and automatic temperature compensation (ATC) based on per-packet CFO tail measurements. The source was read as a complete 210-line file.

## Important APIs, Types, and Functions

Public entry points are `ODM_CfoTrackingReset`, `ODM_CfoTrackingInit`, `ODM_CfoTracking`, and `odm_parsing_cfo`. Internal helpers are `odm_SetCrystalCap`, `odm_GetDefaultCrytaltalCap`, `odm_SetATCStatus`, and `odm_GetATCStatus`. The state is `struct cfo_tracking` inside `dm_odm_t`.

## Control Flow

PHY status parsing calls `odm_parsing_cfo` for OFDM packets, which stores path CFO tails and increments a packet counter. The watchdog calls `ODM_CfoTracking`; if support is disabled, not linked, or not exactly one station, it resets the crystal cap and ATC. Otherwise it waits for a new packet, converts CFO tail to kHz, filters an abnormal first large jump, enables or disables adjustment by high/low CFO thresholds, disables adjustment for BT coexistence, steps `CrystalCap` toward lower CFO, clamps it to six bits, writes `REG_MAC_PHY_CTRL`, and toggles ATC around the `CFO_TH_ATC` threshold.

## State and Persistence Behavior

Persistent adapter-session state includes default/current crystal cap, previous CFO average, packet counters, large-CFO filter flag, adjustment flag, and ATC status. Hardware state persists in `REG_MAC_PHY_CTRL` and `ODM_REG(BB_ATC)` until reset or rewritten.

## Dependencies and Integration Points

It depends on `dm_odm_t`, `hal_com_data->CrystalCap`, PHY BB register access, CFO fields from `struct phy_status_rpt_8192cd_t`, and the ODM watchdog. It integrates with `odm_HWConfig.c` through `odm_parsing_cfo`.

## Risks and Edge Cases

Only path A is averaged even though path B is stored. CFO adjustment is intentionally disabled when BT is enabled. Packet counter wrap is handled by resetting to zero. The default-cap accessor name has a typo but is static. Incorrect station ID handling can ignore CFO for station zero because parsing only updates when `station_id != 0`.

## Test Signals

Tests should cover no-link reset, multi-station reset, no-new-packet early return, positive and negative CFO cap adjustments, clamp at 0 and 0x3f, ATC threshold toggles, BT-enabled suppression, and packet counter wrap.
