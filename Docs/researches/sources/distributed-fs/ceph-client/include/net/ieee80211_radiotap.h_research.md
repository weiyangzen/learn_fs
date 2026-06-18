# sources/distributed-fs/ceph-client/include/net/ieee80211_radiotap.h

Purpose: defines the radiotap metadata ABI used by 802.11 monitor-mode frames. It enumerates presence bits and field encodings for legacy, HT/VHT/HE/EHT, timestamp, AMPDU, LSIG, vendor namespaces, TLVs, and zero-length PSDU metadata.

Important APIs/types: `struct ieee80211_radiotap_header` contains version, pad, length, and present bitmaps. Numerous enums define `ieee80211_radiotap_presence`, flags, channel flags, RX/TX flags, MCS/VHT/HE/HE-MU/EHT fields, timestamp units/flags, LSIG fields, and vendor/TLV structures. `ieee80211_get_radiotap_len()` reads the little-endian `it_len` from raw data.

Control flow and state: this header is ABI/layout definition only. Producers build a radiotap header with present bits and aligned fields; consumers parse based on presence bitmaps and total length. There is no persistent kernel state here.

Dependencies and integration: depends on kernel unaligned helpers and fixed types. It integrates with mac80211, cfg80211, monitor interfaces, packet capture tools, and userspace sniffers.

Risks: radiotap is user-visible ABI; enum values and field layouts must not drift. Variable presence bitmaps and vendor/TLV fields need strict bounds and alignment handling. Tests should parse/build representative legacy, VHT, HE, HE-MU, EHT, vendor, and TLV headers, verify little-endian length reads, and fuzz truncated/misaligned headers.
