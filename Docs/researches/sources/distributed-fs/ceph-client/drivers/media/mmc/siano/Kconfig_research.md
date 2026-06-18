# sources/distributed-fs/ceph-client/drivers/media/mmc/siano/Kconfig

Purpose: Kconfig options for Siano SMS1xxx Mobile Digital TV devices connected through SDIO.

Important APIs/types/functions: defines `SMS_SDIO_DRV`, a tristate "Siano SMS1xxx based MDTV via SDIO interface". It depends on `DVB_CORE`, `HAS_DMA`, `MMC`, and the conditional RC core expression; it selects `MEDIA_COMMON_OPTIONS` and `SMS_SIANO_MDTV`.

Control flow: when selected, the SDIO transport driver and shared Siano common stack are built so SDIO boards can register with the Siano core.

State/persistence: kernel configuration symbol only.

Dependencies/integration: integrates the MMC/SDIO bus with DVB core, DMA-capable systems, optional RC support, and common Siano media code.

Risks/test signals: dependency combinations with `RC_CORE` are easy to regress. Kconfig tests should cover built-in/module configurations for DVB, MMC, RC, and common Siano options, and verify that selecting SDIO pulls required common code.
