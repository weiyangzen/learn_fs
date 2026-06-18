# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/core.c

Purpose: implements WCC-specific brcmfmac firmware-vendor operations.

Important APIs and functions: `brcmf_wcc_set_sae_pwd()` maps SAE password setup to `brcmf_set_wsec()` using `BRCMF_WSEC_PASSPHRASE`. `brcmf_wcc_alloc_fweh_info()` allocates a flexible `struct brcmf_fweh_info` sized for `BRCMF_WCC_E_LAST` event handlers, initializes `num_event_codes`, and stores it on the driver. `brcmf_wcc_ops` exports these operations through the firmware-vendor abstraction.

Control flow: vendor registration in `module.c` publishes `brcmf_wcc_ops`; the brcmf core calls these hooks when handling SAE credentials and firmware event handler setup for WCC devices.

State and persistence: allocates `drvr->fweh` as kernel heap state tied to the brcmf driver lifetime. SAE password data comes from cfg80211 crypto settings and is sent to firmware rather than persisted here.

Dependencies and integration: depends on brcmf core, bus, fwvid, cfg80211, and flexible allocation helper `kzalloc_flex()`. It integrates with the generic vendor hook table `struct brcmf_fwvid_ops`.

Risks and test signals: event-code count must match firmware event IDs. Allocation failure should abort attach cleanly. SAE password length and lifetime should be validated by callers. Test WCC module load, driver attach, event dispatch setup, and WPA3 SAE connection paths.
