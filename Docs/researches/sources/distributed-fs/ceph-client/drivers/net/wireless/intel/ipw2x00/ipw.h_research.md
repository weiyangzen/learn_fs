# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw.h

Purpose: Provides a small shared header for Intel ipw2100/ipw2200 cfg80211 cipher-suite advertisement.

Important APIs/types: Includes Linux IEEE80211 definitions and defines `static const u32 ipw_cipher_suites[]` containing WEP40, WEP104, TKIP, and CCMP cipher suite IDs.

Control flow and state: No executable flow. The static const array gives each including translation unit its own internal-linkage copy, avoiding exported global storage.

Dependencies and integration: Consumed by ipw2x00 driver code that registers supported cipher suites with cfg80211/wiphy structures. Risks include per-translation-unit duplication, missing newer cipher suites by design for legacy hardware, and needing array-size calculations at call sites. Test signals include wiphy registration, scan/connect security capability reporting, WEP/TKIP/CCMP association tests, and compile checks for include consumers.
