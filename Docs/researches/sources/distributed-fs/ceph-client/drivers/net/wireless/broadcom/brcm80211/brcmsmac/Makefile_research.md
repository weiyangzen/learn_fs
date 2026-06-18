# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/Makefile

Purpose: Kbuild fragment for the Broadcom 802.11n SoftMAC driver module `brcmsmac`.

Important build objects: include paths cover the brcmsmac directory, `phy/`, and shared brcm80211 includes. `brcmsmac-y` composes the module from mac80211 interface, ucode loader, A-MPDU, antenna selection, channel/regulatory, main, PHY shim, PMU, rate, space-time formatting, AI utilities, PHY implementations/tables/qmath, DMA, trace events, and debug support. LED support is conditional on `CONFIG_BRCMSMAC_LEDS`; the module is selected by `CONFIG_BRCMSMAC`.

Control flow: build-time only. Runtime initialization is in the object files listed here.

State and persistence: no runtime state. Build outputs and configuration decide which features are present.

Dependencies and integration: integrates brcmsmac into Linux Kbuild and mac80211/cfg80211 driver stack.

Risks and test signals: missing object entries cause unresolved symbols or feature loss. Include path changes affect cross-file private headers. Test allmodconfig/module builds, `CONFIG_BRCMSMAC_LEDS` on/off, and trace/debug configurations.
