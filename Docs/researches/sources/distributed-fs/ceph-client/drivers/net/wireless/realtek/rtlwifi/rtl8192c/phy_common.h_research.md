# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.h

## Purpose
This header declares the RTL8192C common PHY interface and constants shared by chip-specific drivers. It exposes BB/RF register accessors, PHY initialization, TX-power conversion, channel/bandwidth switching, calibration, RF power, and scan I/O control helpers.

## Important APIs, Types, And Functions
Important definitions include command-count limits, IQK register counts, EFUSE offsets, `MAX_TXPWR_IDX_NMODE_92S`, `enum swchnlcmd_id`, `struct swchnlcmd`, `enum hw90_block_e`, `enum baseband_config_type`, `enum ra_offset_area`, `enum antenna_path`, antenna-select bitfield structs, `struct efuse_contents`, and `struct tx_power_struct`. The prototypes match exported functions in `phy_common.c` and the CE-specific implementations in `phy.c`/`rf.c`.

## Control Flow
The header shapes control flow by giving chip-specific HAL ops a common PHY contract: CE code supplies table-loading and RF6052 routines, while common code calls those through `rtlpriv->cfg->ops`. Channel switching uses `struct swchnlcmd`; BB table loading uses `BASEBAND_CONFIG_PHY_REG` and `BASEBAND_CONFIG_AGC_TAB`; TX power code uses the EFUSE and MCS offset structures declared here.

## State And Persistence
The header declares data layouts but no storage. Its structures describe runtime copies of EFUSE contents and TX-power tables. Persistence remains in hardware EFUSE/EEPROM and runtime caches maintained elsewhere.

## Dependencies And Integration Points
It depends on rtlwifi types such as `struct ieee80211_hw`, `enum radio_path`, `enum wireless_mode`, `enum rf_pwrstate`, and `enum io_type`. It is included by CE PHY/HW code and is part of the internal ABI between `rtl8192c` common code and `rtl8192ce`.

## Risks And Edge Cases
There is duplicated content with `rtl8192ce/phy.h`, including the misspelled `rtl92c_phy_config_rf_with_feaderfile()` prototype. Constants such as `RT_CANNOT_IO(hw)` are hard-coded here, so behavioral changes affect every includer. Bitfield structs are layout-sensitive and should not be used as hardware ABI without endian review.

## Test Signals
Build coverage should catch prototype drift between common and CE implementations. Runtime coverage comes indirectly from probe, channel switch, TX-power update, RF power, and calibration paths that include this header.
