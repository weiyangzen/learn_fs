# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/vops.h

## Purpose
Declares the BCA vendor-ops object and a convenience macro for brcmfmac vendor integration.

## Important APIs, Types, and Functions
Exposes `extern const struct brcmf_fwvid_ops brcmf_bca_ops;` and defines `BCA_VOPS` as `(&brcmf_bca_ops)`.

## Control Flow, State, and Persistence
No control flow or state. The referenced object is defined in `core.c`.

## Dependencies and Integration Points
Included by BCA core/module files and by built-in vendor linking code that needs a vendor ops pointer.

## Risks and Test Signals
Risks are declaration drift or missing include guards. Build BCA plugin and built-in vendor configurations.
