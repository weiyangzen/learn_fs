# sources/distributed-fs/ceph-client/net/mac80211/parse.c

Purpose: parses 802.11 management information elements into `struct ieee802_11_elems`, including legacy, HT/VHT/HE/EHT/UHR, mesh, CSA, MBSSID, and multi-link overlays.

Important APIs and functions: `ieee802_11_parse_elems_full()` allocates a flexible parse object, prepares MBSSID or MLO profile parsing, parses outer elements, overlays non-transmitted BSS or per-STA profile elements, defragments reconfiguration/EPCS MLEs, and returns the embedded `ieee802_11_elems`. `_ieee802_11_parse_elems_full()` is the central IE loop. `ieee80211_parse_extension_element()` handles extension IDs for HE/EHT/UHR and MLO markers. `ieee80211_parse_tpe()` parses transmit power envelope variants. `ieee802_11_find_bssid_profile()`, `ieee80211_prep_mle_link_parse()`, and `ieee80211_mle_get_sta_prof()` support MBSSID/MLO profile overlay. `ieee80211_parse_bitrates()` maps supported-rate IE bytes to band bitrate masks.

Control flow: the parser initializes scratch space at three times input length, records original IE pointers, optionally builds a merged non-transmitted profile or defragmented MLO basic element, parses the outer IE stream with duplicate and size checks, then parses inherited inner/profile elements as overrides.

State and persistence: parse results are heap allocated with scratch storage embedded after the result object; callers own and free the returned pointer. Most element pointers refer either to the original frame buffer or scratch defragmentation/profile storage. CRC state is accumulated only for requested filtered elements.

Dependencies and integration points: depends on cfg80211 element iterators, element validation helpers, CRC32, KUnit export visibility, mesh/rate/wme/mac80211 headers, and wireless frame constants. Consumers throughout mac80211 rely on parse flags and pointer lifetimes.

Risks: pointer lifetime is tied to the returned allocation and original frame buffer; callers must not keep pointers after freeing or after skb lifetime ends. Duplicate-element handling is selective and must match standards expectations. MLO and MBSSID overlay paths share scratch space, so bounds and non-inheritance checks are critical.

Test signals: malformed/truncated IE endings, duplicate singleton IEs, extension element size validation, MBSSID profile matching and DTIM override, MLE defragmentation and per-link profile parsing, TPE count/category variants, and bitrate mask translation.
