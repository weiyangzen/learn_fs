# sources/distributed-fs/ceph-client/include/linux/linkmode.h

Purpose: provides bitmap helpers for ethtool link-mode masks.

Important APIs and types: inline wrappers zero, fill, copy, and/or, andnot, test emptiness/equality/intersection/subset, set/clear/modify bits, and set arrays of link-mode bits using `__ETHTOOL_LINK_MODE_MASK_NBITS`. `linkmode_resolve_pause()` computes negotiated pause behavior from local and partner advertisements; `linkmode_set_pause()` updates advertisement pause bits.

Control flow: network drivers and phylink/ethtool code manipulate advertised/supported link-mode bitmaps through these wrappers to avoid hard-coded bitmap sizes.

State and persistence: no state is stored; callers own the bitmap arrays.

Dependencies and integration points: depends on bitmap and ethtool UAPI constants. Integrates NIC/PHY drivers with ethtool link-mode negotiation.

Risks and test signals: risks include using raw bitmap sizes, out-of-range bit arrays, and pause negotiation mistakes. Test ethtool advertise/supported masks, pause resolution combinations, subset/intersection behavior, and future link-mode count changes.
