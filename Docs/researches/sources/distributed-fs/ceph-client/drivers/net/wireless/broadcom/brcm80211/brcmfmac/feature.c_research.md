# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.c

Purpose: Detects firmware features and chip quirks, exposes them through debugfs, and provides runtime query helpers.

Important APIs/types/functions: `brcmf_feat_attach()`, `brcmf_feat_debugfs_create()`, `brcmf_feat_is_enabled()`, and `brcmf_feat_is_quirk_enabled()`. Internal maps bind capability strings, known firmware versions, and WLC version thresholds to feature bits.

Control flow: Attach queries `"cap"`, probes iovars for GSCAN/PNO/WOWL/RSDB/TDLS/MFP/OBSS/scan random/FWSUP/SCAN_V2, reads WOWL caps, applies MBSS chip restriction, WLC and firmware overrides, calls vendor attach, applies feature-disable mask, and sets chip quirks.

State and persistence behavior: Stores feature and quirk bits in `drvr->feat_flags` and `drvr->chip_quirks`. Temporarily toggles `ifp->fwil_fwerr` for raw firmware error checks.

Dependencies and integration points: Uses fwil, bus chip ids, fwvid vendor hook, debugfs, and feature enums. Queried by cfg80211, monitor RX, scan, P2P, WOWL, and flow paths.

Risks: Any iovar result other than firmware unsupported can enable a feature, so transport errors may over-enable. Capability substring matching can be fragile. Firmware/version override tables can become stale.

Test signals: Debugfs `features`/`fwcap`; devices with known monitor firmware; WLC 12/13 PMKID; WOWL subfeatures; feature_disable mask; chip quirks.
