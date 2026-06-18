# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwvid.h

Purpose: defines the vendor-operation contract used to abstract firmware-family differences and provides inline dispatch helpers from generic `brcmfmac` code to selected vendor ops.

Important APIs/types: `struct brcmf_fwvid_ops` contains hooks for feature attach, SAE password setup, firmware event allocation, event activation, cfg80211 op selection, and event handler registration. Exported functions register/unregister vendors and attach/detach a driver to the selected vendor. Inline helpers call through `drvr->vops` or `ifp->drvr->vops`, returning `-EOPNOTSUPP`/`-EIO` when hooks are absent where appropriate.

Control flow and state: the header does not store state; it assumes `brcmf_fwvid_attach()` has populated `drvr->vops`. Some helpers tolerate missing optional hooks, while `brcmf_fwvid_feat_attach()` assumes `ifp->drvr->vops` is valid before checking `feat_attach`.

Dependencies and integration: includes firmware/vendor IDs and cfg80211 types. It is consumed by common cfg80211, feature, firmware-event, and security setup paths that need vendor-specific behavior without hard-coding a vendor.

Risks: helper nullability is uneven. Callers must know whether `drvr->vops` has been attached before invoking helpers, especially `brcmf_fwvid_feat_attach`. Optional hooks need graceful fallback behavior in callers.

Test signals: firmware variants with partial op tables, SAE password calls on unsupported vendors, event activation after attach, cfg80211 ops registration, and detach/reprobe cycles.
