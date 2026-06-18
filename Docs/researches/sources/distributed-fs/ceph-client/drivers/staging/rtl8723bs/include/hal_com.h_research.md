# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com.h

Purpose: this header declares shared HAL helpers and common constants used by the RTL8723BS HAL, including descriptor rates, queue selection, firmware page size, channel-plan helpers, pipe mapping, chip info, C2H, and generic hardware-variable accessors.

Important APIs/types/macros: it includes version, power/PHY/register headers and defines descriptor rates `DESC_RATE*`, `HDATA_RATE`, media status, `MAX_DLFW_PAGE_SIZE`, TX queue selection flags `TX_SELE_HQ/LQ/NQ/EQ`, and `PageNum_128`. Function declarations include `rtw_hal_data_init/deinit`, `dump_chip_info`, `hal_com_config_channel_plan`, `HAL_IsLegalChannel`, `MRateToHwRate`, `HalSetBrateCfg`, `Hal_MappingOutPipe`, `hal_init_macaddr`, C2H helpers, `SetHwReg`, `GetHwReg`, `GetHalDefVar`, and `SetHalODMVar`.

Control flow and integration: the HAL init, PHY, xmit, and SDIO ops code use these declarations as common glue. Queue-selection flags drive SDIO endpoint/page setup; rate conversion feeds TX descriptors; generic `SetHwReg`/`GetHwReg` are fallbacks for chip-specific dispatchers; C2H helpers are used by SDIO interrupt processing.

State and persistence: no state is stored here. Constants influence persistent hardware state by controlling firmware download paging, TX descriptor rates, and queue mappings.

Dependencies: pulls in multiple HAL headers, so it is a central include dependency. It assumes descriptor/register constants from included headers are consistent with RTL8723B hardware.

Risks and test signals: changing common rate constants or queue flags affects TX descriptors and SDIO pipe mapping. Tests should include rate conversion correctness, channel-plan resolution with EFUSE and registry inputs, pipe mapping for one/two/three output queues, generic hardware-variable fallback behavior, and C2H event read/clear handling.
