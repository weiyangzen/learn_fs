# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Kconfig

This file defines the b43 soft-MAC Broadcom 43xx driver and its feature configuration. `CONFIG_B43` is the main tristate and depends on BCMA or SSB availability, `MAC80211`, and `HAS_DMA`; it selects firmware loading and CORDIC. A bus choice selects BCMA, SSB, or both, and dependent options cover SSB PCI host/PCICORE autoselection, SDIO, PIO fallback, PHY families, LEDs, HWRNG, and debugfs.

Important symbols include `B43_BCMA`, `B43_SSB`, `B43_BUSES_*`, `B43_SDIO`, `B43_BCMA_PIO`, `B43_PIO`, `B43_PHY_G`, `B43_PHY_N`, `B43_PHY_LP`, `B43_PHY_HT`, broken `B43_PHY_LCN` and `B43_PHY_AC`, `B43_LEDS`, `B43_HWRNG`, and `B43_DEBUG`. These symbols drive object selection in `b43/Makefile` and alter runtime capability by including or excluding bus glue, PHY code, LED support, random-number support, and debugfs.

The control flow is Kconfig evaluation: enable the main driver, choose supported buses, then expose feature options based on subsystem availability. Persistent state is only `.config`. Integration points include mac80211, BCMA, SSB, SSB SDIO/PCI support, LED class/mac80211 LED triggers, HW random, firmware loader, and Kconfig `BROKEN` gating.

Risks are invalid dependency combinations, unresolved symbols from mismatched Makefile groups, and accidentally enabling documented-broken PHYs. Test signals are a build matrix over bus/PHY/debug/LED/SDIO/HWRNG combinations and Kconfig visibility checks.
