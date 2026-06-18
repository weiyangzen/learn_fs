# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/dmi.c

Purpose: Provides DMI-based board-type selection for systems with Broadcom/Cypress Wi-Fi modules, especially devices with generic or misleading firmware board identifiers.

Important APIs/types/functions: `struct brcmf_dmi_data`, sorted `dmi_platform_data[]` quirk table, static fallback `dmi_board_type`, and `brcmf_dmi_probe()`.

Control flow: Settings creation calls `brcmf_dmi_probe()` when platform data is absent. The function first applies chip/revision-matching DMI quirks, then falls back to `sys_vendor-product_name`.

State and persistence behavior: Writes a static or constant board type pointer into per-device settings. No file persistence.

Dependencies and integration points: Uses Linux DMI APIs and Broadcom hardware IDs. Selected board type influences firmware/NVRAM alternate path lookup.

Risks: Generic DMI strings can still false-match or miss devices. The fallback static buffer is global and can be overwritten on multi-device systems. Board type strings must match linux-firmware naming.

Test signals: Listed devices should request quirk board firmware; unlisted systems should use vendor-product fallback; chip/revision mismatch should not apply quirks.
