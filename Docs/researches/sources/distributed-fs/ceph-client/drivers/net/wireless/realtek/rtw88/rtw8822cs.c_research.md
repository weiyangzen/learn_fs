## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cs.c

Purpose: SDIO module glue for RTL8822CS. It registers a Linux `sdio_driver` for `SDIO_DEVICE_ID_REALTEK_RTW8822CS` and passes `rtw8822c_hw_spec` to the shared rtw88 SDIO HCI implementation.

Important APIs/types: `rtw_8822cs_id_table`, `MODULE_DEVICE_TABLE(sdio, ...)`, `struct sdio_driver rtw_8822cs_driver`, `module_sdio_driver()`, and the shared entry points `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, `rtw_sdio_pm_ops`.

Control flow and state: the MMC/SDIO core matches the vendor/device ID and calls `rtw_sdio_probe()`. This file maintains no per-device state; the SDIO transport allocates `struct rtw_dev` plus `struct rtw_sdio`.

Dependencies and integration: includes MMC SDIO headers, `main.h`, `rtw8822c.h`, and `sdio.h`. It is the connection point between board SDIO enumeration and common rtw88/mac80211 registration.

Risks and test signals: primary risks are missing platform enumeration, wrong ID constants, and power-management callback mismatches. Test through module alias inspection, SDIO card probe, firmware load, RX/TX traffic, and host suspend with `MMC_PM_KEEP_POWER`.
