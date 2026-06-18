<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Kconfig

Purpose: Defines kernel configuration entries for the Qualcomm Atheros WCN3660/WCN3680 mac80211 driver and its debugfs support.

Important APIs/types/functions: Provides `config WCN36XX` as a tristate depending on `MAC80211`, `HAS_DMA`, optional `QCOM_WCNSS_CTRL`, and optional `RPMSG`; provides `config WCN36XX_DEBUGFS` depending on `WCN36XX`.

Control flow: Kconfig dependency resolution controls whether the driver and debugfs code are built.

State and persistence: Build-time configuration only.

Dependencies and integration points: Integrates with kernel wireless, DMA, Qualcomm WCNSS control, RPMSG, and debugfs configuration.

Risks and test signals: Risks include invalid dependency combinations hiding the driver or enabling it without platform messaging support. Test signals are allmodconfig/allyesconfig coverage and module build as `wcn36xx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Kconfig -->
