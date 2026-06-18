# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Kconfig

Purpose: provides the top-level Kconfig vendor gate for MediaTek wireless drivers. `WLAN_VENDOR_MEDIATEK` controls whether MediaTek-specific driver prompts are visible and sources the `mt7601u` and `mt76` driver families.

Important APIs/types/functions: defines `config WLAN_VENDOR_MEDIATEK` as a bool defaulting to `y`; within the vendor conditional it sources `drivers/net/wireless/mediatek/mt7601u/Kconfig` and `drivers/net/wireless/mediatek/mt76/Kconfig`.

Control flow: during kernel configuration, selecting or defaulting this vendor option to yes exposes MediaTek subdriver configuration. Selecting no hides those prompts without directly changing built objects except through the absence of selected child configs.

State and persistence: persists only in the generated kernel `.config` as `CONFIG_WLAN_VENDOR_MEDIATEK`. No runtime state exists.

Dependencies and integration: integrates with the kernel wireless Kconfig hierarchy under `drivers/net/wireless`. Child Kconfig files define actual tristate modules and dependencies.

Risks: if the vendor option is disabled, all MediaTek subdrivers become unreachable even if a user expects a specific device driver. Adding new MediaTek families requires adding a `source` line here or they will not appear in menuconfig.

Test signals: Kconfig/menuconfig coverage should verify the vendor menu appears by default, disappears when disabled, and exposes `mt7601u` and `mt76` options when enabled.
