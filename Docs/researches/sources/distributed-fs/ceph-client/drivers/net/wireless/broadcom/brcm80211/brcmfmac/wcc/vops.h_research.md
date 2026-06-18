# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/vops.h

Purpose: declares the WCC firmware-vendor operations object for WCC plugin source files and consumers.

Important APIs and types: `extern const struct brcmf_fwvid_ops brcmf_wcc_ops;` is the single exported symbol declaration. `WCC_VOPS` is a convenience macro expanding to `&brcmf_wcc_ops`.

Control flow: no executable flow. It connects `core.c` implementation to `module.c` registration.

State and persistence: no state.

Dependencies and integration: depends on `struct brcmf_fwvid_ops` being visible to includers through their own includes. It is local plugin glue, not a public userspace interface.

Risks and test signals: mismatched declarations or missing include guards would cause build failures. Test by building the WCC module and checking that `module.c` links against `brcmf_wcc_ops`.
