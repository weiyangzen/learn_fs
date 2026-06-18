# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.c

Purpose: Implements brcmsmac legacy and HT rate tables plus rateset filtering, default selection, MCS maintenance, and RX PLCP-to-ratespec decoding.

Important APIs: Exports `rate_info`, `mcs_table`, default legacy/MIMO ratesets, `brcms_c_rate_hwrs_filter_sort_validate()`, `brcms_c_compute_rspec()`, `brcms_c_rateset_copy()`, `brcms_c_rateset_filter()`, `brcms_c_rateset_default()`, `brcms_c_rate_legacy_phyctl()`, and MCS clear/build/update/bandwidth filters. `legacy_phycfg_table` maps CCK/OFDM rates to PHY control byte 3 values.

Control flow and state: Most behavior is table driven. Filtering first records valid requested legacy rates, rebuilds them in hardware-supported order while preserving the basic bit, intersects MCS maps, and validates count/basic-rate requirements. Default selection chooses a rateset from PHY type, band, bandwidth, CCK-only, MCS permission, and TX stream count. RX computation branches by PHY type and frame type, decodes CCK/OFDM/MIMO PLCP, marks 40 MHz and short GI.

Dependencies and integration: Uses `brcmu_wifi.h`, bit helpers from `brcmu_utils.h`, D11 RX/PLCP definitions, and `pub.h` rate/PHY constants. Risks include caller-provided rate array bounds, MCS index assumptions, unsupported PHY/frame types silently returning default-ish rspecs, and the need to keep rate tables synchronized with firmware/D11 definitions. Test signals include rateset negotiation, basic-rate validation, 20/40 MHz MCS32 toggling, RX status decode, and interoperability across 2.4/5 GHz bands.
