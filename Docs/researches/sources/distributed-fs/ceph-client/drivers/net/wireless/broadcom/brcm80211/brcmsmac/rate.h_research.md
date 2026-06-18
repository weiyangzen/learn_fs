# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.h

Purpose: Declares brcmsmac rate tables, MCS metadata, ratespec bit layout, rate classification helpers, and rateset manipulation APIs.

Important APIs/types: `struct brcms_mcs_info` stores 20/40 MHz rates, SGI rates, PHY control byte 3, and equivalent legacy OFDM rate. Inline helpers decode MCS stream count, MCS rate, rspec active state, bandwidth, short GI, 40 MHz status, PLCP byte fields, STC/STF, MCS/OFDM/CCK classification, and PLCP-to-MAC rate conversion. Declares default ratesets and manipulation functions implemented in `rate.c`.

Control flow and state: Header-only control flow is limited to inline bit extraction and table lookups. It encodes the persistent ratespec format used through TX/RX paths, with rate/MCS in low bits and mode/bandwidth/coding/override flags in high bits.

Dependencies and integration: Includes `types.h`, `d11.h`, and `phy_hal.h`; depends on `mcs_table`, `rate_info`, D11 PHY TX control encodings, and PHY-provided OFDM lookup. Risks include unchecked MCS/rate indexes in inline helpers, hard-coded bit layouts shared with firmware/hardware, and classification relying on `rate_info`. Test signals include compile users, KUnit-style bitfield checks, PLCP decode, SGI/40 MHz rate math, and TX header generation.
