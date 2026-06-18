# sources/distributed-fs/ceph-client/net/mac80211/uhr.c

## Purpose

`uhr.c` contains mac80211 helper logic for Ultra High Reliability capability propagation. Its only function, `ieee80211_uhr_cap_ie_to_sta_uhr_cap()`, translates a parsed UHR capability information element into the per-link station capability cache stored in `link_sta->pub->uhr_cap`.

The file is narrowly scoped: it does not parse the IE from raw bytes, validate element length, negotiate UHR operation, or emit capabilities. It assumes callers have already parsed and size-checked the UHR capability element and supplies the local interface, supported band, received capability pointer, received length, and target link station.

## Important APIs, Types, and Functions

The exported internal API is:

`ieee80211_uhr_cap_ie_to_sta_uhr_cap(struct ieee80211_sub_if_data *sdata, struct ieee80211_supported_band *sband, const struct ieee80211_uhr_cap *uhr_cap, u8 uhr_cap_len, struct link_sta_info *link_sta)`.

The target state is `struct ieee80211_sta_uhr_cap`, reached through `link_sta->pub->uhr_cap`. The copied source fields are `struct ieee80211_uhr_cap_mac mac` and `struct ieee80211_uhr_cap_phy phy`. Local capability gating uses `ieee80211_get_uhr_iftype_cap_vif(sband, &sdata->vif)`, which checks whether the supported band advertises UHR capability for the current virtual interface type. PHY field extraction uses `ieee80211_uhr_phy_cap(uhr_cap, from_ap)`, which accounts for the variable placement of PHY capability data when AP-originated UHR capabilities include optional DBE MCS map fields.

The function is declared in `ieee80211_i.h` and is called from at least MLME association handling and cfg80211 station-add/change paths when UHR capability attributes are present.

## Control Flow

The function first clears the stored station UHR capability with `memset()`. This makes absence of local support or early return explicit by leaving `has_uhr` false and zeroing old MAC/PHY data.

It then checks local support for UHR on the given band and vif type. If the local hardware/interface combination does not advertise UHR capability, the function returns without storing peer UHR data, even if the peer supplied a UHR capability IE.

When local support exists, it marks `sta_uhr_cap->has_uhr = true`, copies the fixed MAC capability block from `uhr_cap->mac`, determines whether the element came from an AP by checking `sdata->vif.type == NL80211_IFTYPE_STATION`, and copies the PHY capability block returned by `ieee80211_uhr_phy_cap(uhr_cap, from_ap)`.

## State and Persistence Behavior

The only persistent mutation is the station/link public UHR capability cache. It is overwritten on every call and intentionally reset before capability gating. This means UHR support can be removed cleanly when a later station update lacks valid local compatibility or when caller-provided capability data is no longer usable.

There is no allocation, reference counting, locking, or global state in this file. Correct synchronization is delegated to callers that own `link_sta_info` updates. The unused `uhr_cap_len` parameter documents the intended relationship to parsed IE length, but this helper itself does not inspect it.

## Dependencies and Integration Points

The helper depends on definitions from `ieee80211_i.h`, cfg80211/mac80211 capability structures, and UHR inline helpers from the IEEE 802.11 UHR header. Its inputs are populated by parse/configuration paths such as mac80211 element parsing and nl80211 station parameters. Its output is consumed anywhere station capabilities are queried, including rate/capability negotiation, station reporting, and driver-facing station state.

It complements `ieee80211_put_uhr_cap()` in `util.c`, which emits local UHR capabilities into management frames, and nl80211 validation paths that check `NL80211_ATTR_UHR_CAPABILITY` sizes before mac80211 receives the parsed pointer.

## Risks

The main risk is relying on callers to validate `uhr_cap_len`. `ieee80211_uhr_phy_cap()` can compute a variable offset based on AP DBE support bits, so a malformed or undersized IE would be dangerous if it reached this helper without earlier `ieee80211_uhr_capa_size_ok()` validation. The local-support gate prevents exposing peer UHR support when the local iftype does not support UHR, but it also means callers must pass the correct `sband` and `sdata` for the link being updated.

Because the function clears the cached capability before checking local support, accidental calls with the wrong band or vif can erase previously stored UHR state. The `from_ap` heuristic depends on station mode being the only path where the peer capability comes from an AP; new interface types or UHR exchange paths should revisit that assumption.

## Test Signals

Useful tests include station association with a valid AP UHR capability IE, AP/cfg80211 station insertion with UHR capability attributes, local iftype without UHR support producing `has_uhr == false`, DBE-present AP capability layouts exercising `ieee80211_uhr_phy_cap()` offsets, malformed UHR capability attributes being rejected before this helper, and repeated updates confirming stale UHR fields are cleared when support is absent.
