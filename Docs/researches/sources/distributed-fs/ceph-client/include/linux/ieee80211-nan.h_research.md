# sources/distributed-fs/ceph-client/include/linux/ieee80211-nan.h

## Purpose
Defines Wi-Fi Aware NAN operation-mode and device-capability bits, NAN attribute headers, master indication, anchor master information, and an attribute iteration macro.

## Important APIs, Types, And Functions
Constants describe VHT/HE PHY modes, 80+80/160 MHz support, PNDL support, TX/RX antenna count masks, device capability flags, and NAN attribute IDs. Packed types are `ieee80211_nan_attr`, `ieee80211_nan_master_indication`, and `ieee80211_nan_anchor_master_info`. `for_each_nan_attr()` safely walks variable-length NAN attributes using the 16-bit little-endian length field.

## Control Flow
NAN frame parsers iterate attributes from a data pointer and total length. The iterator checks that both the attribute header and declared payload fit before advancing to the next attribute.

## State And Persistence
No mutable state is owned here. NAN cluster/master election, discovery state, and parsed attributes are maintained by cfg80211/mac80211 or driver NAN logic.

## Dependencies And Integration Points
Uses Linux types, endian annotations, packed layout, and Ethernet address length. Integrates with Wi-Fi Aware discovery, NAN cluster information parsing, and vendor/driver management-frame handling.

## Risks
Attribute iteration depends on correct total length and little-endian conversion. Misspelled `NAN_OP_MODE_PNDL_SUPPRTED` is API surface and should not be casually renamed. Callers must still validate attribute-specific payload sizes after iteration.

## Test Signals
NAN attribute fuzzing, zero-length and truncated attributes, master indication parsing, anchor master rank/address union interpretation, antenna mask extraction, and operation-mode capability parsing.
