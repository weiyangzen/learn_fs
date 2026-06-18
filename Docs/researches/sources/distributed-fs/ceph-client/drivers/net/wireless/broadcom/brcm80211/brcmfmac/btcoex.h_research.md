# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.h

## Purpose
Declares brcmfmac Bluetooth coexistence modes and attach/detach/control APIs.

## Important APIs, Types, and Functions
Defines `enum brcmf_btcoex_mode` with `BRCMF_BTCOEX_DISABLED` and `BRCMF_BTCOEX_ENABLED`. Exposes `brcmf_btcoex_attach()`, `brcmf_btcoex_detach()`, and `brcmf_btcoex_set_mode()`.

## Control Flow, State, and Persistence
No state in the header. Runtime state is `struct brcmf_btcoex_info` private to `btcoex.c` and referenced through cfg80211 private data.

## Dependencies and Integration Points
Used by brcmfmac cfg80211/P2P code to initialize coexistence and wrap critical protocol windows.

## Risks and Test Signals
Risks are enum semantic mismatch and prototype drift. Test build coverage and runtime DHCP critical-protocol calls with and without Bluetooth activity.
