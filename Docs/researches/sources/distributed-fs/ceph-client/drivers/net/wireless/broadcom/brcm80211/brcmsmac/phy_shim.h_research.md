# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.h

Purpose: Declares the PHY shim API and PHY-facing constants for radar classification, antenna selection/diversity, N preamble modes, transmit-power table indexing, and forced TX/RX chain selection. It is intended for inclusion by PHY-side code.

Important APIs/types: Forward declares `struct brcms_phy` and exports `wlc_phy_shim_attach/detach()` plus the `wlapi_*` service surface implemented in `phy_shim.c`. The function set covers timer allocation, timer add/delete/free, interrupt on/off/restore, SHM access, MHF updates, core reset, MAC suspend/enable, MAC frequency switching, PHY reset, bandwidth and clock controls, PHY PLL control, wake override, template RAM, rate SHM offsets, object-memory copy, and TX antenna query.

Control flow and state: This header has no executable flow. It defines the binary contract by which PHY code can request operations that mutate BMAC, MAC, clock, timer, or firmware-visible memory state through a `phy_shim_info *`.

Dependencies and integration: Includes `types.h` for common forward declarations and integer types. It integrates with PHY HAL code, the brcmsmac common layer, and board/PHY power-rate tables. Risks include duplicated antenna definitions also appearing in `pub.h`, tight coupling to Broadcom firmware table index layouts, and declarations such as `wlapi_high_update_phy_mode()` that are not implemented in the paired C file in this subset. Test signals are compile/link coverage, PHY bring-up paths, DFS/radar-related consumers, TX power table indexing, and timer/interrupt API users.
