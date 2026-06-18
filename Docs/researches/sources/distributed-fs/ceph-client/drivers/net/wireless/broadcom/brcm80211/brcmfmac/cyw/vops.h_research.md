# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/vops.h

Purpose: Exposes the CYW vendor operations object to module registration code.

Important APIs/types/functions: Declares `extern const struct brcmf_fwvid_ops brcmf_cyw_ops` and `CYW_VOPS` as a pointer macro.

Control flow: `module.c` includes this and passes the ops pointer to the fwvid registry.

State and persistence behavior: Declaration only; no state.

Dependencies and integration points: Requires `struct brcmf_fwvid_ops` from fwvid headers in includers.

Risks: Missing definition is caught at link/modpost time.

Test signals: `brcmfmac-cyw` links and registers expected ops.
