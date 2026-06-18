# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_phycfg.c

Purpose: this file implements RTL8723B baseband and RF register access, MAC/BB/RF configuration loading, TX power programming, and channel/bandwidth switching.

Important APIs and functions: `PHY_QueryBBReg_8723B` and `PHY_SetBBReg_8723B` read/write masked BB register fields using `phy_CalculateBitShift`. `PHY_QueryRFReg_8723B` and `PHY_SetRFReg_8723B` wrap RF serial read/write over the HSSI/LSSI BB registers initialized by `phy_InitBBRFRegisterDefinition`. `PHY_MACConfig8723B`, `PHY_BBConfig8723B`, and `PHY_RFConfig8723B` load ODM header-file tables and perform RF LCK. TX power APIs include `PHY_SetTxPowerIndex`, `PHY_GetTxPowerIndex`, and `PHY_SetTxPowerLevel8723B`. `PHY_SwChnl8723B` and `PHY_SetSwChnlBWMode8723B` update runtime channel and bandwidth.

Control flow: BB config first initializes RF register definitions, enables BB/RF clocks and resets, applies MAC/BB/AGC tables, initializes TX-power-by-rate and optional power-limit tables, and applies crystal-cap settings. RF config delegates to `PHY_RF6052_Config8723B` and then performs LCK. Channel/bandwidth changes stage new values in `hal_com_data`, apply RF channel bits and BB bandwidth registers, then reprogram TX power for the current channel.

State and persistence: `hal_com_data` stores `PHYRegDef`, `CurrentChannel`, `CurrentChannelBW`, primary side-channel offsets, `RfRegChnlVal`, antenna diversity configuration, and EEPROM-derived power tables. Register writes persist in hardware until reset or a later channel/bandwidth operation.

Dependencies and integration: uses ODM config routines (`ODM_ReadAndConfig_MP_8723B_MAC_REG`, `ODM_ConfigBBWithHeaderFile`, `ODM_ConfigRFWithHeaderFile`) and common power-limit helpers declared in `hal_com_phycfg.h`. SDIO HAL init calls MAC, BB, and RF config in sequence, and xmit descriptor mapping reads current bandwidth state from `hal_com_data`.

Risks and test signals: masked register writes depend on correct bit masks; RF serial reads require timing delays and correct RF path definitions. Channel switching rolls state forward before applying hardware writes and only rolls back when the adapter is already stopped/removed. Tests should cover legal/illegal channels, 20/40 MHz transitions, crystal-cap programming, TX power for CCK/OFDM/MCS rates, antenna-diversity path selection, and init failure propagation from ODM table loading.
