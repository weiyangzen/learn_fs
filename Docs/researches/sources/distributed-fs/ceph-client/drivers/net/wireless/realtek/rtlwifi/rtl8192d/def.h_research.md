
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/def.h

Purpose: Defines RTL8192D family constants, chip-version encodings, RF operation enums, descriptor queue selectors, channel plans, CCK PHY status layout, H2C command wrapper, and tx-power EEPROM data layout.

Important APIs/types: Constants include min-spacing densities, `RF6052_MAX_TX_PWR`, RSSI/link-quality window sizes, AC interrupt masks, channel offset values, and RX queue IDs. `enum version_8192d` covers test/normal 88C/92C/8723/92D variants, UMC cuts, and 92D single/dual PHY C/D/E cuts. Macros decode chip ID fields: `GET_CVID_*`, `IS_1T1R`, `IS_1T2R`, `IS_2T2R`, `IS_92D_SINGLEPHY`, `IS_92D`, and cut checks. `enum rf_optype` selects software 3-wire or firmware RF ops. `enum rtl_desc_qsel` defines firmware queue selectors. `enum channel_plan` enumerates regulatory domain plans. `struct phy_sts_cck_8192d`, `struct h2c_cmd_8192c`, and `struct txpower_info` describe hardware/firmware data.

Control flow: Header only. The macros drive chip-version branches, RF path selection, channel-plan handling, descriptor queue selection, and tx-power parsing in 8192D common code.

State and persistence: Encoded version bits persist in HAL state after probe. `struct txpower_info` holds EEPROM/efuse power calibration arrays across channels and RF paths.

Dependencies/integration: Used by 8192D common source files and likely transport-specific 8192D drivers. Relies on common bit macros and `CHANNEL_GROUP_MAX` from surrounding rtlwifi headers.

Risks: `RF_TYPE_1T1R` is defined as an inverted mask expression for comparison through `GET_CVID_RF_TYPE`; misuse outside `IS_1T1R()` can be confusing. Version bit layouts differ from 8192CU/CE, so cross-family macro reuse is unsafe. Regulatory channel-plan constants affect allowed channel behavior when consumed by common code.

Test signals: Chip-version decode tests for all 92D single/dual PHY and cut variants, RF type selection, tx-power EEPROM parsing for both RF paths, descriptor queue mapping, and country/channel-plan behavior.
