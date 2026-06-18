# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.c

Purpose: reads device-tree properties into `brcmf_mp_device` platform settings, mainly for embedded/Apple ARM64 and SDIO designs.

Important APIs/functions: `brcmf_of_probe` is the public entry point. `brcmf_of_get_country_codes` parses `brcm,ccode-map` string arrays or the `brcm,ccode-map-trivial` boolean into country-code mapping settings.

Control flow and state: probe reads board type, antenna SKU, optional calibration blob, falls back to root `compatible` as board type with slashes replaced by dashes, enables optional 32.768 kHz LPO clock, and then only applies the Broadcom FMAC-compatible node-specific settings. It reads country map, MAC address, SDIO drive strength, and optional out-of-band IRQ mapping/trigger flags. Allocations use devm where appropriate; stored pointers refer to device-tree property memory or devm-managed memory.

Dependencies and integration: depends on OF APIs, clock APIs, IRQ mapping, `of_get_mac_address`, `brcmf_mp_device`, and SDIO platform data. It feeds later firmware selection, NVRAM/calibration, regulatory country mapping, MAC assignment, and OOB interrupt setup.

Risks: malformed country map strings log errors but still leave partially initialized entries. `brcmf_of_probe` dereferences `dev->of_node` for early property reads, so it assumes callers only invoke it with an OF node when `CONFIG_OF` implementation is used. Optional failures are intentionally ignored in several places, which is correct for broad platform compatibility but can make board-data issues quiet.

Test signals: DTs with explicit and trivial country maps, Apple board-type/antenna/cal-blob properties, missing OF node, deferred MAC address provider, optional LPO clock failure, SDIO drive strength, and OOB IRQ trigger mapping.
