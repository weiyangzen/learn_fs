<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/def.h

## Purpose
Defines RTL8821AE/RTL8812AE chip constants for rates, chip version decoding, board capabilities, RF and power states, PCI interface selection, descriptor queue selectors, CCK PHY status, and firmware H2C command descriptors.

## Important APIs, Types, And Functions
- Rate constants cover CCK, OFDM, HT MCS0 to MCS15, VHT 1SS/2SS/3SS MCS0 to MCS9, SG variants, and `MGN_UNKNOWN`.
- Hardware limits and channel constants include `WIFI_NAV_UPPER_US`, `HAL_92C_NAV_UPPER_UNIT`, `MAX_RX_DMA_BUFFER_SIZE`, `MAX_RX_DMA_BUFFER_SIZE_8812`, and primary channel offset values.
- Chip identity constants and masks include `CHIP_8812`, `CHIP_8821`, `NORMAL_CHIP`, RF type bits, vendor/cut bits, `IC_TYPE_MASK`, `RF_TYPE_MASK`, `CUT_VERSION_MASK`, and extraction helpers such as `GET_CVID_IC_TYPE`.
- Version helpers include `IS_1T1R`, `IS_1T2R`, `IS_2T2R`, `IS_8812_SERIES`, `IS_8821_SERIES`, and vendor/cut checks for 8812A and 8821A.
- Enums define `version_8821ae`, `vht_data_sc`, `board_type`, `rf_optype`, `rf_power_state`, `power_save_mode`, `power_polocy_config`, `interface_select_pci`, and `rtl_desc_qsel`.
- Structures define `phy_sts_cck_8821ae_t` and `h2c_cmd_8821ae`.

## Control Flow
The header has no executable control flow. Its macros are used by chip detection, rate mapping, descriptor construction, PHY status parsing, firmware command construction, and feature selection code throughout the RTL8821AE driver.

## State And Persistence
The values encode persistent hardware and firmware ABI meanings: chip version bits, RF path capabilities, board options such as external PA/LNA/TRSW and Bluetooth presence, power state labels, descriptor queue selectors, and H2C command buffer layout. The header itself stores no mutable state.

## Dependencies And Integration Points
Included by RTL8821AE driver components such as software registration, hardware init, firmware, PHY/RF, dynamic management, and TRX code. It aligns driver-visible constants with mac80211 rates, RTL8821/8812 hardware version registers, firmware H2C ABI, and descriptor queue selection.

## Risks And Edge Cases
Chip-version helper macros depend on masks and bit values matching hardware. A bad helper can select the wrong RF path count, board capabilities, or firmware flow. Queue selector constants must match descriptor hardware. The `power_polocy_config` spelling is part of the local ABI and should not be casually renamed. Rate constants must remain compatible with firmware/rate-adaptive tables.

## Test Signals
Signals include correct detection of 8812 versus 8821, RF type and chip cut logging, successful VHT/HT rate operation, correct queue selection for TX descriptors, firmware H2C command handling, board-type feature behavior for external front-end components, and compile coverage of all includers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/def.h -->
