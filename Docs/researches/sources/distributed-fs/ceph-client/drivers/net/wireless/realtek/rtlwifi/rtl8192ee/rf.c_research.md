# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.c

## Purpose
`rf.c` implements RTL8192EE RF6052-specific configuration and bandwidth programming. It is a small bridge between generic PHY code and RF register-table programming for paths A/B.

## Important APIs, Types, And Functions
The exported APIs are `rtl92ee_phy_rf6052_set_bandwidth` and `rtl92ee_phy_rf6052_config`. The internal `_rtl92ee_phy_rf6052_config_parafile` prepares the RF serial interface for each path, calls `rtl92ee_phy_config_rf_with_headerfile`, and restores RF environment bits. It uses `struct rtl_priv`, `struct rtl_phy`, `struct bb_reg_def`, RF path enums, `RF_CHNLBW`, `RFREG_OFFSET_MASK`, and HSSI/3-wire bit masks from `reg.h`.

## Control Flow
`rtl92ee_phy_rf6052_config` sets `rtlphy->num_total_rfpath` to one or two based on RF type, then loads RF tables. The parafile loader loops over active RF paths, saves RFENV from path-specific BB interface registers, enables RFENV/OE, configures 3-wire address/data length, loads the path table for A/B, restores RFENV, and aborts on failure. Bandwidth changes update cached `rfreg_chnlval[0]` and write RF channel/bandwidth register on paths A and B: 20 MHz sets bits 10 and 11, while 20/40 sets bit 10.

## State And Persistence Behavior
The main software state is `rtlphy->num_total_rfpath` and `rtlphy->rfreg_chnlval[]`. Hardware RF path registers retain bandwidth and table-programmed values until another RF write or reset.

## Dependencies And Integration Points
It depends on `phy.c` for `rtl92ee_phy_config_rf_with_headerfile`, on `reg.h` for RF/BB masks, and on `dm.h`/`def.h` for surrounding driver context. It is called from `rtl92ee_phy_rf_config` during init and `rtl92ee_phy_set_bw_mode_callback` during bandwidth changes.

## Risks
Bandwidth programming writes both A and B even if only one path is active in the bandwidth helper, which is probably harmless but worth noting on 1T1R variants. RF table load failures return false, but detailed failure diagnosis depends on logs. Timing is delay-sensitive.

## Test Signals
RF init success logs, valid RF register readback after table load, correct `num_total_rfpath`, stable 20/40 MHz throughput, and no RF path B access faults on 1T1R hardware are key signals.
