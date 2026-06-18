# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_halinit.c

Purpose: this is the RTL8723BS SDIO hardware initialization, deinitialization, interface-configuration, adapter-info, and SDIO-specific hardware-variable dispatch file.

Important APIs and functions: `rtl8723bs_hal_init` is the main bring-up sequence; `rtl8723bs_hal_deinit` and `CardDisableRTL8723BSdio` power down the device. `_InitPowerOn_8723BS` powers on MAC/SDIO blocks; queue/page setup is handled by `_InitQueueReservedPage`, `_InitTxBufferBoundary`, `_InitQueuePriority`, `_InitPageBoundary`, and `_InitTransferPageSize`. `_InitWMACSetting`, `_InitAdaptiveCtrl`, `_InitEDCA`, `_initSdioAggregationSetting`, `_InitInterrupt`, and `_InitBurstPktLen_8723BS` program runtime MAC/SDIO defaults. `ReadAdapterInfo8723BS` reads EFUSE/EEPROM fields and `SetHwReg8723BS`/`GetHwReg8723BS` add SDIO-specific hardware variables.

Control flow: init handles an IPS fast path first, otherwise powers on, downloads firmware, initializes firmware variables, detects power-down mode, configures MAC/BB/RF, records RF channel registers, sets TX/RX queue pages and LLT, programs WMAC filters, aggregation, beacon, interrupts, current channel/bandwidth, antenna selection, reserved hardware controls, dynamic management, free-page/OQT status, MAC TX/RX enable, NAV, IQK/LCK, and BT coexistence hardware config.

State and persistence: `hal_com_data` caches SDIO endpoint count/queue selection, free pages, OQT maximum, `SdioRxFIFOCnt`, `SdioRxFIFOSize`, RF type, current channel, and MAC power-control status. `pwrctrl_priv` tracks RF power state, IPS state, RPWM toggles, and pre-IPS type. EFUSE parsing populates adapter EEPROM and HAL fields.

Dependencies and integration: uses power sequence tables, firmware download from `rtl8723b_hal_init.c`, PHY/RF config, SDIO interrupt functions, BT coexistence, ODM calibration, and common adapter/MLME/power abstractions.

Risks and test signals: init has many early returns without a common unwind path, so partial initialization failures should be tested. Power-state handling differs for normal init, IPS resume, IPS suspend, and module-loaded-but-GUI-off adapter-info reads. Tests should validate firmware-ready path, missing firmware failure, LLT timeout, endpoint/page mapping for `wifi_spec`, interrupt enable/disable, RX aggregation settings, EFUSE autoload failure, random MAC fallback, deinit in netif-up/down IPS paths, and CPWM/RPWM transitions.
