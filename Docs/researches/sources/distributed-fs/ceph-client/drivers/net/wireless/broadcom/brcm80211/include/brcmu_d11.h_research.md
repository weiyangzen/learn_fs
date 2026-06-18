# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_d11.h

Purpose: Defines Broadcom D11N/D11AC chanspec bit layouts and the generic channel conversion interface used by `brcmutil/d11.c`.

Important APIs/types: Defines IO type constants, channel masks/shifts, D11N sideband/bandwidth/band fields, D11AC sideband/bandwidth/band fields, generic band constants, `enum brcmu_chan_bw`, `enum brcmu_chan_sb`, `struct brcmu_chan`, `struct brcmu_d11inf`, and `brcmu_d11_attach()`.

Control flow and state: No executable flow. `struct brcmu_d11inf` stores selected encode/decode function pointers, while `struct brcmu_chan` stores mutable channel conversion state: raw `chspec`, center channel, control channel, band, bandwidth, and sideband.

Dependencies and integration: Consumed by brcmutil and Broadcom drivers needing firmware chanspec conversion. Risks include fixed bit layouts tied to firmware ABI, unsupported width values such as 80+80 needing explicit handling, sideband aliases sharing enum values, and callers using callbacks before `brcmu_d11_attach()`. Test signals include conversion callback initialization, compile checks for all enum values, and D11N/D11AC round-trip channel tests.
