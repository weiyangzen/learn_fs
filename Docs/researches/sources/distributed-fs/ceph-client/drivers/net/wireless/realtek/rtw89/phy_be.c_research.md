# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy_be.c

## Purpose
`phy_be.c` implements the 802.11be generation-specific PHY definition for rtw89. It supplies BE and BE v1 register maps, BB gain table parsing, RF NCTL preinitialization, BB-wrapper initialization, channel-info setup, RFSI/bandedge controls, and TX power programming for by-rate, rate-offset, regulatory limits, and RU limits up to 320 MHz. The file exports `rtw89_phy_gen_be` and `rtw89_phy_gen_be_v1`, which generic PHY code reaches through `rtwdev->chip->phy_def`.

## Important APIs, types, and functions
- Static register descriptors `rtw89_ccx_regs_be`, `rtw89_ccx_regs_be_v1`, `rtw89_physts_regs_be*`, `rtw89_cfo_regs_be*`, and `rtw89_bb_wrap_regs_be*` map generic CCX, PHY status, CFO, and BB-wrapper operations onto BE register addresses and masks.
- `rtw89_phy0_phy1_offset_be()` and `_be_v1()` calculate PHY1 register offsets for selected register page ranges.
- `union rtw89_phy_bb_gain_arg_be` decodes packed BB gain-table addresses into config type, gain band, path, bandwidth, and subtype fields.
- `rtw89_phy_config_bb_gain_be()` routes BB gain table entries to gain-error, replacement-offset, op1dB, or direct PHY write handling, with bounds checks against path, bandwidth, gain-band, and EFUSE RFE type.
- `rtw89_phy_preinit_rf_nctl_be()` and `_be_v1()` program IQK/DPK resets and clock gates before RF NCTL use, with DBCC-aware PHY1 handling for the non-v1 map.
- BB-wrapper helpers initialize per-MACID power limits, TX path maps, TPU registers, force-control bits, FTM power registers, listen-path state, uplink power thresholds, RFSI QAM/DPD/CIM3K compensation, and bandedge controls.
- Exported `rtw89_phy_bb_wrap_set_rfsi_ct_opt()` and `rtw89_phy_bb_wrap_set_rfsi_bandedge_ch()` are callable by other chip code to update RFSI control and bandedge channel state.
- `rtw89_phy_set_txpwr_byrate_be()`, `rtw89_phy_set_txpwr_offset_be()`, `rtw89_phy_set_txpwr_limit_be()`, and `rtw89_phy_set_txpwr_limit_ru_be()` implement the TX power callbacks installed in the generation definitions.

## Control flow and state behavior
Generation setup is declarative at the bottom of the file: two exported `struct rtw89_phy_gen_def` instances point generic code to the proper register maps and callback functions. BE uses CR base `0x20000`; BE v1 uses base `0x0` with BE4 register names. During PHY initialization, generic code calls `preinit_rf_nctl`, then optional BB-wrapper and channel-info hooks. The BB-wrapper path clears per-MACID limit/path tables, zeroes by-rate/RU/rate-offset power pages, disables force paths, initializes FTM, and applies additional RFSI controls for RTL8922D or uplink power thresholds for RTL8922A. If DBCC is enabled, initialization is repeated for MAC1.

BB gain parsing is table-driven. A packed `reg->addr` is decoded, rejected if out of bounds, and then stored into `rtwdev->bb_gain.be` arrays for LNA/TIA gain error, replacement offsets by bandwidth/subchannel, or op1dB data. Flow-control-looking addresses are rejected, bypass config type is ignored, and config type 4 is only meaningful for EFUSE `rfe_type >= 50`. These writes persist in runtime driver memory rather than immediate hardware except for config type 15, which writes a PHY register.

TX power programming builds contiguous hardware pages. By-rate programming iterates bandwidths from 20 through 320 MHz and NSS 1-3 encodings up to `RTW89_NSS_2`, skips unsupported combinations for CCK and special single-NSS sections, reads signed table entries through `rtw89_phy_read_txpwr_byrate()`, packs four signed bytes per word, and writes via `rtw89_mac_txpwr_write32()`. Limit programming fills `struct rtw89_txpwr_limit_be` for the current channel width using center/primary channel arithmetic, including 40 MHz offset minimum fields, then writes a 76-byte page per NSS. RU limit programming similarly fills 16 RU subchannel slots and writes an 80-byte page per NSS.

## Dependencies and integration points
The file includes `chan.h`, `debug.h`, `mac.h`, `phy.h`, and `reg.h`. It depends on register constants from `reg.h`, channel helpers such as `rtw89_mgnt_chan_get()`, MAC-index helpers such as `rtw89_mac_reg_by_idx()` and `rtw89_mac_check_mac_en()`, MMIO helpers, EFUSE RFE data, chip ID/CID fields, DBCC state, and generic TX power readers. The exported generation definitions are consumed by BE chip descriptions. The exported RFSI helpers integrate with chip-specific channel and RF code that needs to refresh bandedge controls after channel changes.

## Risks and edge cases
- Register maps differ sharply between BE and BE v1; assigning the wrong `phy_def` will write plausible but incorrect addresses.
- Channel arithmetic for 40/80/160/320 MHz assumes valid center channels. Invalid channel descriptors can underflow unsigned channel calculations.
- TX power layouts depend on `struct rtw89_txpwr_limit_be` and `struct rtw89_txpwr_limit_ru_be` byte ordering matching hardware pages.
- `rtw89_phy_bb_wrap_flush_addr()` contains a special RTL8922D CID7025 workaround that only runs when the device is marked running; missed flushes could leave stale MACID power tables.
- BB gain config type 4 is warned for non-eFEM RFE types after falling through to the default case, so table authors need to keep RFE-conditional data aligned.
- RFSI compensation setup is heavily chip-ID gated. New BE chips may need additional handling rather than inheriting RTL8922A/RTL8922D assumptions.

## Test signals
Useful signals include successful probe with `rtw89_phy_gen_be` or `_be_v1`, BB gain table loading without unknown-type warnings, no register access faults during RF NCTL preinit, correct DBCC MAC1 BB-wrapper initialization, channel-info reports after `ch_info_init`, TX power debug logs for by-rate/limit/RU programming on 20/40/80/160/320 MHz channels, regulatory power values matching table data, and stable RTL8922D bandedge/RFSI behavior at 2 GHz, 5 GHz, and 6 GHz edge channels.
