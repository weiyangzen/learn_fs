## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.c

### Purpose
`qlink_util.c` converts between QLINK protocol values and Linux cfg80211/nl80211/mac80211 representations. It is the small translation layer that keeps command builders and parsers from open-coding enum, flag, channel, ACL, and regulatory conversions.

### Important APIs, Types, And Functions
Public helpers include `qlink_iface_type_to_nl_mask()`, `qlink_chan_width_mask_to_nl()`, `qlink_chandef_q2cfg()`, `qlink_chandef_cfg2q()`, `qlink_hidden_ssid_nl2q()`, `qtnf_utils_is_bit_set()`, `qlink_acl_data_cfg2q()`, `qlink_utils_band_cfg2q()`, `qlink_utils_dfs_state_cfg2q()`, `qlink_utils_chflags_cfg2q()`, and `qlink_utils_regrule_q2nl()`. Private helpers map individual channel widths and regulatory flags.

### Control Flow
Most functions are switch or bitmask translations. Channel conversion looks up `struct ieee80211_channel` by center frequency for firmware-to-cfg80211 and copies channel fields back for cfg80211-to-firmware. ACL conversion maps cfg80211 policy values then copies the MAC-address array. Regulatory parsing expands QLINK rule flags into nl80211 rule flags and copies frequency/power/CAC values after endian conversion.

### State, Persistence, And Dependencies
The file has no retained state. It depends on `qlink.h`, cfg80211/nl80211 enums, `ieee80211_get_channel()`, endian helpers, and caller-provided destination buffers. Persistence is only the transformed command/response content written elsewhere.

### Integration Points
Command construction for scans, AP setup, channel switches, regulatory notifications, and ACLs uses these helpers. Response/event parsers use them to present firmware channel definitions and regulatory rules to cfg80211.

### Risks
Unknown widths return `(u8)-1` or invalid enum values and depend on callers catching invalid chandefs. `qlink_acl_data_cfg2q()` assumes the destination has enough trailing space for all entries. Flag conversions are intentionally partial; unsupported future flags will be silently dropped unless expanded.

### Test Signals
Tests should cover every enum mapping, invalid width handling, channel lookups that return `NULL`, ACL array sizing, bit-test bounds, regulatory flags including DFS/no-IR/HT/VHT restrictions, and endian-correct round trips.
