# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcm_hw_ids.h

Purpose: Centralizes Broadcom/Cypress wireless vendor, chipcommon, USB, PCIe, and brcmsmac device IDs.

Important APIs/constants: Defines Broadcom, LG, Linksys, Cypress USB vendor IDs, Broadcom PCIe vendor ID, many `BRCM_CC_*` and `CY_CC_*` chip IDs, USB device IDs, PCIe device IDs, and legacy brcmsmac D11N IDs for BCM4313/43224/43225/43236 plus chip IDs.

Control flow and state: No executable code or state. It is a compile-time ID database used for device matching and chip-specific branching.

Dependencies and integration: Includes Linux PCI and SDIO ID headers to reuse standard vendor constants. It feeds Broadcom bus/probe tables and chip ID checks such as PMU delay selection. Risks include stale or duplicated IDs, decimal versus hex notation confusion, and mismatches causing device probe failures or wrong chip-specific workarounds. Test signals include modalias/probe matching, device table coverage, chip-ID-specific paths, and comparison with kernel PCI/USB/SDIO tables.
