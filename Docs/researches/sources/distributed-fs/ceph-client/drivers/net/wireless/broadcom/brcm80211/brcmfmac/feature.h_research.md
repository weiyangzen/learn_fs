# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.h

Purpose: Enumerates firmware feature bits and chip quirk bits and declares feature attach/query APIs.

Important APIs/types/functions: `BRCMF_FEAT_LIST` expands to features including MBSS, MCHAN, PNO, WOWL, P2P, RSDB, TDLS, scan random MAC, WOWL subfeatures, MFP, GSCAN, FWSUP, monitor formats, DOT11H, SAE/FWAUTH, OBSS dump, scan v2, PMKID v2/v3, and SAE_EXT. `BRCMF_QUIRK_LIST` defines AUTO_AUTH and NEED_MPC.

Control flow: `feature.c` expands these macros into enum values and names; other modules query feature bits before optional behavior.

State and persistence behavior: No state; enum values map to bits in `brcmf_pub`.

Dependencies and integration points: Used by core monitor RX, cfg80211, PNO/WOWL/scan, and vendor modules.

Risks: Enum order is effectively part of the module parameter `feature_disable` bitmask; inserting in the middle changes user-visible masks.

Test signals: Compile all feature users; runtime feature_disable should clear intended bits; debugfs names should align with enum order.
